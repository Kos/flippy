from .subject import Subject


class Flag:
    def __init__(self, name, default=False):
        self.name = name
        self.default = default

    def get_state_for_request(self, request):
        # Note: Flag is exported in __init__.py,
        # -> don't import models at import time
        from .models import Rollout

        for rollout in Rollout.objects.all():  # TODO
            subject: Subject = rollout.subject_instance
            identifier = subject.get_subject_identifier_for_request(request)
            score = identifier.get_flag_score(self.name)
            if score < rollout.enable_fraction:
                return True
        return self.default
