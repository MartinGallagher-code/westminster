from catechism.atlas import atlas_url
from catechism.models import Catechism
from catechism.utils import get_active_traditions

# Pages that lead with their own search box. The navbar renders one too, so on
# these the reader was given two search fields at once — stacked one above the
# other on a phone.
SEARCH_LED_ROUTES = {'catechism:home', 'catechism:search'}


def sidebar_topics(request):
    match = getattr(request, 'resolver_match', None)
    return {
        'catechisms': Catechism.objects.all(),
        'active_traditions': get_active_traditions(request),
        'atlas_home_url': atlas_url(),
        'hide_navbar_search': bool(match) and match.view_name in SEARCH_LED_ROUTES,
    }
