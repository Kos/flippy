from .subject import IpAddressSubject, UserSubject, SubjectIdentifier
from mockito import mock
from django.http import HttpRequest
import pytest


def test_subject_identifier():
    identifier = SubjectIdentifier(subject_class="hello", subject_id="123")
    assert identifier.subject_class == "hello"
    assert identifier.subject_id == "123"


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


@pytest.mark.parametrize(
    ["ip", "expected_identifier"],
    [
        (
            "10.20.30.40",
            SubjectIdentifier("flippy.subject.IpAddressSubject", "10.20.30.40"),
        ),
        (
            "40.30.20.10",
            SubjectIdentifier("flippy.subject.IpAddressSubject", "40.30.20.10"),
        ),
        (None, None),
    ],
)
def test_ip_address_subject(ip, expected_identifier):
    assert (
        IpAddressSubject().get_subject_identifier_for_request(request_factory(ip=ip))
        == expected_identifier
    )


@pytest.mark.parametrize(
    ["user", "expected_identifier"],
    [
        (user_factory(pk=42), SubjectIdentifier("flippy.subject.UserSubject", "42")),
        (user_factory(pk=25), SubjectIdentifier("flippy.subject.UserSubject", "25")),
        (None, None),
    ],
)
def test_user_subject(user, expected_identifier):
    assert (
        UserSubject().get_subject_identifier_for_request(request_factory(user=user))
        == expected_identifier
    )
