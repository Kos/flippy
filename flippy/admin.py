from django.contrib import admin
from django import forms

from flippy.flag import flag_registry
from flippy.models import Rollout
from flippy.subject import Subject


class FlagChoices:
    def __iter__(self):
        for flag in sorted(flag_registry, key=lambda flag: flag.name):
            yield (flag.id, flag.name)


class SubjectChoices:
    def __iter__(self):
        for subject in Subject.get_installed_subjects():
            yield (subject.subject_class, str(subject))


class RolloutForm(forms.ModelForm):
    flag_id = forms.ChoiceField(choices=FlagChoices, label="Flag")
    subject = forms.ChoiceField(choices=SubjectChoices)

    class Meta:
        model = Rollout
        fields = ["flag_id", "subject", "enable_percentage"]


class RolloutAdmin(admin.ModelAdmin):
    form = RolloutForm
    list_display = ["flag_name", "subject_name", "enable_percentage", "create_date"]
    list_filter = ["flag_id"]


admin.site.register(Rollout, RolloutAdmin)
