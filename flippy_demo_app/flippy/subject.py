from dataclasses import dataclass
from abc import ABC, abstractmethod
from django.http import HttpRequest
from typing import Optional, Sequence
import importlib
from .exceptions import ConfigurationError


@dataclass
class SubjectIdentifier:
    subject_class: str
    subject_id: str


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

    @classmethod
    def choices(cls):
        """Returns a django-friendly iterable of choices."""
        return SubjectChoices()


class SubjectChoices:
    def __iter__(self):
        for subject in Subject.get_installed_subjects():
            yield (subject.subject_class, str(subject))


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
