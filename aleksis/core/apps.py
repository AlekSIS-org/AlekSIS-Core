from typing import Any, List, Optional, Tuple

import django.apps
from django.apps import apps
from django.http import HttpRequest
from django.utils.module_loading import autodiscover_modules

from dynamic_preferences.registries import preference_models
from health_check.plugins import plugin_dir

from .registries import (
    group_preferences_registry,
    person_preferences_registry,
    site_preferences_registry,
)
from .util.apps import AppConfig
from .util.core_helpers import has_person
from .util.sass_helpers import clean_scss


class CoreConfig(AppConfig):
    name = "aleksis.core"
    verbose_name = "AlekSIS — The Free School Information System"
    dist_name = "AlekSIS-Core"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/official/AlekSIS/",
    }
    licence = "EUPL-1.2+"
    copyright_info = (
        ([2017, 2018, 2019, 2020], "Jonathan Weth", "wethjo@katharineum.de"),
        ([2017, 2018, 2019], "Frank Poetzsch-Heffter", "p-h@katharineum.de"),
        ([2018, 2019, 2020], "Julian Leucker", "leuckeju@katharineum.de"),
        ([2018, 2019, 2020], "Hangzhi Yu", "yuha@katharineum.de"),
        ([2019, 2020], "Dominik George", "dominik.george@teckids.org"),
        ([2019, 2020], "Tom Teichler", "tom.teichler@teckids.org"),
        ([2019], "mirabilos", "thorsten.glaser@teckids.org"),
    )

    def ready(self):
        super().ready()

        # Autodiscover various modules defined by AlekSIS
        autodiscover_modules("form_extensions", "model_extensions", "checks")

        sitepreferencemodel = self.get_model("SitePreferenceModel")
        personpreferencemodel = self.get_model("PersonPreferenceModel")
        grouppreferencemodel = self.get_model("GroupPreferenceModel")

        preference_models.register(sitepreferencemodel, site_preferences_registry)
        preference_models.register(personpreferencemodel, person_preferences_registry)
        preference_models.register(grouppreferencemodel, group_preferences_registry)

        self._load_data_checks()

        from .health_checks import DataChecksHealthCheckBackend

        plugin_dir.register(DataChecksHealthCheckBackend)

    @classmethod
    def _load_data_checks(cls):
        """Get all data checks from all loaded models."""
        from aleksis.core.data_checks import DataCheckRegistry

        data_checks = []
        for model in apps.get_models():
            data_checks += getattr(model, "data_checks", [])
        DataCheckRegistry.data_checks = data_checks

    def preference_updated(
        self,
        sender: Any,
        section: Optional[str] = None,
        name: Optional[str] = None,
        old_value: Optional[Any] = None,
        new_value: Optional[Any] = None,
        **kwargs,
    ) -> None:
        if section == "theme":
            if name in ("primary", "secondary"):
                clean_scss()
            elif name in ("favicon", "pwa_icon"):
                from favicon.models import Favicon  # noqa

                is_favicon = name == "favicon"

                if new_value:
                    Favicon.on_site.update_or_create(
                        title=name,
                        defaults={"isFavicon": name == "favicon", "faviconImage": new_value,},
                    )
                else:
                    Favicon.on_site.filter(title=name, isFavicon=is_favicon).delete()

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
        super().post_migrate(app_config, verbosity, interactive, using, plan, apps)

        # Ensure presence of an OTP YubiKey default config
        apps.get_model("otp_yubikey", "ValidationService").objects.using(using).update_or_create(
            name="default", defaults={"use_ssl": True, "param_sl": "", "param_timeout": ""}
        )

    def user_logged_in(
        self, sender: type, request: Optional[HttpRequest], user: "User", **kwargs
    ) -> None:
        if has_person(user):
            # Save the associated person to pick up defaults
            user.person.save()
