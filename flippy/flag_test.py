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


@pytest.mark.parametrize(
    "percentage,result", [(0, False), (10, False), (20, True), (100, True)]
)
def test_flag_uses_rollout(percentage, result):
    f = Flag("hello")
    Rollout.objects.create(
        flag_name=f.name,
        enable_percentage=percentage,
        subject="flippy.subject.IpAddressSubject",
    )
    assert f.get_state_for_request(request_factory()) is result


def test_flag_uses_correct_rollout():
    f = Flag("hello")
    Rollout.objects.create(
        flag_name="hello2",
        enable_percentage=100,
        subject="flippy.subject.IpAddressSubject",
    )
    assert f.get_state_for_request(request_factory()) is False


def test_flag_respects_null_identifier():
    f = Flag("hello")
    Rollout.objects.create(
        flag_name=f.name, enable_percentage=100, subject="flippy.subject.UserSubject"
    )
    assert f.get_state_for_request(request_factory()) is False


def test_zero_rollout_overrides_default():
    f = Flag("hello", default=True)
    Rollout.objects.create(
        flag_name=f.name, enable_percentage=0, subject="flippy.subject.IpAddressSubject"
    )
    assert f.get_state_for_request(request_factory()) is False


def test_zero_rollout_doesnt_override_default_with_null_identifier():
    f = Flag("hello", default=True)
    Rollout.objects.create(
        flag_name=f.name, enable_percentage=0, subject="flippy.subject.UserSubject"
    )
    assert f.get_state_for_request(request_factory()) is True


def test_flag_uses_latest_rollout():
    f = Flag("hello", default=True)
    Rollout.objects.create(
        flag_name=f.name,
        enable_percentage=100,
        subject="flippy.subject.IpAddressSubject",
    )
    Rollout.objects.create(
        flag_name=f.name, enable_percentage=0, subject="flippy.subject.IpAddressSubject"
    )
    assert f.get_state_for_request(request_factory()) is False
