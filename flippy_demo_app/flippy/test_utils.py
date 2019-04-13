from mockito import mock
from django.http import HttpRequest

from django.contrib.auth.models import User, AnonymousUser


def request_factory(ip="10.1.2.3", user=None):
    if user is None:
        user = AnonymousUser()
    spec = {"META": {}, "user": user}
    if ip:
        spec["META"]["REMOTE_ADDR"] = ip
    return mock(spec, HttpRequest)


def user_factory(pk):
    spec = {"pk": pk, "is_authenticated": True, "is_anonymous": False}
    return mock(spec, User)
