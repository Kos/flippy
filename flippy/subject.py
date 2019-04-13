from dataclasses import dataclass
from abc import ABC, abstractmethod
from django.http import HttpRequest
from typing import Optional, Sequence
import importlib
from .exceptions import ConfigurationError
import hashlib


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
    def get_subject_identifier_for_request(
        self, request: HttpRequest
    ) -> Optional[SubjectIdentifier]:
        ...

    @property
    def subject_class(self):
        cls = type(self)
        return cls.__module__ + "." + cls.__name__

    @classmethod
    def get_installed_subjects(cls) -> Sequence["Subject"]:
        from django.conf import settings

        results = []
        for path in settings.FLIPPY_SUBJECTS:
            results.append(import_and_instantiate_subject(path))
        return results


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
    def get_subject_identifier_for_request(
        self, request: HttpRequest
    ) -> Optional[SubjectIdentifier]:
        ip = request.META.get("REMOTE_ADDR")
        return SubjectIdentifier(self.subject_class, ip) if ip else None

    def __str__(self):
        return "IP address"


class UserSubject(Subject):
    def get_subject_identifier_for_request(
        self, request: HttpRequest
    ) -> Optional[SubjectIdentifier]:
        user = request.user
        return (
            SubjectIdentifier(self.subject_class, str(user.pk))
            if user.is_authenticated
            else None
        )

    def __str__(self):
        return "User"
