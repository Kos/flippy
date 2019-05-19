import hashlib
import importlib
from abc import ABC, abstractmethod
from typing import Optional, Sequence, Generic, TypeVar, TYPE_CHECKING

from dataclasses import dataclass
from django.http import HttpRequest

from .exceptions import ConfigurationError

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


@dataclass
class SubjectIdentifier:
    subject_class: str
    subject_id: str

    def get_flag_score(self, flag_id: str) -> float:
        """
        Given a flag name, roll the dice and determine a number in range [0, 1)
        that describes the probability if this particular subject instance should have the flag enabled.

        Deterministic.
        """
        m = hashlib.sha256()
        assert m.digest_size == 32
        delimiter = b"\0\0\0\0Cookies!\3\2\1\0"
        m.update(self.subject_class.encode())
        m.update(delimiter)
        m.update(self.subject_id.encode())
        m.update(delimiter)
        m.update(flag_id.encode())
        digest = m.digest()
        step = 4
        word = 0
        for i in range(0, m.digest_size, step):
            digest_part = digest[i : i + step]
            word ^= int.from_bytes(digest_part, "little")
        fraction = word / (1 << (8 * step))
        assert 0 <= fraction < 1
        return fraction


class Subject(ABC):
    @abstractmethod
    def get_identifier_for_request(self, request: HttpRequest) -> Optional[str]:
        ...

    @classmethod
    def get_installed_subjects(cls) -> Sequence["Subject"]:
        from django.conf import settings

        results = []
        for path in settings.FLIPPY_SUBJECTS:
            results.append(import_and_instantiate_subject(path))
        return results

    @property
    def subject_class(self):
        cls = type(self)
        return cls.__module__ + "." + cls.__name__


T = TypeVar("T")


class TypedSubject(Subject, Generic[T]):
    @abstractmethod
    def get_identifier_for_object(self, obj: T) -> Optional[str]:
        ...


def import_and_instantiate_subject(path):
    module, _, name = path.rpartition(".")
    try:
        cls = getattr(importlib.import_module(module), name)
        if not issubclass(cls, Subject):
            raise TypeError(f"{cls} should be a subclass of Subject")
        return cls()
    except (AttributeError, TypeError, ModuleNotFoundError) as e:
        raise ConfigurationError(str(e)) from e


class IpAddressSubject(Subject):
    def get_identifier_for_request(self, request: HttpRequest) -> Optional[str]:
        return request.META.get("REMOTE_ADDR")

    def __str__(self):
        return "IP address"


class UserSubject(TypedSubject["AbstractUser"]):
    def get_identifier_for_request(self, request: HttpRequest) -> Optional[str]:
        user = request.user
        return self.get_identifier_for_object(user) if user.is_authenticated else None

    def get_identifier_for_object(self, user: "AbstractUser") -> Optional[str]:
        return str(user.pk)

    def __str__(self):
        return "User"
