from catechism.models import Catechism


def sidebar_topics(request):
    return {
        'catechisms': Catechism.objects.all(),
    }
