from django.template.response import TemplateResponse

from .flags import flag_foo, flag_bar


def index(request):
    return TemplateResponse(
        request,
        "index.html",
        {
            "flag_foo": flag_foo.get_value(request),
            "flag_bar": flag_bar.get_value(request),
        },
    )
