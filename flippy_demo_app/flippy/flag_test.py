from .flag import Flag
from .test_utils import request_factory
from .models import Rollout
import pytest

pytestmark = pytest.mark.django_db


def test_flag_has_name():
    f = Flag("hello")
    assert f.name == "hello"


def test_flag_is_false_by_default():
    f = Flag("hello")
    assert f.get_state_for_request(request_factory()) is False


def test_flag_true_default_value():
    f = Flag("hello", default=True)
    assert f.get_state_for_request(request_factory()) is True


def test_flag_uses_rollout():
    f = Flag("hello")
    assert f.get_state_for_request(request_factory()) is False
    Rollout.objects.create(
        flag_name=f.name,
        enable_percentage=100,
        subject="flippy.subject.IpAddressSubject",
    )
    assert f.get_state_for_request(request_factory()) is True
