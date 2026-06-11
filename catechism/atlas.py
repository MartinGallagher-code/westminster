from urllib.parse import urljoin

from django.conf import settings


DEFAULT_ATLAS_BASE_URL = 'https://ontologicalatlas.com/westminster_standards/'


def atlas_base_url():
    return getattr(settings, 'WESTMINSTER_ATLAS_BASE_URL', DEFAULT_ATLAS_BASE_URL).rstrip('/') + '/'


def atlas_url(path=''):
    clean_path = path.lstrip('/')
    legacy_prefix = 'westminster_standards/'
    if clean_path.startswith(legacy_prefix):
        clean_path = clean_path[len(legacy_prefix):]
    return urljoin(atlas_base_url(), clean_path)


def atlas_work_url(catechism_slug, question):
    if catechism_slug in ('wsc', 'wlc'):
        return atlas_url(f'works/{catechism_slug}/q/{question.number}/')
    if catechism_slug == 'wcf':
        return atlas_url(f'works/wcf/chapter/{question.topic.order}/')
    return ''
