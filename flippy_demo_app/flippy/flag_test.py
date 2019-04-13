from .flag import Flag
from .test_utils import request_factory


def test_flag_has_name():
    f = Flag("hello")
    assert f.name == "hello"


def test_flag_is_false_by_default():
    f = Flag("hello")
    assert f.get_state_for_request(request_factory()) is False


def test_flag_true_default_value():
    f = Flag("hello", default=True)
    assert f.get_state_for_request(request_factory()) is True
