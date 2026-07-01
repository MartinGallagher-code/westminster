from urllib.parse import urljoin

from django.conf import settings


# The Westminster Standards Atlas now lives natively in this project, mounted
# at /atlas/ (see config/urls.py and the westminster_standards app), so links
# resolve internally by default. Set WESTMINSTER_ATLAS_BASE_URL to point back
# at the public ontologicalatlas.com deployment if that is ever wanted.
DEFAULT_ATLAS_BASE_URL = '/atlas/'


def atlas_base_url():
    return getattr(settings, 'WESTMINSTER_ATLAS_BASE_URL', DEFAULT_ATLAS_BASE_URL).rstrip('/') + '/'


def atlas_url(path=''):
    clean_path = path.lstrip('/')
    legacy_prefix = 'westminster_standards/'
    if clean_path.startswith(legacy_prefix):
        clean_path = clean_path[len(legacy_prefix):]
    return urljoin(atlas_base_url(), clean_path)
