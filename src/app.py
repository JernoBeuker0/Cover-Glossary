"""Django routes and configuration for the Cover glossary."""
import os
import sys
from pathlib import Path

from django.conf import settings

SRC_DIR = Path(__file__).resolve().parent
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "local-development-only-not-for-production"
    else:
        raise RuntimeError("Set DJANGO_SECRET_KEY before starting in production")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

if not settings.configured:
    settings.configure(
        DEBUG=DEBUG,
        SECRET_KEY=SECRET_KEY,
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=ALLOWED_HOSTS,
        INSTALLED_APPS=["django.contrib.staticfiles"],
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "whitenoise.middleware.WhiteNoiseMiddleware",
        ],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [SRC_DIR / "templates"],
                "APP_DIRS": True,
            }
        ],
        STATIC_URL="/static/",
        STATICFILES_DIRS=[SRC_DIR / "static"],
        STATIC_ROOT=SRC_DIR / "collected_static",
    )

from django.http import JsonResponse  # noqa: E402
from django.shortcuts import render  # noqa: E402
from django.urls import path  # noqa: E402
from django.core.wsgi import get_wsgi_application  # noqa: E402
from search import find_terms  # noqa: E402


def home(request):
    return render(request, "index.html")


def search(request):
    return JsonResponse({"results": find_terms(request.GET.get("q", ""))})


urlpatterns = [
    path("", home, name="home"),
    path("search/", search, name="search"),
]

# Gunicorn loads this application rather than Django's development server.
application = get_wsgi_application()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)