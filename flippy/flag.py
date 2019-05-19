from typing import Any, TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from .models import Rollout

flag_registry = []


class Flag:
    def __init__(self, id: str, name: str = None, default=False):
        self.id = id
        self.name = name or id.title()
        self.default = default
        flag_registry.append(self)

    def get_value(self, obj: Any) -> bool:
        # Note: Flag is exported in __init__.py,
        # -> don't import models at import time
        from .models import Rollout

        matching_rollouts = Rollout.objects.filter(flag_id=self.id).order_by(
            "-create_date"
        )
        return self._get_first_rollout_value(obj, matching_rollouts)

    def _get_first_rollout_value(self, obj: Any, rollouts: Iterable['Rollout']) -> bool:
        for rollout in rollouts:
            maybe_value = rollout.get_flag_value(obj)
            if maybe_value is not None:
                return maybe_value
            # Otherwise, ignore the particular rollout - it doesn't match the request.

        return self.default

    def get_state_for_object(self, request) -> bool:
        # Note: Flag is exported in __init__.py,
        # -> don't import models at import time
        from .models import Rollout

        matching_rollouts = Rollout.objects.filter(flag_id=self.id).order_by(
            "-create_date"
        )
        return self._get_first_rollout_value(request, matching_rollouts)

    def _get_first_rollout_value_for_object(self, request, rollouts) -> bool:
        for rollout in rollouts:
            maybe_value = rollout.get_flag_value_for_object(request)
            if maybe_value is not None:
                return maybe_value
            # Otherwise, ignore the particular rollout - it doesn't match the request.

        return self.default
