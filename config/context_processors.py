from django.conf import settings
from django.templatetags.static import static


def google_analytics(request):
    return {'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', '')}


def site_metadata(request):
    return {
        'canonical_url': request.build_absolute_uri(request.path),
        'og_image_url': request.build_absolute_uri(static('img/og-image.png')),
    }
