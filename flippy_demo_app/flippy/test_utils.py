from mockito import mock
from django.http import HttpRequest


def request_factory(ip="10.1.2.3", user=None):
    if user is None:
        # user = AnonymomusUser() - would be better, but requires Django setup
        user = anonymous_user_factory()
    spec = {"META": {}, "user": user}
    if ip:
        spec["META"]["REMOTE_ADDR"] = ip
    return mock(spec, HttpRequest)


def user_factory(pk):
    spec = {"pk": pk, "is_authenticated": True, "is_anonymous": False}
    return mock(spec, strict=True)


def anonymous_user_factory():
    spec = {"is_authenticated": False, "is_anonymous": True}
    return mock(spec, strict=True)

