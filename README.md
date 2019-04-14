# Flippy - a feature flipper for Django

## Concepts

- A **Flag** is a parameter that controls if a feature should be enabled to users. For example, if you're adding chat to your application, you can have a flag `enable_chat`.
- **Rollout** is the process of enabling features for your users. For example, you might want to have `enable_chat` initially equal `False` for everyone, then enable it for a group of beta-testers, then if nothing explodes - roll it out to 25% of users, then 50% users and finally for everyone!
- A **Subject** is an individual or a group that for whom you'd like to enable flags. Depending on your case, you may want to enable a flag for some subset of:
  - Django users,
  - all anonymous users based on their IP,
  - only users on a specific subscription plan...

## Quick start

1. Install `flippy` in your app:

```bash
pip install flippy
```

2. Add `flippy` to your `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = [
...
'flippy',
]
```

3. Run `python manage.py migrate` to create the `Rollout` model.

4. Create a file `flags.py` somewhere in your application and define your first flag:

```python
from flippy import Flag

flag_enable_chat = Flag(id="chat", name="Enable the chat feature")
```

5. Use the flag somewhere in your code:

```python
from .flags import flag_enable_chat

def some_page(request):
chat_enabled = flag_enable_chat.get_state_for_request(request)
if chat_enabled:
...
```

Now the flag will be always disabled:

6. Visit the Django Admin in http://localhost:8000/admin/flippy/rollout/ and create a new rollout for this flag to enable it locally.

7. If you'd like to disable this flag later, the simplest way is to create a new rollout that sets the percentage to zero. This way you preserve the history when the flag has been enabled and when it was disabled. Alternatively, you can edit the previous rollout in-place or delete it.

## Writing flags

New flags can be added very easily by instantiating the `Flag` class.

The initial state of each flag can be controlled using the `default` parameter:

```python
enable_logging = Flag(id="logging", default=True)
```

Hint: For local development, it's convenient to have the flags enabled by default, but at the same time you'd like them to be default-off on production until rolled out. There's a simple pattern that accomplishes this:

```python
from django.conf import settings

enable_beta_features = Flag(..., default=settings.DEBUG)
```

## Writing subjects

Flippy comes with some generic subjects (Django users, IP addresses) for the most common use case, but you can get the most value by defining your own subjects.

For example, assume your application has users with various subscription levels:

```python
class User(...):
    subscription_level_choices = [
        (0, "Trial"),
        (1, "Standard"),
        (2, "Premium"),
    ]
    subscription_level = models.IntegerField(choices=subscription_level_choices)
```

Here's an example `Subject` implementation that lets you roll out features to all (or a percentage of) Premium users:

```python
from flippy import Subject

class PremiumUserSubject(Subject):
    def get_identifier_for_request(self, request: HttpRequest) -> Optional[str]:
        user = request.user
        return (
            str(user.pk)
            if user.is_authenticated and user.subscription_level == 2
            else None
        )

    def __str__(self):
        return "Premium Users"    
```

As you can see, the method `get_identifier_for_request` returns either `None` if the subject doesn't match the request (there's no user or the user is not premium), or otherwise, the user's ID. In fact, any string is acceptable here, as long as it's different between each premium user. (The value is later used as a part of a hash, in order to ensure that percentage-based rollouts are deterministic for each user.)

The next step is to register this subject in your Django settings, so that it becomes available as an option:

```python
# settings.py

FLIPPY_SUBJECTS = [
    # standard subjects
    "flippy.subject.IpAddressSubject",
    "flippy.subject.UserSubject",
    # custom subjects
    "your_app.subjects.PremiumUserSubject",
]

```

Of course you're not limited to users. If your application features multi-user Accounts, you can use the same approach and write an `Account` subject. In that case, the function should return a group ID instead of user ID.

## Percentage-based rollout

- ... TODO: describe how it works


## Parametrized subjects

- ... TODO: implement, describe how it works