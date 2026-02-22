from django.contrib import admin
from django.http import JsonResponse
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


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('accounts/', include('accounts.urls')),
    path('', include('catechism.urls')),
]
