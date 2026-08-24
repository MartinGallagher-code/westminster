from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.urls import path, include

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'


def health_check(request):
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok"})
    except Exception:
        return JsonResponse({"status": "error"}, status=503)


def webmanifest(request):
    """The web app manifest, rendered rather than served as a static file.

    Its icon URLs have to be the hashed ones the manifest storage produces —
    a JSON file is not post-processed the way CSS is, so hard-coded paths in a
    static manifest would name files that are only incidentally still there.
    """
    return render(
        request, 'site.webmanifest',
        content_type='application/manifest+json',
    )


def favicon(request):
    """Browsers ask for /favicon.ico at the root whatever a page declares.

    Nothing served it, so every such request was a 404 — visible on /health/,
    which renders no <head> to declare an icon from, and in the logs besides.
    Resolved per request rather than at import, so the hashed name the
    manifest storage produces is picked up.
    """
    return redirect(static('img/favicon.ico'), permanent=True)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.ico', favicon, name='favicon'),
    path('site.webmanifest', webmanifest, name='webmanifest'),
    path('health/', health_check, name='health_check'),
    path('accounts/', include('accounts.urls')),
    # Westminster Standards Atlas — mounted before the catechism catch-all
    # (`<slug:catechism_slug>/`) so `/atlas/...` is not shadowed by it.
    path('atlas/', include('westminster_standards.urls')),
    path('', include('catechism.urls')),
]
