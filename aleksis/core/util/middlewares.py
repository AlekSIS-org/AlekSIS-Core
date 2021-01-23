from typing import Callable

from django.http import HttpRequest, HttpResponse

from ..models import DummyPerson, Person
from .core_helpers import get_site_preferences, has_person


class EnsurePersonMiddleware:
    """Middleware that ensures that the logged-in user is linked to a person.

    It is needed to inject a dummy person to a superuser that would otherwise
    not have an associated person, in order they can get their account set up
    without external help.

    In addition, if configured in preferences, it auto-creates or links persons
    to regular users if they match.
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not has_person(request) and not request.user.is_anonymous:
            prefs = get_site_preferences()
            if (
                prefs.get("account__auto_link_person", False)
                and request.user.first_name
                and request.user.last_name
            ):
                if prefs.get("account__auto_create_person"):
                    person, created = Person.objects.get_or_create(
                        email=request.user.email,
                        defaults={
                            "first_name": request.user.first_name,
                            "last_name": request.user.last_name,
                        },
                    )
                    person.user = request.user
                else:
                    person = Person.objects.filter(email=request.user.email).first()
                    if person:
                        person.user = request.user
                        person.save()

        if request.user.is_superuser and not has_person(request):
            # Super-users get a dummy person linked
            dummy_person = DummyPerson(
                first_name=request.user.first_name, last_name=request.user.last_name
            )
            request.user.person = dummy_person

        response = self.get_response(request)
        return response
