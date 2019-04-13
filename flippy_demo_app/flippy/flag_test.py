from .flag import Flag
from django.http import HttpRequest
import pytest
from mockito import mock


def test_flag_has_name():
    f = Flag("hello")
    assert f.name == "hello"


def test_flag_is_always_false(request):
    f = Flag("hello")
    assert f.get_state_for_request(request) is False


@pytest.fixture
def request():
    return mock(HttpRequest)
