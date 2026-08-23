"""Page caching for the read-only pages.

Chapter, question, comparison and handout pages are expensive to render —
commentaries, proof texts, cross-references, ontology chips — and change only
when the data is reloaded, which already ends with ``clear_cache``.

The cache key is built explicitly rather than by varying on the Cookie header:
every visitor carries a csrftoken, so ``vary_on_cookie`` would give each of
them a private copy and cache nothing useful. What actually changes the page
is the active document collections, so that is what the key carries.

Only anonymous GETs are cached. A signed-in reader's page shows their notes,
their highlights and whether an answer is in their memorisation deck, and no
key is worth the risk of handing one reader another's page.
"""

import hashlib
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse

from .utils import get_active_traditions

CACHE_KEY_PREFIX = 'page'


def _cache_key(request):
    traditions = ','.join(sorted(get_active_traditions(request)))
    raw = f'{request.get_full_path()}|{traditions}'
    digest = hashlib.sha256(raw.encode()).hexdigest()[:32]
    return f'{CACHE_KEY_PREFIX}:{digest}'


def _is_cacheable_request(request):
    if request.method != 'GET':
        return False
    if getattr(request, 'user', None) is not None and request.user.is_authenticated:
        return False
    # An anonymous visitor with a session may be carrying a flash message,
    # which must never be baked into a shared page.
    if request.COOKIES.get(settings.SESSION_COOKIE_NAME):
        return False
    return True


def _is_cacheable_response(response):
    if response.status_code != 200:
        return False
    # A response that sets a cookie is establishing per-visitor state.
    if response.cookies:
        return False
    if response.has_header('Vary') and 'cookie' in response['Vary'].lower():
        return False
    return True


def cache_read_only_page(view_func):
    """Cache a page for anonymous visitors, keyed by path and collections.

    A no-op when ``PAGE_CACHE_SECONDS`` is 0, which is the default outside
    production so local edits show up immediately.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        timeout = getattr(settings, 'PAGE_CACHE_SECONDS', 0)
        if not timeout or not _is_cacheable_request(request):
            return view_func(request, *args, **kwargs)

        key = _cache_key(request)
        cached = cache.get(key)
        if cached is not None:
            response = HttpResponse(
                cached['content'], content_type=cached['content_type'],
            )
            response['X-Page-Cache'] = 'hit'
            return response

        response = view_func(request, *args, **kwargs)

        def store(rendered):
            if _is_cacheable_response(rendered):
                cache.set(key, {
                    'content': rendered.content,
                    'content_type': rendered.get('Content-Type', 'text/html; charset=utf-8'),
                }, timeout)
            return rendered

        if hasattr(response, 'add_post_render_callback'):
            response.add_post_render_callback(store)
        else:
            store(response)
        response['X-Page-Cache'] = 'miss'
        return response

    return wrapper
