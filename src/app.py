import os
import sys
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import path
from django.core.wsgi import get_wsgi_application
from search import find_terms
from django.core.management import execute_from_command_line

from editor import editor_data, editor_delete, editor_page, editor_save

# --- Configuration ---------------------------------------------------------

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

def configure_django():
    """Configure standalone Django settings only when necessary."""
    if settings.configured:
        return

    settings.configure(
        DEBUG=DEBUG,
        SECRET_KEY=SECRET_KEY,
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=ALLOWED_HOSTS,
        INSTALLED_APPS=["django.contrib.staticfiles"],
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "whitenoise.middleware.WhiteNoiseMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
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


#--------------- VIEWS -----------------

def home(request):
    return render(request, "index.html")

def search(request):
    return JsonResponse({"results": find_terms(request.GET.get("q", ""))})

#--------------- URL PATTERNS -----------------

def get_editor_routes():
    """Return local editor routes only when explicitly enabled in debug mode."""
    if not (DEBUG and os.getenv("ENABLE_LOCAL_EDITOR", "false").lower() == "true"):
        return []

    return [
        path("editor/", editor_page, name="editor"),
        path("editor/api/", editor_data, name="editor_data"),
        path("editor/api/save/", editor_save, name="editor_save"),
        path("editor/api/delete/", editor_delete, name="editor_delete"),
    ]

def get_urlpatterns():
    """Combine public routes with optional development-only routes."""
    return [
        path("", home, name="home"),
        path("search/", search, name="search"),
    ] + get_editor_routes()


#--------------- ENTRY POINTS -----------------

configure_django()
urlpatterns = get_urlpatterns()
application = get_wsgi_application()

if __name__ == "__main__":
    execute_from_command_line(sys.argv)