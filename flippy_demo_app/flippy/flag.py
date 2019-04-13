class Flag:
    def __init__(self, name, default=False):
        self.name = name
        self.default = default

    def get_state_for_request(self, request) -> bool:
        # Note: Flag is exported in __init__.py,
        # -> don't import models at import time
        from .models import Rollout

        matching_rollouts = Rollout.objects.filter(flag_name=self.name).order_by(
            "-create_date"
        )
        return self._get_first_rollout_value(request, matching_rollouts)

    def _get_first_rollout_value(self, request, rollouts) -> bool:
        for rollout in rollouts:
            maybe_value = rollout.get_flag_value_for_request(request)
            if maybe_value is not None:
                return maybe_value
            # Otherwise, ignore the particular rollout - it doesn't match the request.

        return self.default
