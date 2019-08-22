from datetime import datetime
from typing import Optional, Any

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.http import HttpRequest

from flippy import Flag
from flippy.flag import flag_registry, TypedFlag
from .subject import import_and_instantiate_subject, SubjectIdentifier, TypedSubject


class Rollout(models.Model):
    """A Rollout is what happens when someone changes the value of a flag."""

    flag_id: str = models.CharField(max_length=64)
    subject: str = models.TextField()
    enable_percentage: float = models.FloatField(
        default=100, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    create_date: datetime = models.DateTimeField(auto_now_add=True)

    @property
    def enable_fraction(self):
        fraction = self.enable_percentage / 100
        assert 0 <= fraction <= 1
        return fraction

    def get_flag_value(self, obj: Any) -> Optional[bool]:
        """
        Returns the flag state assigned determined by this rollout to a given request.

        Returns None in case the request doesn't match the rollout's subject.
        """
        identifier = self._build_identifier(obj)
        if not identifier:
            return None
        score = identifier.get_flag_score(self.flag_id)
        return score < self.enable_fraction

    def _build_identifier(self, obj: Any) -> Optional[SubjectIdentifier]:
        subject = self.subject_obj
        if isinstance(obj, HttpRequest):
            subject_id = subject.get_identifier_for_request(obj)
        else:
            assert isinstance(subject, TypedSubject)  # TODO handle this gracefully
            subject_id = subject.get_identifier_for_object(obj)
        if subject_id is None:
            return None
        return SubjectIdentifier(subject.subject_class, subject_id)

    @property
    def subject_obj(self):
        subject = import_and_instantiate_subject(self.subject)
        return subject

    @property
    def subject_name(self):
        return str(self.subject_obj)

    @property
    def _flag_obj(self) -> Optional[Flag]:
        return next((f for f in flag_registry if f.id == self.flag_id), None)

    @property
    def flag_name(self):
        obj = self._flag_obj
        return obj.name if obj else f"<missing flag: `{self.flag_id}`>"

    def clean(self):
        flag = self._flag_obj
        if flag is None:
            raise ValidationError(f"Flag `{self.flag_id}` does not exist")
        subject = self.subject_obj
        if not flag.accepts_subject(subject):
            message = f"Flag `{flag.name}` cannot be used with subject `{subject}`."
            if isinstance(flag, TypedFlag):
                message += f" It can only be used with subjects that support `{flag.expected_type.__name__}`."
            raise ValidationError(message)
