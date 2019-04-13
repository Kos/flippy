from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from .subject import Subject, import_and_instantiate_subject


class Rollout(models.Model):
    """A Rollout is what happens when someone changes the value of a flag."""

    flag_name: str = models.CharField(max_length=64)
    enable_percentage: float = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    subject: str = models.TextField(choices=Subject.choices())

    @property
    def enable_fraction(self):
        fraction = self.enable_percentage / 100
        assert 0 <= fraction <= 1
        return fraction

    @property
    def subject_instance(self) -> Subject:
        return import_and_instantiate_subject(self.subject)
