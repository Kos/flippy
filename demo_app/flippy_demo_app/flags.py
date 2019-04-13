from flippy import Flag
from django.conf import settings

flag_foo = Flag("foo", "Foo")
flag_bar = Flag("bar", "Bar", default=settings.DEBUG)
