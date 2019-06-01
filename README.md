# Flippy - a feature flipper for Django

Flippy gives you a simple way to add [feature flags](https://martinfowler.com/articles/feature-toggles.html) to your Django application using a simple syntax:

```python
# define a flag
flag_enable_chat = Flag(id="chat", name="Enable the chat feature")

# check the flag value for a specific user
chat_enabled = flag_enable_chat.get_state_for_request(request)	
if chat_enabled:
    ...
```

This lets you release your new feature to your users in a slow, controlled manner.

The flags are defined in code with initial value, and later enabled via Django Admin for specific subgroups of users, with a good degree of flexibility.

## Main selling point: Subject flexibility

Flippy tries to assume as little as possible about the type of feature flags you write. This means you can do things like:

- enable a feature for a percentage of IP addresses (anonymous visitors)
- enable a feature for all (or a percentage of) users who have some property (admins, beta testers)
- enable a feature for each user in 50% of registered accounts
- enable a feature on 50% of pages (posts, documents...)

## Concepts

- A **Flag** is a parameter that controls if a feature should be enabled for users. For example, if you're adding chat to your application, you can hide it behind a flag `enable_chat`.
- **Rollout** is the process of enabling features for your users. For example, you might want to have `enable_chat` initially equal `False` for everyone, then enable it for a group of beta-testers, then if nothing explodes - roll it out to 25% of users, then 50% users and finally for everyone! Each such action is considered a separate Rollout.  
- A **Subject** a group that for whom you'd like to enable the feature flags. Typical use case is to enable flags for Users individually, but your app will have more concepts that would make good Subjects. For example:
  - Users can be narrowed out by app-specific properties, like "subscription plan". "Free Trial Users" or "Premium Users" are good Subjects.
  - If your app has multi-user accounts, then a whole Account can be a Subject as well.
  - For an app that resembles Google Docs, you may choose to roll out a feature per-document rather than per-user. In this case, a document could become a Subject.

## Quick start

1. Install `flippy` in your app:

```bash
pip install git+https://github.com/kos/flippy.git@master
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

flag_enable_chat = Flag(id="chat", name="Chat Feature")
```

5. Use the flag somewhere in your code:

```python
from .flags import flag_enable_chat

def some_page(request):
	chat_enabled = flag_enable_chat.get_state_for_request(request)
	if chat_enabled:
		...
```

Now the flag is defined in code, but it will be always `False` because we haven't rolled the feature out yet.

6. Visit the Django Admin in http://localhost:8000/admin/flippy/rollout/ and create a new rollout for this flag to enable it.


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

## Advanced: Using Flags without a request

Sometimes you need to query a feature flag somewhere deep in the code where you don't have access to the `request` variable, because:

- you're in a context where the `request` is not accessible (like models or utils) and it's not practical to pass the value all the way from the view
- you're writing a management command or a Celery task, so there's no request whatsoever

This can be addressed using *typed flags*:

```python
enable_sudoku = TypedFlag[User]("enable_sudoku", "Sudoku")
```

A typed flag, in addition to querying by request, can also be queried with an object of its declared type:

```python
sudoku_enabled = enable_sudoku.get_state_for_object(user)
```

However, there's a limitation: a typed flag can only be rolled out for compatible subjects that match their type. This means that this flag can be rolled out to `flippy.subject.UserSubject"` but not `flippy.subject.IpAddressSubject`.

Django Admin will forbid you from creating a mismatched Rollout.

Here's an example custom Subject that could be used together with `TypedFlag[Account]` in order to roll features to a given percentage of Accounts (your example custom model):

```python
class AccountSubject(TypedSubject["Account"]):
    def get_identifier_for_request(self, request: HttpRequest) -> Optional[str]:
        user = request.user
        if user.is_anonymous or user.account is None:
            return None
        return self.get_identifier_for_object(user.account)

    def get_identifier_for_object(self, account) -> Optional[str]:
        return str(account.pk)

    def is_supported_type(self, type) -> bool:
        from your_app import Account

        return issubclass(type, Account)

    def __str__(self):
        return "Accounts"
```

Note that in this case, in addition to `get_identifier_for_request` you also need to implement `get_identifier_for_object`. It's convenient to define one in terms of the other. The method `is_supported_type` is required for validation (so that Flippy can ensure the subject will be only used with matching flags).

## Status

**Alpha**. You mileage may vary, things may and will break. The API can change in future versions. I'm gathering feedback, so please try it out, open issues and describe what's broken or missing.