import json
import urllib.parse

VALID_TRADITIONS = {'westminster', 'three_forms_of_unity'}


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
    return ['westminster']
