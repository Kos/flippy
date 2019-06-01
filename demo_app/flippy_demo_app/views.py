from django.template.response import TemplateResponse

from .flags import enable_weather, enable_cats


def index(request):
    return TemplateResponse(
        request,
        "index.html",
        {
            "show_weather": enable_weather.get_state_for_request(request),
            "show_cat": enable_cats.get_state_for_request(request),
        },
    )
