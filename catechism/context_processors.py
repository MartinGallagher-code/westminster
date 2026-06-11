from catechism.atlas import atlas_url
from catechism.models import Catechism
from catechism.utils import get_active_traditions


def sidebar_topics(request):
    return {
        'catechisms': Catechism.objects.all(),
        'active_traditions': get_active_traditions(request),
        'atlas_home_url': atlas_url(),
    }
