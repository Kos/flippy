from django.contrib.auth.models import User
from django.template.response import TemplateResponse

from .flags import enable_weather, enable_cats, enable_sudoku


def index(request):
    if request.user.is_authenticated:
        show_sudoku = should_show_sudoku(request.user)
    else:
        show_sudoku = False

    # Any flag can be queried with a request.
    return TemplateResponse(
        request,
        "index.html",
        {
            "show_weather": enable_weather.get_state_for_request(request),
            "show_cat": enable_cats.get_state_for_request(request),
            "show_sudoku": show_sudoku,
        },
    )


def should_show_sudoku(user: User):
    # TypedFlags can be queried anywhere in the code, even without a request:
    return enable_sudoku.get_state_for_object(user)
