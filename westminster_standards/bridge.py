"""Integration bridge between the Westminster Standards Atlas and Study Reformed.

The Atlas ships its own full-text pages for the Confession chapters and the
catechism questions (``works/wcf/chapter/<n>/`` and ``works/<wsc|wlc>/q/<n>/``).
Study Reformed already owns that text with richer pages (commentary, proof
texts, cross-references, notes), so rather than keep two copies these routes
redirect to the canonical Study Reformed page. The Atlas remains the home of
what it uniquely provides — the ontology, personas, cruxes, schools and heads.

Keeping this coupling in its own module leaves the ported ``views.py`` pristine
for future syncs with the upstream ontologicalatlas.com app.
"""

from django.http import Http404
from django.shortcuts import redirect

from catechism.models import Catechism, Question, Topic

from . import views as _atlas_views


def wcf_chapter_redirect(request, number):
    """``/atlas/works/wcf/chapter/<n>/`` -> the Study Reformed WCF chapter page."""
    try:
        topic = Topic.objects.select_related('catechism').get(
            catechism__slug='wcf', order=number,
        )
    except Topic.DoesNotExist:
        raise Http404("No Westminster Confession chapter %s" % number)
    return redirect(topic.get_absolute_url())


def catechism_question_redirect(request, catechism_slug, number):
    """``/atlas/works/<wsc|wlc>/q/<n>/`` -> the Study Reformed question page."""
    if catechism_slug not in ('wsc', 'wlc'):
        raise Http404("Unknown catechism %r" % catechism_slug)
    try:
        question = Question.objects.select_related('catechism', 'topic').get(
            catechism__slug=catechism_slug, number=number,
        )
    except Question.DoesNotExist:
        raise Http404("No %s question %s" % (catechism_slug, number))
    return redirect(question.get_absolute_url())


def work_detail_dispatch(request, slug):
    """Redirect the three Standards that Study Reformed already carries to their
    document home; render the Atlas's own page for the rest (the Directory for
    Public Worship, the Form of Presbyterial Church Government, and the Sum of
    Saving Knowledge), which Study Reformed does not host.
    """
    if slug in ('wcf', 'wlc', 'wsc'):
        try:
            catechism = Catechism.objects.get(slug=slug)
        except Catechism.DoesNotExist:
            raise Http404("Unknown standard %r" % slug)
        return redirect(catechism.get_absolute_url())
    return _atlas_views.work_detail(request, slug)
