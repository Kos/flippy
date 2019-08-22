from django.contrib.auth.models import User

from flippy import Flag
from django.conf import settings

from flippy.flag import TypedFlag

enable_weather: Flag = Flag("enable_weather", "Weather widget")
enable_cats: Flag = Flag("enable_cats", "Cats widget", default=settings.DEBUG)
enable_sudoku: TypedFlag[User] = TypedFlag[User]("enable_sudoku", "Sudoku")
