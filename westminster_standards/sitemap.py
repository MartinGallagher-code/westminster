"""The Atlas's public URLs, for inclusion in the site sitemap.

Study Reformed builds one sitemap for the whole site (``catechism.views
.sitemap_xml``). The Atlas is mounted at /atlas/ and owns several hundred
pages that nothing else links to exhaustively — the personas, cruxes, schools,
heads of doctrine, and every locus/attribute/value page of the ontology — so
they are enumerated here.

Only routes that render are listed. The Confession-chapter and catechism-
question routes redirect to Study Reformed's canonical pages (see
``bridge.py``) and the three Standards it hosts redirect to their document
homes, so those are deliberately excluded: a sitemap should advertise
destinations, not redirects.

Kept out of ``views.py`` so the ported module stays syncable with upstream.
"""

from django.urls import reverse

from .cruxes import CRUXES
from .data import DIMENSIONS, DIMENSION_PAIRS
from .heads_of_doctrine import HEADS_OF_DOCTRINE
from .personas import PERSONAS
from .schools import SCHOOLS
from .works import WORKS

# The Standards that Study Reformed hosts itself; their Atlas work pages
# redirect, so they are not sitemap destinations.
REDIRECTING_WORK_SLUGS = {'wcf', 'wlc', 'wsc'}

INDEX_ROUTES = [
    'home', 'ontology', 'personas_list', 'cruxes_list', 'schools_list',
    'heads_list', 'works_list', 'dimension_pairs', 'compare_personas',
    'compare_schools',
]


def atlas_sitemap_paths():
    """Every Atlas URL that renders a page, in a stable order."""
    paths = [reverse(f'westminster_standards:{route}') for route in INDEX_ROUTES]

    for dimension in DIMENSIONS:
        paths.append(reverse(
            'westminster_standards:dimension_detail', args=[dimension['key']],
        ))
        for attribute in dimension['attributes']:
            for value in attribute['values']:
                paths.append(reverse(
                    'westminster_standards:value_detail',
                    args=[dimension['key'], attribute['key'], value['key']],
                ))

    paths.extend(
        reverse('westminster_standards:dimension_pair_detail', args=['-'.join(pair)])
        for pair in DIMENSION_PAIRS
    )
    paths.extend(
        reverse('westminster_standards:head_detail', args=[head['slug']])
        for head in HEADS_OF_DOCTRINE
    )
    paths.extend(
        reverse('westminster_standards:crux_detail', args=[crux['slug']])
        for crux in CRUXES
    )
    paths.extend(
        reverse('westminster_standards:persona_detail', args=[persona['slug']])
        for persona in PERSONAS
    )
    paths.extend(
        reverse('westminster_standards:school_detail', args=[school['slug']])
        for school in SCHOOLS
    )
    paths.extend(
        reverse('westminster_standards:work_detail', args=[work['slug']])
        for work in WORKS
        if work['slug'] not in REDIRECTING_WORK_SLUGS
    )
    return paths
