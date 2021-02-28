"""Utilities and extensions for django_auth_ldap."""

from django.core.exceptions import PermissionDenied

from django_auth_ldap.backend import LDAPBackend as _LDAPBackend


class LDAPBackend(_LDAPBackend):
    default_settings = {"SET_USABLE_PASSWORD": False}

    def authenticate_ldap_user(self, ldap_user, password):
        """Authenticate user against LDAP and set local password if successful.

        Having a local password is needed to make changing passwords easier. In
        order to catch password changes in a universal way and forward them to
        backends (like LDAP, in this case), getting the old password first is
        necessary to authenticate as that user to LDAP.

        We buy the small insecurity of having a hash of the password in the
        Django database in order to not require it to have global admin permissions
        on the LDAP directory.
        """
        user = ldap_user.authenticate(password)

        if not user:
            # Fail early and do not try other backends
            raise PermissionDenied("LDAP failed to authenticate user")

        if self.settings.SET_USABLE_PASSWORD:
            # Set a usable password so users can change their LDAP password
            user.set_password(password)
            user.save()

        return user
