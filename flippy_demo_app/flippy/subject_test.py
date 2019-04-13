from .subject import IpAddressSubject, UserSubject, SubjectIdentifier
from .test_utils import request_factory, user_factory
import pytest


def test_subject_identifier():
    identifier = SubjectIdentifier(subject_class="hello", subject_id="123")
    assert identifier.subject_class == "hello"
    assert identifier.subject_id == "123"


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
