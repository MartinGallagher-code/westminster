from catechism.models import Catechism, Topic


def sidebar_topics(request):
    return {
        'catechisms': Catechism.objects.all(),
        'sidebar_topics': Topic.objects.select_related('catechism').all(),
    }
