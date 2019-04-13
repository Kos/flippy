from datetime import datetime
from typing import Optional

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from flippy.flag import flag_registry
from .subject import import_and_instantiate_subject


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

    def get_flag_value_for_request(self, request) -> Optional[bool]:
        """
        Returns the flag state assigned determined by this rollout to a given request.

        Returns None in case the request doesn't match the rollout's subject.
        """
        subject = self.subject_obj
        identifier = subject.get_subject_identifier_for_request(request)
        if not identifier:
            return None
        score = identifier.get_flag_score(self.flag_id)
        return score < self.enable_fraction

    @property
    def subject_obj(self):
        subject = import_and_instantiate_subject(self.subject)
        return subject

    @property
    def subject_name(self):
        return str(self.subject_obj)

    @property
    def flag_obj(self):
        return [f for f in flag_registry if f.id == self.flag_id][0]

    @property
    def flag_name(self):
        return self.flag_obj.name
