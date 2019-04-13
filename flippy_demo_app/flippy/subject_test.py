from .subject import IpAddressSubject, SubjectIdentifier
from mockito import mock
from django.http import HttpRequest
import pytest


def test_subject_identifier():
    identifier = SubjectIdentifier(subject_class="hello", subject_id="123")
    assert identifier.subject_class == "hello"
    assert identifier.subject_id == "123"


def test_ip_address_subject(request):
    assert IpAddressSubject().get_subject_identifier_for_request(
        request
    ) == SubjectIdentifier("flippy.subject.IpAddressSubject", example_ip)


@pytest.fixture
def request():
    spec = {"META": {"REMOTE_ADDR": example_ip}}
    return mock(spec, HttpRequest)


example_ip = "10.1.2.3"
