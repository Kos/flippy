from .subject import IpAddressSubject, SubjectIdentifier
from mockito import mock
from django.http import HttpRequest
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
        IpAddressSubject().get_subject_identifier_for_request(request(ip))
        == expected_identifier
    )


def request(ip="10.1.2.3"):
    spec = {"META": {}}
    if ip:
        spec["META"]["REMOTE_ADDR"] = ip
    return mock(spec, HttpRequest)

