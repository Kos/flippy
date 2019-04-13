from dataclasses import dataclass
from abc import ABC, abstractmethod
from django.http import HttpRequest
from typing import Optional


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


class IpAddressSubject(Subject):
    def get_subject_identifier_for_request(
        self, request: HttpRequest
    ) -> Optional[SubjectIdentifier]:
        ip = request.META.get("REMOTE_ADDR")
        return SubjectIdentifier(self.subject_class, ip) if ip else None
