from typing import Any, List, Optional, Sequence, Tuple

import django.apps
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_migrate, pre_migrate
from django.http import HttpRequest

import pkg_resources
from dynamic_preferences.signals import preference_updated
from license_expression import Licensing
from spdx_license_list import LICENSES

from .core_helpers import copyright_years


class AppConfig(django.apps.AppConfig):
    """An extended version of DJango's AppConfig container."""

    def ready(self):
        super().ready()

        # Register default listeners
        pre_migrate.connect(self.pre_migrate, sender=self)
        post_migrate.connect(self.post_migrate, sender=self)
        preference_updated.connect(self.preference_updated)
        user_logged_in.connect(self.user_logged_in)
        user_logged_out.connect(self.user_logged_out)

        # Getting an app ready means it should look at its config once
        self.preference_updated(self)

    def get_distribution_name(self):
        """Get pkg_resources distribution name of application package."""
        if hasattr(self, "dist_name"):
            return self.dist_name
        elif self.name.lower().startswith("aleksis.apps."):
            return self.name.lower().replace("aleksis.apps.", "AlekSIS-App-")

        return None

    def get_distribution(self):
        """Get pkg_resources distribution of application package."""
        dist_name = self.get_distribution_name()
        if dist_name:
            try:
                dist = pkg_resources.get_distribution(dist_name)
            except pkg_resources.DistributionNotFound:
                return None

            return dist

    def get_name(self):
        """Get name of application package."""
        if hasattr(self, "verbose_name"):
            return self.verbose_name
        else:
            dist_name = self.get_distribution_name()
            if dist_name:
                return dist_name
            return self.name

    def get_version(self):
        """Get version of application package."""
        if hasattr(self, "version"):
            return self.version
        else:
            dist = self.get_distribution()
            if dist:
                return dist.version
            else:
                return "unknown"

    @classmethod
    def get_licence(cls) -> Tuple:
        """Get tuple of licence information of application package."""
        # Get string representation of licence in SPDX format
        licence = getattr(cls, "licence", None)

        default_dict = {
            "isDeprecatedLicenseId": False,
            "isFsfLibre": False,
            "isOsiApproved": False,
            "licenseId": "unknown",
            "name": "Unknown Licence",
            "referenceNumber": -1,
            "url": "",
        }
        if licence:
            # Parse licence string into object format
            licensing = Licensing(LICENSES.keys())
            parsed = licensing.parse(licence).simplify()
            readable = parsed.render_as_readable()

            # Collect flags about licence combination (drop to False if any licence is False)
            flags = {
                "isFsfLibre": True,
                "isOsiApproved": True,
            }

            # Fill information dictionaries with missing data
            licence_dicts = []
            for symbol in parsed.symbols:
                # Get licence base information, stripping the "or later" mark
                licence_dict = LICENSES.get(symbol.key.rstrip("+"), None)

                if licence_dict is None:
                    # Fall back to the default dict
                    licence_dict = default_dict
                else:
                    # Add missing licence link to SPDX data
                    licence_id = licence_dict["licenseId"]
                    licence_dict["url"] = f"https://spdx.org/licenses/{licence_id}.html"

                # Drop summed up flags to False if this licence is False
                flags["isFsfLibre"] = flags["isFsfLibre"] and licence_dict["isFsfLibre"]
                flags["isOsiApproved"] = flags["isOsiApproved"] and licence_dict["isOsiApproved"]

                licence_dicts.append(licence_dict)

            return (readable, flags, licence_dicts)
        else:
            # We could not find a valid licence
            return ("Unknown", [default_dict])

    @classmethod
    def get_urls(cls):
        """Get list of URLs for this application package."""
        return getattr(cls, "urls", {})
        # TODO Try getting from distribution if not set

    @classmethod
    def get_copyright(cls) -> Sequence[Tuple[str, str, str]]:
        """Get copyright information tuples for application package."""
        copyrights = getattr(cls, "copyright_info", tuple())

        copyrights_processed = []
        for copyright_info in copyrights:
            copyrights_processed.append(
                (
                    # Sort copyright years and combine year ranges for display
                    copyright_info[0]
                    if isinstance(copyright_info[0], str)
                    else copyright_years(copyright_info[0]),
                    copyright_info[1],
                    copyright_info[2],
                )
            )

        return copyrights_processed
        # TODO Try getting from distribution if not set

    def preference_updated(
        self,
        sender: Any,
        section: Optional[str] = None,
        name: Optional[str] = None,
        old_value: Optional[Any] = None,
        new_value: Optional[Any] = None,
        **kwargs,
    ) -> None:
        """Call on every app instance if a dynamic preference changes, and once on startup.

        By default, it does nothing.
        """
        pass

    def pre_migrate(
        self,
        app_config: django.apps.AppConfig,
        verbosity: int,
        interactive: bool,
        using: str,
        plan: List[Tuple],
        apps: django.apps.registry.Apps,
        **kwargs,
    ) -> None:
        """Call on every app instance before its models are migrated.

        By default, it does nothing.
        """
        pass

    def post_migrate(
        self,
        app_config: django.apps.AppConfig,
        verbosity: int,
        interactive: bool,
        using: str,
        plan: List[Tuple],
        apps: django.apps.registry.Apps,
        **kwargs,
    ) -> None:
        """Call on every app instance after its models have been migrated.

        By default, asks all models to do maintenance on their default data.
        """
        self._maintain_default_data()

    def user_logged_in(
        self, sender: type, request: Optional[HttpRequest], user: "User", **kwargs
    ) -> None:
        """Call after a user logged in.

        By default, it does nothing.
        """
        pass

    def user_logged_out(
        self, sender: type, request: Optional[HttpRequest], user: "User", **kwargs
    ) -> None:
        """Call after a user logged out.

        By default, it does nothing.
        """
        pass

    def _maintain_default_data(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        if not self.models_module:
            # This app does not have any models, so bail out early
            return

        for model in self.get_models():
            if hasattr(model, "maintain_default_data"):
                # Method implemented by each model object; can be left out
                model.maintain_default_data()
            if hasattr(model, "extra_permissions"):
                ct = ContentType.objects.get_for_model(model)
                for perm, verbose_name in model.extra_permissions:
                    Permission.objects.get_or_create(
                        codename=perm, content_type=ct, defaults={"name": verbose_name},
                    )
