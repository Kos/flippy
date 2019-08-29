from mockito import mock
from django.http import HttpRequest

from django.contrib.auth.models import User, AbstractUser, AnonymousUser
from typing import Optional, Any


def request_factory(
    ip: str = "10.1.2.3", user: Optional[AbstractUser] = None
) -> HttpRequest:
    if user is None:
        user = AnonymousUser()
    spec = {"META": {}, "user": user}
    if ip:
        spec["META"]["REMOTE_ADDR"] = ip
    return mock(spec, HttpRequest)


def user_factory(pk: Any) -> User:
    spec = {"pk": pk, "is_authenticated": True, "is_anonymous": False}
    return mock(spec, User)
