import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from flippy.flag import TypedFlag
from flippy.models import Rollout


def test_rollout_should_validate_flag_matches_subject(monkeypatch):
    TypedFlag[int]("hejka")
    rollout = Rollout(flag_id="hejka", subject="flippy.subject.UserSubject")
    with pytest.raises(
        ValidationError,
        match="Flag `Hejka` cannot be used with subject `User`. It can only be used with subjects that support `int`.",
    ):
        rollout.full_clean()


def test_rollout_should_validate_flag_matches_subject__ok(monkeypatch):
    TypedFlag[User]("och")
    rollout = Rollout(flag_id="och", subject="flippy.subject.UserSubject")
    rollout.full_clean()


def test_rollout_should_validate_flag_id():
    rollout = Rollout(flag_id="missing_id", subject="flippy.subject.UserSubject")
    with pytest.raises(ValidationError, match="Flag `missing_id` does not exist"):
        rollout.full_clean()


def test_rollout_flag_name_should_work_for_missing_flag():
    rollout = Rollout(flag_id="missing_id", subject="flippy.subject.UserSubject")
    assert "<missing flag: `missing_id`>" == rollout.flag_name
