from .flag import Flag
from .test_utils import request_factory
import pytest


def test_flag_has_name():
    f = Flag("hello")
    assert f.name == "hello"


def test_flag_is_always_false():
    f = Flag("hello")
    assert f.get_state_for_request(request_factory()) is False
