from flippy import Flag
from django.conf import settings

flag_foo = Flag("foo")
flag_bar = Flag("bar", default=settings.DEBUG)
