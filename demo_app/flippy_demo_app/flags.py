from flippy import Flag
from django.conf import settings

enable_weather = Flag("enable_weather", "Weather widget")
enable_cats = Flag("enable_cats", "Cats widget", default=settings.DEBUG)
