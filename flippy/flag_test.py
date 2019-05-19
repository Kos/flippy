import pytest
from django.contrib.auth.models import User, AbstractUser
from django.http import HttpRequest
from pytest import raises

from flippy.subject import IpAddressSubject, UserSubject
from .flag import Flag, TypedFlag
from .models import Rollout
from .test_utils import request_factory

pytestmark = pytest.mark.django_db


def test_flag_has_name():
    f = Flag("hello")
    assert f.id == "hello"


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
        flag_id=f.id,
        enable_percentage=percentage,
        subject="flippy.subject.IpAddressSubject",
    )
    assert f.get_state_for_request(request_factory()) is result


def test_flag_ignores_other_rollout():
    f = Flag("hello")
    Rollout.objects.create(
        flag_id="hello2",
        enable_percentage=100,
        subject="flippy.subject.IpAddressSubject",
    )
    assert f.get_state_for_request(request_factory()) is False


def test_flag_respects_null_identifier():
    f = Flag("hello")
    Rollout.objects.create(
        flag_id=f.id, enable_percentage=100, subject="flippy.subject.UserSubject"
    )
    assert f.get_state_for_request(request_factory()) is False


def test_zero_rollout_overrides_default():
    f = Flag("hello", default=True)
    Rollout.objects.create(
        flag_id=f.id, enable_percentage=0, subject="flippy.subject.IpAddressSubject"
    )
    assert f.get_state_for_request(request_factory()) is False


def test_zero_rollout_doesnt_override_default_with_null_identifier():
    f = Flag("hello", default=True)
    Rollout.objects.create(
        flag_id=f.id, enable_percentage=0, subject="flippy.subject.UserSubject"
    )
    assert f.get_state_for_request(request_factory()) is True


def test_flag_uses_latest_rollout():
    f = Flag("hello", default=True)
    Rollout.objects.create(
        flag_id=f.id, enable_percentage=100, subject="flippy.subject.IpAddressSubject"
    )
    Rollout.objects.create(
        flag_id=f.id, enable_percentage=0, subject="flippy.subject.IpAddressSubject"
    )
    assert f.get_state_for_request(request_factory()) is False


def test_flag_disallows_calling_with_unrelated_type():
    f = Flag("hello")

    with raises(
        TypeError,
        match=r"`Flag\.get_state_for_request\(\)` may only be called with `HttpRequest` instances",
    ):
        f.get_state_for_request("hello")


def test_typed_flag_allows_calling_with_object():
    f: TypedFlag[User] = TypedFlag[User]("hello")
    Rollout.objects.create(flag_id=f.id, subject="flippy.subject.UserSubject")
    user = User()
    assert f.get_state_for_object(user) is True


def test_typed_flag_allows_calling_with_request():
    f = TypedFlag[int]("hello")
    Rollout.objects.create(flag_id=f.id, subject="flippy.subject.IpAddressSubject")
    assert f.get_state_for_request(request_factory())


@pytest.mark.parametrize(
    "flag_type,arg_type",
    [(int, User), (int, str), (User, str), (User, HttpRequest), (int, HttpRequest)],
)
def test_typed_flag_disallows_calling_with_unrelated_type(flag_type, arg_type):
    obj = arg_type()
    f = TypedFlag[flag_type]("hello")

    with raises(
        TypeError,
        match=rf"`TypedFlag\.get_state_for_object\(\)` may only be called with `{flag_type.__name__}` instances",
    ):
        f.get_state_for_object(obj)


def test_flag_accepts_any_subject():
    f = Flag("hello")
    assert f.accepts_subject(IpAddressSubject())
    assert f.accepts_subject(UserSubject())


@pytest.mark.parametrize(
    "flag_type,subject_cls,expected",
    [
        (AbstractUser, UserSubject, True),
        (AbstractUser, IpAddressSubject, False),
        (User, UserSubject, True),
        (User, IpAddressSubject, False),
        (int, UserSubject, False),
        (int, IpAddressSubject, False),
    ],
)
def test_typed_flag_accepts_matching_subjects(flag_type, subject_cls, expected):
    f = TypedFlag[flag_type]("hello")
    assert f.accepts_subject(subject_cls()) is expected
