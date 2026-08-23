"""Lookups over the ontology's positions, for linking and glossing.

Every one of the 117 positions in the ontology carries a written definition.
Until now nothing rendered them, so a reader met labels like
``Deliberately-Permits-Both`` with no way to find out what they meant short of
navigating to the value page and back. These indexes let any template gloss a
position where it stands, and link it.
"""

from django.urls import reverse

from .data import DIMENSIONS


def _build():
    by_keys, by_label = {}, {}
    for dimension in DIMENSIONS:
        for attribute in dimension['attributes']:
            for value in attribute['values']:
                entry = {
                    'dim_key': dimension['key'],
                    'dim_label': dimension['label'],
                    'attr_key': attribute['key'],
                    'attr_label': attribute['label'],
                    'value_key': value['key'],
                    'label': value['label'],
                    'definition': value.get('definition', ''),
                }
                by_keys[(dimension['key'], attribute['key'], value['key'])] = entry
                by_label[(dimension['key'], attribute['key'], value['label'])] = entry
    return by_keys, by_label


VALUE_BY_KEYS, VALUE_BY_LABEL = _build()

# Some labels are unique across the whole ontology, so a template holding only
# a label (the schools list, for instance) can still resolve one.
_label_counts = {}
for _entry in VALUE_BY_KEYS.values():
    _label_counts[_entry['label']] = _label_counts.get(_entry['label'], 0) + 1
UNIQUE_BY_LABEL = {
    entry['label']: entry
    for entry in VALUE_BY_KEYS.values()
    if _label_counts[entry['label']] == 1
}


def url_for(entry):
    return reverse('westminster_standards:value_detail', args=[
        entry['dim_key'], entry['attr_key'], entry['value_key'],
    ])


def lookup(dim_key=None, attr_key=None, value=None):
    """Resolve a position from whatever the caller happens to hold.

    Accepts a value key or a label; falls back to a label that is unique
    across the ontology when the dimension and attribute are not to hand.
    Returns None rather than guessing.
    """
    if not value:
        return None
    if dim_key and attr_key:
        entry = (
            VALUE_BY_KEYS.get((dim_key, attr_key, value))
            or VALUE_BY_LABEL.get((dim_key, attr_key, value))
        )
        if entry:
            return entry
    return UNIQUE_BY_LABEL.get(value)
