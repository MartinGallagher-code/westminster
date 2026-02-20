from catechism.models import Topic


def sidebar_topics(request):
    return {'sidebar_topics': Topic.objects.all()}
