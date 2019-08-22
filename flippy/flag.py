import inspect
from typing import TypeVar, Generic, TYPE_CHECKING, Any, Type

from django.http import HttpRequest
from django.utils.functional import LazyObject

from .subject import Subject, TypedSubject

if TYPE_CHECKING:
    from flippy.models import Rollout

flag_registry = []

T = TypeVar("T")


class Flag:
    def __init__(self, id: str, name: str = None, default=False):
        self.id = id
        self.name = name or id.title()
        self.default = default
        flag_registry.append(self)

    def get_state_for_request(self, request: HttpRequest) -> bool:
        if not isinstance(request, HttpRequest):
            raise self._type_error(
                actual_type_name=type(request).__name__,
                expected_type_name=HttpRequest.__name__,
            )
        return self._get_first_rollout_value(request)

    def _type_error(self, actual_type_name: str, expected_type_name: str):
        this_method_name = inspect.stack()[1].function
        error = TypeError(
            f"`{self.id}.{this_method_name}()` may only be called "
            f"with `{expected_type_name}` instances, not `{actual_type_name}`"
        )
        return error

    def _get_first_rollout_value(self, obj: Any) -> bool:
        # Note: Flag is exported in __init__.py,
        # -> don't import models at import time
        from .models import Rollout

        matching_rollouts = Rollout.objects.filter(flag_id=self.id).order_by(
            "-create_date"
        )

        for rollout in matching_rollouts:
            maybe_value = rollout.get_flag_value(obj)
            if maybe_value is not None:
                return maybe_value
            # Otherwise, ignore the particular rollout - it doesn't match the request.

        return self.default

    def accepts_subject(self, subject: Subject):
        return True


class TypedFlag(Flag, Generic[T]):
    def get_state_for_object(self, obj: T) -> bool:
        if isinstance(obj, LazyObject):
            # Compatibility for `request.user`
            obj._setup()
            obj = obj._wrapped
        if not isinstance(obj, self.expected_type):
            raise self._type_error(
                actual_type_name=type(obj).__name__,
                expected_type_name=self.expected_type.__name__,
            )

        return self._get_first_rollout_value(obj)

    def accepts_subject(self, subject: Subject):
        return isinstance(subject, TypedSubject) and subject.is_supported_type(
            self.expected_type
        )

    @property
    def expected_type(self) -> Type:
        """
        Return the object type supported by this flag. This is the same type that is later expected in get_state_for_object().
        """
        # NOTE: TypingFlag is generic, but `type(TypedFlag[int](...))` will give you just `TypingFlag`,
        # not `TypingFlag[int]` which we need here for further inspection.
        # Instead, the actual generic type `TypingFlag[T]` is accessible on the instance:
        generic_class_type = self.__orig_class__
        return generic_class_type.__args__[0]
