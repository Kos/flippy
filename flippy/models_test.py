import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from flippy.flag import TypedFlag
from flippy.models import Rollout


def test_rollout_should_validate_flag_matches_subject(monkeypatch):
    TypedFlag[int]("hejka")
    rollout = Rollout(flag_id="hejka", subject="flippy.subject.UserSubject")
    with pytest.raises(ValidationError):
        rollout.full_clean()


def test_rollout_should_validate_flag_matches_subject__ok(monkeypatch):
    TypedFlag[User]("och")
    rollout = Rollout(flag_id="och", subject="flippy.subject.UserSubject")
    rollout.full_clean()
