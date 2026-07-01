"""Westminster controversies — the Assembly's major debates and after.

Mirrors `puritans/controversies.py` in shape. Candidate controversies
include: jure-divino presbyterianism vs Independency (the Grand Debate
of 1644-46); Erastianism (Selden/Lightfoot vs Gillespie); the extent
of the atonement (Calamy vs Rutherford, January 1646); the imputation
of active obedience (1645); the supra/infra question (Twisse vs the
English majority); the magistrate and toleration (1647); the
Apocrypha (1645); the Sabbath (1645-46); the descendit ad inferna
(LC 50); and the post-Assembly controversies — Marrow (1717), Auchterarder
Creed (1717), and the American 1788 revision.

This file is intentionally stubbed at scaffold time.
"""


CONTROVERSIES = []


def get_controversy_by_slug(slug):
    for c in CONTROVERSIES:
        if c.get('slug') == slug:
            return c
    return None


def shared_parties(controversy):
    return []


def shared_allied_schools(controversy):
    return []
