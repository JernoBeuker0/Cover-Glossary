"""Django routes and configuration for a small, read-only glossary."""
import sys
from pathlib import Path

from django.conf import settings

SRC_DIR = Path(__file__).resolve().parent

# A small Django project can keep its settings here instead of adding
# a separate settings package and manage.py.
if not settings.configured:
    settings.configure(
        DEBUG=True,  # Local development only, not for a public deployment.
        SECRET_KEY="local-development-only-change-before-deployment",
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=["localhost", "127.0.0.1"],
        INSTALLED_APPS=["django.contrib.staticfiles"],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [SRC_DIR / "templates"],
                "APP_DIRS": True,
            }
        ],
        STATIC_URL="/static/",
        STATICFILES_DIRS=[SRC_DIR / "static"],
    )

from django.http import JsonResponse  # noqa: E402
from django.shortcuts import render  # noqa: E402
from django.urls import path  # noqa: E402

from search import find_terms  # noqa: E402


def home(request):
    """Render the search page."""
    return render(request, "index.html")


def search(request):
    """Return up to five search suggestions as JSON."""
    query = request.GET.get("q", "")
    return JsonResponse({"results": find_terms(query)})


urlpatterns = [
    path("", home, name="home"),
    path("search/", search, name="search"),
]

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
