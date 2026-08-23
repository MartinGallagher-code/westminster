import json
import urllib.parse

VALID_TRADITIONS = {'westminster', 'three_forms_of_unity', 'reformed_confessions'}

# What a visitor with no docFilters cookie sees — including every search-engine
# crawler. Anything advertised in sitemap.xml has to resolve under these.
DEFAULT_TRADITIONS = ['westminster']


def get_active_traditions(request):
    """Read the docFilters cookie; return a list of active tradition slugs.

    The cookie value is URL-encoded by JS (via encodeURIComponent), so we
    decode it before parsing as JSON.  Falls back to ['westminster'] if the
    cookie is absent or invalid.
    """
    raw = request.COOKIES.get('docFilters', '')
    if raw:
        try:
            filters = json.loads(urllib.parse.unquote(raw))
            active = [k for k in VALID_TRADITIONS if filters.get(k)]
            if active:
                return active
        except (ValueError, TypeError):
            pass
    return list(DEFAULT_TRADITIONS)
