"""Westminster cases — Assembly votes, drafting decisions, and after-cases.

Mirrors `puritans/cases.py` in shape. Candidate cases include the
key Assembly votes (the Grand Debate divisions, the active-obedience
vote, the Calamy-Rutherford atonement debate, the Sabbath votes, the
magistrate clause), and the major post-Assembly reception cases
(Solemn League's lapse, 1662 Great Ejection, Halfway Covenant in
New England — though that is a Cambridge-Platform case — the 1788
American revision, the 1843 Disruption, the 1879 PCUS Declaratory
Statement, the 1903 PCUSA revisions, the 1947 OPC affirmation of
the 1647 text).

This file is intentionally stubbed at scaffold time.
"""


CASES = []


def get_case_by_slug(slug):
    for c in CASES:
        if c.get('slug') == slug:
            return c
    return None


def cases_grouped_by_category():
    return []


def shared_responders(case):
    return []
