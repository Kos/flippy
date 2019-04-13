from .subject import Subject, IpAddressSubject, UserSubject, SubjectIdentifier
from .test_utils import request_factory, user_factory
from .exceptions import ConfigurationError
from random import Random
from pathlib import Path
import pytest


def test_subject_identifier():
    identifier = SubjectIdentifier(subject_class="hello", subject_id="123")
    assert identifier.subject_class == "hello"
    assert identifier.subject_id == "123"


def test_get_flag_score():
    """get_flag_score should be deterministic"""
    rng = Random(321321321)
    ids = [f"id-{rng.randint(0, 9999999)}" for _ in range(100)]
    actual_scores = [
        SubjectIdentifier("someclass", subject_id).get_flag_score("someflag")
        for subject_id in ids
    ]
    expected_scores_path = Path(__file__).parent / "expected_scores.txt"
    expected_scores = [
        float(row) for row in expected_scores_path.read_text().splitlines()
    ]
    assert expected_scores == actual_scores


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


@pytest.mark.parametrize(
    "names",
    [
        [],
        ["flippy.subject.UserSubject"],
        ["flippy.subject.IpAddressSubject"],
        ["flippy.subject.IpAddressSubject", "flippy.subject.UserSubject"],
    ],
)
def test_get_installed_subjects(settings, names):
    setattr(settings, "FLIPPY_SUBJECTS", names)
    assert [x.subject_class for x in Subject.get_installed_subjects()] == names


@pytest.mark.parametrize(
    "names, match",
    [
        (["flippy.this.does.not.exist"], "No module named 'flippy.this'"),
        (["flippy.subject.DoesNotExist"], "has no attribute 'DoesNotExist'"),
        (["flippy.subject.Subject"], "Can't instantiate abstract class"),
    ],
)
def test_get_installed_subjects(settings, names, match):
    setattr(settings, "FLIPPY_SUBJECTS", names)
    with pytest.raises(ConfigurationError, match=match):
        Subject.get_installed_subjects()


def test_subject_choices(settings):
    settings.FLIPPY_SUBJECTS = [
        "flippy.subject.UserSubject",
        "flippy.subject.IpAddressSubject",
    ]
    assert list(Subject.choices()) == [
        ("flippy.subject.UserSubject", "User"),
        ("flippy.subject.IpAddressSubject", "IP address"),
    ]