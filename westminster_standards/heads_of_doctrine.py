"""Heads of Doctrine — a fine-grained topical index of the Westminster Standards.

Where the eight-locus ontology (data.py) is an analytical grid for placing
personas and schools on a spectrum, the Heads of Doctrine are the
traditional Reformed systematic theology topics mapped to the specific
WCF sections, Larger Catechism questions, and Shorter Catechism questions
that address each topic.

Each 'head' has:

  - ``slug`` — URL-safe identifier
  - ``name`` — display name
  - ``description`` — 200-400 character overview of the doctrine
  - ``locus_key`` — which of the 8 ontology loci this falls under
  - ``attribute_keys`` — list of full ontology attribute keys (of the form
    ``locus_attr``, e.g. ``god_decree_extent_of_atonement``) that this head
    bears on. Every head carries at least one; heads treating doctrines the
    ontology does not adjudicate as a *contested* axis (creation,
    providence, adoption, the doctrine of God's essence, &c.) are mapped to
    the nearest representative attribute within their locus, so that the
    text they cover still receives an ontology tag.
  - ``wcf_sections`` — list of (chapter, section) tuples
  - ``wsc_questions`` — list of SC question numbers
  - ``wlc_questions`` — list of LC question numbers
  - ``related_crux_slugs`` — list of crux slugs bearing on this head

Because every WCF section and almost every catechism question is mapped to
at least one head, the heads serve as the bridge from the *text* of the
Standards to the *ontology*: a work-section's ontology tags are the union
of the ``attribute_keys`` of the heads that cover it (see
``attributes_for_wcf_section`` / ``attributes_for_catechism_question``).

There are ~39 heads, ordered by the internal logic of the Standards
themselves and grouped under the eight loci.
"""


HEADS_OF_DOCTRINE = []
_COUNTER = [0]


def _h(slug, name, description, *, locus_key, attribute_keys=None,
       wcf_sections=None, wsc_questions=None, wlc_questions=None,
       related_crux_slugs=None,
       dpw_sections=None, fpcg_sections=None, ssk_sections=None):
    _COUNTER[0] += 1
    HEADS_OF_DOCTRINE.append({
        'slug': slug,
        'number': _COUNTER[0],
        'name': name,
        'description': description,
        'locus_key': locus_key,
        'attribute_keys': attribute_keys or [],
        'wcf_sections': wcf_sections or [],
        'wsc_questions': wsc_questions or [],
        'wlc_questions': wlc_questions or [],
        'related_crux_slugs': related_crux_slugs or [],
        'dpw_sections': dpw_sections or [],
        'fpcg_sections': fpcg_sections or [],
        'ssk_sections': ssk_sections or [],
    })


def get_head_by_slug(slug):
    for h in HEADS_OF_DOCTRINE:
        if h['slug'] == slug:
            return h
    return None


def heads_by_locus(locus_key):
    return [h for h in HEADS_OF_DOCTRINE if h['locus_key'] == locus_key]


# Build reverse indexes lazily.
_WCF_SECTION_INDEX = None
_WSC_QUESTION_INDEX = None
_WLC_QUESTION_INDEX = None
_CRUX_INDEX = None


def heads_for_wcf_section(chapter, section):
    """Return list of heads that map to the given WCF (chapter, section)."""
    global _WCF_SECTION_INDEX
    if _WCF_SECTION_INDEX is None:
        idx = {}
        for h in HEADS_OF_DOCTRINE:
            for cs in h['wcf_sections']:
                idx.setdefault(tuple(cs), []).append(h)
        _WCF_SECTION_INDEX = idx
    return _WCF_SECTION_INDEX.get((chapter, section), [])


def heads_for_catechism_question(catechism_slug, number):
    """Return list of heads that map to the given catechism question."""
    global _WSC_QUESTION_INDEX, _WLC_QUESTION_INDEX
    if _WSC_QUESTION_INDEX is None:
        wsc_idx = {}
        wlc_idx = {}
        for h in HEADS_OF_DOCTRINE:
            for q in h['wsc_questions']:
                wsc_idx.setdefault(q, []).append(h)
            for q in h['wlc_questions']:
                wlc_idx.setdefault(q, []).append(h)
        _WSC_QUESTION_INDEX = wsc_idx
        _WLC_QUESTION_INDEX = wlc_idx
    if catechism_slug == 'wsc':
        return _WSC_QUESTION_INDEX.get(number, [])
    elif catechism_slug == 'wlc':
        return _WLC_QUESTION_INDEX.get(number, [])
    return []


def heads_for_crux(crux_slug):
    """Return list of heads that reference the given crux slug."""
    global _CRUX_INDEX
    if _CRUX_INDEX is None:
        idx = {}
        for h in HEADS_OF_DOCTRINE:
            for cs in h['related_crux_slugs']:
                idx.setdefault(cs, []).append(h)
        _CRUX_INDEX = idx
    return _CRUX_INDEX.get(crux_slug, [])


# ----------------------------------------------------------------------
# Ontology tags for work-sections.
#
# Every WCF section and almost every catechism question is mapped to one
# or more heads; each head carries the ontology ``attribute_keys`` it
# bears on. A section's ontology tags are therefore the *union* of the
# attribute keys of the heads that cover it, in head order, de-duplicated.
# Sections covered only by heads with no attribute mapping (creation,
# providence, adoption, &c.) come back empty — and that is faithful: not
# every paragraph of the Standards lands on a contested ontology axis.
# ----------------------------------------------------------------------

# Some heads treat a doctrine the ontology does not carve out as a *contested*
# axis (creation, providence, adoption, &c.). They are still tagged — with the
# nearest representative attribute within their locus — but that association is
# "representative", not "core". This set records the representative
# (head_slug, attribute_key) pairs so the UI can distinguish the two: the very
# same attribute is *core* under one head and *representative* under another
# (e.g. `order_of_decrees` is core for the-eternal-decree but representative
# for creation and providence).
_REPRESENTATIVE_ATTRS = {
    ('being-and-attributes-of-god', 'god_decree_trinity_processions'),
    ('creation', 'god_decree_order_of_decrees'),
    ('providence', 'god_decree_order_of_decrees'),
    ('adoption', 'soteriology_effectual_calling'),
    ('repentance', 'soteriology_saving_faith'),
    ('christian-liberty', 'law_sanctification_uses_of_the_law'),
    ('christian-liberty', 'ecclesiology_worship_regulative_principle'),
}


def is_representative(head_slug, attr_key):
    """True if this head bears on the attribute only by nearest-fit, because
    the ontology has no dedicated contested axis for the head's doctrine."""
    return (head_slug, attr_key) in _REPRESENTATIVE_ATTRS


def attribute_tags_for_heads(heads):
    """Ordered, de-duplicated ontology tags for the given heads.

    Each tag is a dict ``{'key', 'representative'}``. An attribute counts as
    *core* (``representative`` False) when at least one covering head treats
    it as a genuinely contested axis — core wins over representative."""
    order = []
    rep = {}
    for h in heads:
        for k in h.get('attribute_keys', []):
            r = is_representative(h['slug'], k)
            if k not in rep:
                order.append(k)
                rep[k] = r
            else:
                rep[k] = rep[k] and r   # any core occurrence wins
    return [{'key': k, 'representative': rep[k]} for k in order]


def attribute_keys_for_heads(heads):
    """Union of ``attribute_keys`` across the given heads, order-preserving."""
    return [t['key'] for t in attribute_tags_for_heads(heads)]


def attributes_for_wcf_section(chapter, section):
    """Full ontology attribute keys for a WCF (chapter, section)."""
    return attribute_keys_for_heads(heads_for_wcf_section(chapter, section))


def attributes_for_catechism_question(catechism_slug, number):
    """Full ontology attribute keys for a catechism question."""
    return attribute_keys_for_heads(
        heads_for_catechism_question(catechism_slug, number))


def attribute_tags_for_wcf_section(chapter, section):
    """Ontology tags (with core/representative flag) for a WCF section."""
    return attribute_tags_for_heads(heads_for_wcf_section(chapter, section))


def attribute_tags_for_catechism_question(catechism_slug, number):
    """Ontology tags (with core/representative flag) for a catechism question."""
    return attribute_tags_for_heads(
        heads_for_catechism_question(catechism_slug, number))


# ======================================================================
# I. SCRIPTURE
# ======================================================================

_h('prolegomena',
   'Prolegomena / The Nature of Theology',
   "The grounds and method of theological knowledge: why theology is "
   "necessary, how it differs from philosophy, and what role Scripture "
   "plays as the principium cognoscendi (the cognitive principle) of all "
   "doctrinal inquiry. The Shorter Catechism opens with the chief end of "
   "man; the Larger Catechism with the duty Scripture reveals.",
   locus_key='scripture',
   attribute_keys=['scripture_necessity', 'scripture_authority'],
   wcf_sections=[(1, 1)],
   wsc_questions=[1, 2, 3],
   wlc_questions=[1, 2, 3, 5],
   related_crux_slugs=['good-and-necessary-consequence'])

_h('revelation',
   'Revelation (General and Special)',
   "God's self-disclosure through the works of creation and providence "
   "(general revelation) and through his prophetic and apostolic Word "
   "(special revelation). WCF I.1 teaches that the light of nature is "
   "insufficient for salvation, making inscripturation necessary. The "
   "distinction grounds the Reformed insistence that saving knowledge "
   "comes only through the Word.",
   locus_key='scripture',
   attribute_keys=['scripture_necessity'],
   wcf_sections=[(1, 1), (1, 6)],
   wsc_questions=[2],
   wlc_questions=[2, 3],
   related_crux_slugs=[])

_h('doctrine-of-scripture',
   'The Doctrine of Scripture (Bibliology)',
   "The nature, canon, authority, sufficiency, perspicuity, and "
   "interpretation of the Bible. WCF I is the most fully developed "
   "Reformed confessional treatment of Scripture: ten sections covering "
   "inscripturation, the 66-book canon, the exclusion of the Apocrypha, "
   "the internal witness of the Spirit, the rule of interpretation "
   "(Scripture interprets Scripture), and the supremacy of the original "
   "languages.",
   locus_key='scripture',
   attribute_keys=['scripture_sufficiency', 'scripture_canon',
                   'scripture_authority', 'scripture_interpretation',
                   'scripture_necessity'],
   wcf_sections=[(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
                 (1, 7), (1, 8), (1, 9), (1, 10)],
   wsc_questions=[2, 3],
   wlc_questions=[2, 3, 4, 5],
   related_crux_slugs=['the-canon-and-the-apocrypha',
                       'good-and-necessary-consequence'])


# ======================================================================
# II. GOD & DECREE
# ======================================================================

_h('being-and-attributes-of-god',
   'The Being and Attributes of God',
   "Classical theism as confessed at Westminster: God is 'one only, "
   "living, and true God, who is infinite in being and perfection, a "
   "most pure spirit, invisible, without body, parts, or passions, "
   "immutable, immense, eternal, incomprehensible, almighty, most wise, "
   "most holy, most free, most absolute' (WCF II.1). The doctrine of "
   "divine simplicity and aseity underlie the entire confessional system.",
   locus_key='god_decree',
   attribute_keys=['god_decree_trinity_processions'],   # the doctrine of the one true God
   wcf_sections=[(2, 1), (2, 2)],
   wsc_questions=[4, 5],
   wlc_questions=[6, 7, 8],
   related_crux_slugs=[])

_h('the-trinity',
   'The Trinity',
   "One God in three persons: Father, Son, and Holy Spirit, the same in "
   "substance, equal in power and glory. The Son is eternally begotten "
   "of the Father; the Spirit eternally proceeds from the Father and "
   "the Son (the Western filioque). WCF II.3 is the Standards' "
   "Nicene-Chalcedonian Trinitarianism.",
   locus_key='god_decree',
   attribute_keys=['god_decree_trinity_processions'],
   wcf_sections=[(2, 3), (8, 2)],
   wsc_questions=[5, 6],
   wlc_questions=[8, 9, 10, 11],
   related_crux_slugs=[])

_h('the-eternal-decree',
   'The Eternal Decree',
   "God's eternal purpose, according to the counsel of his will, whereby "
   "he has foreordained whatsoever comes to pass. WCF III treats election "
   "and reprobation; the Assembly deliberately permitted both supra- and "
   "infralapsarian readings. The decree is unconditioned by foreseen "
   "creaturely action and is executed through providence.",
   locus_key='god_decree',
   attribute_keys=['god_decree_order_of_decrees', 'god_decree_reprobation'],
   wcf_sections=[(3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6),
                 (3, 7), (3, 8), (11, 4), (25, 1)],
   wsc_questions=[7, 8],
   wlc_questions=[12, 13, 14],
   related_crux_slugs=['the-order-of-the-decrees',
                       'the-extent-of-the-atonement',
                       'the-decree-of-reprobation'])

_h('creation',
   'Creation',
   "God made all things of nothing, by the word of his power, in the "
   "space of six days, and all very good. WCF IV.1-2 treats the creation "
   "of the world and the special creation of man in God's image with "
   "dominion over the creatures. The Shorter Catechism Q. 9-10 summarises "
   "the doctrine catechetically.",
   locus_key='god_decree',
   attribute_keys=['god_decree_order_of_decrees'],   # creation as first execution of the decree
   wcf_sections=[(4, 1), (4, 2), (9, 1)],
   wsc_questions=[9, 10],
   wlc_questions=[15, 16, 17],
   related_crux_slugs=[])

_h('providence',
   'Providence',
   "God's most holy, wise, and powerful preserving and governing all his "
   "creatures and all their actions. WCF V covers ordinary providence, "
   "the concourse of secondary causes, God's permission of sin, and the "
   "special providence toward the church. Providence is the execution in "
   "time of the eternal decree.",
   locus_key='god_decree',
   attribute_keys=['god_decree_order_of_decrees'],   # providence executes the eternal decree
   wcf_sections=[(5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7)],
   wsc_questions=[11],
   wlc_questions=[18, 19],
   related_crux_slugs=[])


# ======================================================================
# III. COVENANT
# ======================================================================

_h('fall-and-original-sin',
   'The Fall and Original Sin (Hamartiology)',
   "The fall of Adam and Eve, the imputation of Adam's first sin to all "
   "his posterity, and the corruption of the whole nature that followed. "
   "WCF VI treats the fall, the covenant headship of Adam, original sin, "
   "and the total depravity that extends to every part of man. The "
   "covenant of works provides the federal framework: in Adam all die.",
   locus_key='covenant',
   attribute_keys=['covenant_number_of_covenants'],
   wcf_sections=[(6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6),
                 (9, 3)],
   wsc_questions=[13, 14, 15, 16, 17, 18, 19],
   wlc_questions=[21, 22, 23, 24, 25, 26, 27, 28, 29],
   related_crux_slugs=[])

_h('covenant-of-works',
   'The Covenant of Works',
   "The first covenant made with man, in which life was promised to Adam "
   "and in him to his posterity upon condition of perfect and personal "
   "obedience. WCF VII.1-2 establishes the covenant of works as the "
   "framework for understanding the fall and the moral law's perpetual "
   "obligation on all persons.",
   locus_key='covenant',
   attribute_keys=['covenant_number_of_covenants'],
   wcf_sections=[(7, 1), (7, 2), (9, 2), (19, 1), (19, 6)],
   wsc_questions=[12],
   wlc_questions=[20, 30],
   related_crux_slugs=['the-mosaic-covenant'])

_h('covenant-of-grace',
   'The Covenant of Grace',
   "The second covenant, in which God freely offers unto sinners life "
   "and salvation by Jesus Christ, requiring of them faith in him. "
   "WCF VII.3-6 teaches that the covenant of grace is one in substance "
   "through both testaments, differently administered under the law "
   "and under the gospel. This is the structural hinge of the Standards' "
   "redemptive-historical theology.",
   locus_key='covenant',
   attribute_keys=['covenant_number_of_covenants',
                   'covenant_testamental_continuity',
                   'covenant_mosaic_covenant'],
   wcf_sections=[(7, 3), (7, 4), (7, 5), (7, 6), (17, 2), (27, 1), (28, 1)],
   wsc_questions=[20],
   wlc_questions=[30, 31, 32, 33, 34, 35],
   related_crux_slugs=['the-mosaic-covenant',
                       'the-children-of-believers'])

_h('covenant-of-redemption',
   'The Covenant of Redemption (Pactum Salutis)',
   "The eternal intra-Trinitarian covenant in which the Father appoints "
   "the Son as Mediator and the Son freely accepts the office for the "
   "elect. The Standards affirm its substance (WCF VIII.1; LC Q. 31) "
   "without the developed tri-covenantal apparatus of Cocceius or Witsius. "
   "The pactum salutis grounds the unity of the decree and the covenant.",
   locus_key='covenant',
   attribute_keys=['god_decree_covenant_of_redemption'],
   wcf_sections=[(8, 1)],
   wsc_questions=[],
   wlc_questions=[31],
   related_crux_slugs=['the-covenant-of-redemption'])


# ======================================================================
# IV. CHRISTOLOGY
# ======================================================================

_h('person-of-christ',
   'The Person of Christ (Christology Proper)',
   "Two whole, perfect, and distinct natures — Godhead and manhood — "
   "inseparably joined in one person, without conversion, composition, "
   "or confusion. WCF VIII.2 is the Standards' Chalcedonian statement. "
   "The Larger Catechism Q. 36-40 develops the incarnation and the "
   "personal union at length.",
   locus_key='christology',
   attribute_keys=['christology_natures'],
   wcf_sections=[(8, 2), (8, 3)],
   wsc_questions=[21, 22],
   wlc_questions=[36, 37, 38, 39, 40],
   related_crux_slugs=[])

_h('offices-of-christ',
   'The Offices of Christ (Prophet, Priest, King)',
   "Christ as the threefold Mediator: Prophet (revealing the will of God), "
   "Priest (offering himself a sacrifice and making continual "
   "intercession), and King (subduing, ruling, and defending his church). "
   "The three offices answer to the three deficiencies of fallen humanity: "
   "ignorance, guilt, and bondage.",
   locus_key='christology',
   attribute_keys=['christology_offices'],
   wcf_sections=[(8, 1), (8, 3)],
   wsc_questions=[23, 24, 25, 26],
   wlc_questions=[41, 42, 43, 44, 45],
   related_crux_slugs=[])

_h('states-of-christ',
   'The States of Christ (Humiliation and Exaltation)',
   "Christ's estate of humiliation (conception, birth, life, suffering, "
   "death, burial, continuance in the state of the dead) and his estate "
   "of exaltation (resurrection, ascension, session at the Father's "
   "right hand, return to judgment). The Larger Catechism Q. 46-56 "
   "develops this schema from Philippians 2.",
   locus_key='christology',
   attribute_keys=['christology_states_and_descent'],
   wcf_sections=[(8, 4)],
   wsc_questions=[27, 28],
   wlc_questions=[46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56],
   related_crux_slugs=['the-descent-into-hell'])

_h('the-atonement',
   'The Atonement',
   "Christ's perfect obedience and sacrifice of himself, by which he "
   "fully satisfied the justice of his Father and purchased reconciliation "
   "and an everlasting inheritance for all those whom the Father has "
   "given him. WCF VIII.5-8 treats both the accomplishment and the "
   "application of redemption; the Assembly's language accommodates both "
   "strict particularism and hypothetical universalism.",
   locus_key='christology',
   attribute_keys=['god_decree_extent_of_atonement',
                   'christology_active_obedience_imputation'],
   wcf_sections=[(8, 5), (8, 6), (8, 7), (8, 8)],
   wsc_questions=[21, 25],
   wlc_questions=[38, 39, 40, 44, 57, 58, 59],
   related_crux_slugs=['the-extent-of-the-atonement',
                       'active-obedience-imputation'])


# ======================================================================
# V. SOTERIOLOGY
# ======================================================================

_h('effectual-calling',
   'Effectual Calling',
   "The Spirit's work of enlightening the mind, renewing and effectually "
   "determining the will, so that the sinner comes to Christ most freely. "
   "WCF X distinguishes the effectual call (for the elect) from the "
   "outward call of the gospel (to all who hear). The Standards also "
   "address the salvation of elect infants dying in infancy (X.3).",
   locus_key='soteriology',
   attribute_keys=['soteriology_effectual_calling'],
   wcf_sections=[(8, 8), (9, 4), (10, 1), (10, 2), (10, 3), (10, 4)],
   wsc_questions=[29, 30, 31, 32],
   wlc_questions=[57, 58, 59, 60, 66, 67, 68, 69],
   related_crux_slugs=[])

_h('justification',
   'Justification',
   "A forensic act of God's free grace, in which he pardons all the sins "
   "of the justified and accepts their persons as righteous in his sight, "
   "not for anything wrought in them or done by them, but only for the "
   "perfect obedience and full satisfaction of Christ, by God imputed to "
   "them and received by faith alone. WCF XI is the heart of the "
   "Reformed soteriology.",
   locus_key='soteriology',
   attribute_keys=['soteriology_justification_ground',
                   'christology_active_obedience_imputation'],
   wcf_sections=[(11, 1), (11, 2), (11, 3), (11, 4), (11, 5), (11, 6), (14, 2)],
   wsc_questions=[33],
   wlc_questions=[70, 71, 72, 73],
   related_crux_slugs=['justification-and-the-antinomian-crisis',
                       'active-obedience-imputation'])

_h('adoption',
   'Adoption',
   "An act of God's free grace, by which all those who are justified are "
   "received into the number of his children, have his name put upon "
   "them, receive the Spirit of adoption, have access to the throne of "
   "grace with boldness, and are entitled to the privileges of the "
   "children of God. WCF XII is a single, densely packed section.",
   locus_key='soteriology',
   attribute_keys=['soteriology_effectual_calling'],   # adoption, a benefit of applied redemption
   wcf_sections=[(12, 1)],
   wsc_questions=[34],
   wlc_questions=[74],
   related_crux_slugs=[])

_h('sanctification',
   'Sanctification',
   "The work of God's free grace, by which the whole man is renewed "
   "after the image of God and is enabled more and more to die unto "
   "sin and live unto righteousness. WCF XIII teaches that sanctification "
   "is imperfect in this life: remainders of corruption abide in every "
   "part, producing a continual war between flesh and spirit.",
   locus_key='soteriology',
   attribute_keys=['law_sanctification_good_works'],
   wcf_sections=[(13, 1), (13, 2), (13, 3)],
   wsc_questions=[35, 36],
   wlc_questions=[75, 77, 78],
   related_crux_slugs=[])

_h('saving-faith',
   'Saving Faith',
   "The grace of faith, by which the elect are enabled to believe to "
   "the saving of their souls, is the work of the Spirit in their hearts "
   "and is ordinarily wrought by the ministry of the Word. By faith a "
   "Christian receives and rests upon Christ alone for justification, "
   "sanctification, and eternal life (WCF XIV).",
   locus_key='soteriology',
   attribute_keys=['soteriology_saving_faith'],
   wcf_sections=[(11, 2), (14, 1), (14, 2), (14, 3)],
   wsc_questions=[85, 86],
   wlc_questions=[72, 73, 153],
   related_crux_slugs=[])

_h('repentance',
   'Repentance',
   "An evangelical grace wrought in the heart of a sinner by the Spirit "
   "and the Word, by which he is made sensible of his sin and misery and "
   "apprehends the mercy of God in Christ, grieves for and hates his "
   "sins, and turns from them unto God with full purpose of and endeavour "
   "after new obedience (WCF XV).",
   locus_key='soteriology',
   attribute_keys=['soteriology_saving_faith'],   # repentance, the twin grace of conversion
   wcf_sections=[(15, 1), (15, 2), (15, 3), (15, 4), (15, 5), (15, 6)],
   wsc_questions=[87],
   wlc_questions=[76],
   related_crux_slugs=['justification-and-the-antinomian-crisis'])

_h('good-works',
   'Good Works',
   "Only such works as God has commanded in his holy Word, proceeding "
   "from a heart purified by faith, are properly good works. They are "
   "the fruits and evidences of a true and lively faith; they cannot "
   "make satisfaction for sin or merit pardon, but are accepted in "
   "Christ (WCF XVI). The Standards thread carefully between Rome and "
   "antinomianism.",
   locus_key='soteriology',
   attribute_keys=['law_sanctification_good_works'],
   wcf_sections=[(16, 1), (16, 2), (16, 3), (16, 4), (16, 5),
                 (16, 6), (16, 7)],
   wsc_questions=[],
   wlc_questions=[78],
   related_crux_slugs=['justification-and-the-antinomian-crisis'])

_h('perseverance-of-the-saints',
   'Perseverance of the Saints',
   "Those whom God has accepted in his Beloved, effectually called and "
   "sanctified by his Spirit, can neither totally nor finally fall away "
   "from the state of grace, but shall certainly persevere therein to "
   "the end and be eternally saved. Perseverance is grounded in God's "
   "decree, Christ's merit, and the Spirit's indwelling (WCF XVII).",
   locus_key='soteriology',
   attribute_keys=['soteriology_perseverance'],
   wcf_sections=[(17, 1), (17, 2), (17, 3)],
   wsc_questions=[36],
   wlc_questions=[79],
   related_crux_slugs=['perseverance-of-the-saints'])

_h('assurance-of-grace',
   'Assurance of Grace',
   "An infallible assurance of salvation is attainable in this life "
   "through the divine promises, the inward evidences of grace, and "
   "the testimony of the Spirit of adoption. Yet assurance does not "
   "belong to the essence of saving faith: a true believer may wait "
   "long and conflict with many difficulties before attaining it "
   "(WCF XVIII).",
   locus_key='soteriology',
   attribute_keys=['soteriology_assurance'],
   wcf_sections=[(14, 3), (18, 1), (18, 2), (18, 3), (18, 4)],
   wsc_questions=[36],
   wlc_questions=[80, 81],
   related_crux_slugs=['assurance-of-the-essence-of-faith'])


# ======================================================================
# VI. LAW & SANCTIFICATION
# ======================================================================

_h('moral-law-and-decalogue',
   'The Moral Law and the Decalogue',
   "God gave to Adam a law as a covenant of works, and afterward "
   "delivered the same upon Mount Sinai in ten commandments. The moral "
   "law forever binds all persons to obedience. WCF XIX establishes "
   "the tripartite division (moral, judicial, ceremonial) and the "
   "perpetual obligation of the moral law. The Larger Catechism's "
   "Q. 91-148 exposition of the Decalogue is the Standards' longest "
   "single section.",
   locus_key='law_sanctification',
   attribute_keys=['law_sanctification_uses_of_the_law',
                   'law_sanctification_tripartite_division'],
   wcf_sections=[(19, 1), (19, 2), (19, 3), (19, 4), (19, 5),
                 (19, 6), (19, 7)],
   wsc_questions=[39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
                  52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
                  65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77,
                  78, 79, 80, 81, 82, 83, 84],
   wlc_questions=list(range(91, 153)),
   related_crux_slugs=['the-third-use-of-the-law',
                       'the-tripartite-division-of-the-law',
                       'justification-and-the-antinomian-crisis'])

_h('christian-liberty',
   'Christian Liberty and Liberty of Conscience',
   "The liberty which Christ has purchased for believers under the "
   "gospel consists in freedom from the guilt of sin, the condemning "
   "wrath of God, the curse of the moral law, the dominion of sin, "
   "and freedom to approach God with boldness (WCF XX). God alone is "
   "lord of the conscience; doctrines and commandments of men contrary "
   "to or beside the Word are a betrayal of this liberty.",
   locus_key='law_sanctification',
   attribute_keys=['law_sanctification_uses_of_the_law',
                   'ecclesiology_worship_regulative_principle'],
   wcf_sections=[(20, 1), (20, 2), (20, 3), (20, 4)],
   wsc_questions=[],
   wlc_questions=[],
   related_crux_slugs=[])

_h('religious-worship-and-sabbath',
   'Religious Worship and the Sabbath',
   "The acceptable way of worshipping the true God is instituted by "
   "himself and limited by his revealed will (the regulative principle, "
   "WCF XXI.1). Worship includes prayer, the reading and preaching "
   "of the Word, the administration of the sacraments, singing of "
   "psalms, religious oaths, and the keeping of the Lord's Day. "
   "WCF XXI.7-8 codifies the strict Sabbatarian position: one day "
   "in seven, changed to the first day from the resurrection.",
   locus_key='law_sanctification',
   attribute_keys=['law_sanctification_sabbath',
                   'ecclesiology_worship_regulative_principle'],
   wcf_sections=[(21, 1), (21, 2), (21, 3), (21, 4), (21, 5),
                 (21, 6), (21, 7), (21, 8)],
   wsc_questions=[45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                  57, 58, 59, 60, 61, 62, 88, 89, 90],
   wlc_questions=[108, 109, 110, 111, 112, 113, 114, 115, 116, 117,
                  118, 119, 120, 121, 154, 155, 156, 157, 158, 159, 160],
   related_crux_slugs=['the-regulative-principle', 'the-strict-sabbath',
                       'the-rouse-psalter'])

_h('lawful-oaths-and-vows',
   'Lawful Oaths and Vows',
   "A lawful oath is a part of religious worship in which the person "
   "swearing solemnly calls God to witness what he asserts or promises "
   "and to judge him if he swears falsely or breaks his engagement "
   "(WCF XXII). Vows are of the like nature with promissory oaths "
   "and are to be made to God alone, in matters within the vower's "
   "power and liberty.",
   locus_key='law_sanctification',
   attribute_keys=['civil_last_things_lawful_oaths_and_marriage'],
   wcf_sections=[(22, 1), (22, 2), (22, 3), (22, 4), (22, 5),
                 (22, 6), (22, 7)],
   wsc_questions=[],
   wlc_questions=[],
   related_crux_slugs=['lawful-oaths-and-the-quaker-question'])


# ======================================================================
# VII. ECCLESIOLOGY & WORSHIP
# ======================================================================

_h('the-church',
   'The Church (Visible and Invisible)',
   "The catholic church consists of the whole number of the elect. The "
   "visible church consists of all those throughout the world who profess "
   "the true religion, together with their children. Outside the visible "
   "church there is no ordinary possibility of salvation. WCF XXV-XXVI "
   "treats the invisible-visible distinction and the communion of saints.",
   locus_key='ecclesiology_worship',
   attribute_keys=['ecclesiology_worship_polity'],
   wcf_sections=[(25, 1), (25, 2), (25, 3), (25, 4), (25, 5), (25, 6),
                 (26, 1), (26, 2), (26, 3)],
   wsc_questions=[],
   wlc_questions=[61, 62, 63, 64, 65],
   related_crux_slugs=['the-grand-debate-polity',
                       'the-pope-as-antichrist'])

_h('the-sacraments-general',
   'The Sacraments (General)',
   "Sacraments are holy signs and seals of the covenant of grace, "
   "immediately instituted by God, to represent Christ and his benefits "
   "and to confirm our interest in him. They put a visible difference "
   "between the church and the rest of the world. The grace exhibited "
   "in or by the sacraments is conferred by the Spirit upon worthy "
   "receivers (WCF XXVII).",
   locus_key='ecclesiology_worship',
   attribute_keys=['ecclesiology_worship_sacraments_efficacy'],
   wcf_sections=[(7, 6), (27, 1), (27, 2), (27, 3), (27, 4), (27, 5)],
   wsc_questions=[91, 92, 93],
   wlc_questions=[161, 162, 163, 164],
   related_crux_slugs=['sacramental-efficacy'])

_h('baptism',
   'Baptism',
   "A sacrament of the New Testament, ordained by Jesus Christ, as a "
   "sign and seal of the covenant of grace. Not only those who profess "
   "faith but also the infants of one or both believing parents are to "
   "be baptized (WCF XXVIII). Dipping is not necessary; pouring or "
   "sprinkling suffices. The efficacy of baptism is not tied to the "
   "moment of administration.",
   locus_key='ecclesiology_worship',
   attribute_keys=['ecclesiology_worship_sacraments_efficacy',
                   'covenant_children_of_believers'],
   wcf_sections=[(28, 1), (28, 2), (28, 3), (28, 4), (28, 5),
                 (28, 6), (28, 7)],
   wsc_questions=[94, 95],
   wlc_questions=[165, 166, 167],
   related_crux_slugs=['the-children-of-believers',
                       'sacramental-efficacy'])

_h('the-lords-supper',
   'The Lord\'s Supper',
   "A sacrament in which Christ's death is shown forth and the worthy "
   "receivers are made partakers of his body and blood, with all his "
   "benefits, to their spiritual nourishment and growth in grace. "
   "WCF XXIX rejects the Roman transubstantiation, the sacrifice "
   "of the mass, and the withholding of the cup from the laity.",
   locus_key='ecclesiology_worship',
   attribute_keys=['ecclesiology_worship_sacraments_efficacy'],
   wcf_sections=[(29, 1), (29, 2), (29, 3), (29, 4), (29, 5),
                 (29, 6), (29, 7), (29, 8)],
   wsc_questions=[96, 97],
   wlc_questions=[168, 169, 170, 171, 172, 173, 174, 175, 176, 177],
   related_crux_slugs=['sacramental-efficacy'])

_h('prayer-and-the-lords-prayer',
   "Prayer and the Lord's Prayer",
   "Prayer is an offering up of our desires unto God, in the name of "
   "Christ, by the help of his Spirit, with confession of our sins and "
   "thankful acknowledgement of his mercies. The Standards treat prayer "
   "as a chief part of religious worship (WCF XXI.3-4), required of all "
   "and to be made in a known tongue; the Larger and Shorter Catechisms "
   "close with an extended exposition of the Lord's Prayer as the rule "
   "and pattern of prayer. The Directory's free pastoral prayer, in place "
   "of the Prayer Book's prescribed forms, is the regulative principle "
   "applied to prayer.",
   locus_key='ecclesiology_worship',
   attribute_keys=['ecclesiology_worship_regulative_principle'],
   wcf_sections=[(21, 3), (21, 4)],
   wsc_questions=list(range(98, 108)),
   wlc_questions=list(range(178, 197)),
   related_crux_slugs=['the-regulative-principle'])

_h('church-government-and-discipline',
   'Church Government and Discipline',
   "The Lord Jesus, as King and Head of his Church, has appointed a "
   "government in the hand of church officers distinct from the civil "
   "magistrate. WCF XXX-XXXI treats church censures (admonition, "
   "suspension, excommunication) and synods and councils as a "
   "regulative ordinance of Christ for the better government of the "
   "church.",
   locus_key='ecclesiology_worship',
   attribute_keys=['ecclesiology_worship_polity',
                   'ecclesiology_worship_censures_and_synods'],
   wcf_sections=[(30, 1), (30, 2), (30, 3), (30, 4),
                 (31, 1), (31, 2), (31, 3), (31, 4), (31, 5)],
   wsc_questions=[],
   wlc_questions=[],
   related_crux_slugs=['the-grand-debate-polity',
                       'the-erastian-question'])


# ======================================================================
# VIII. CIVIL & LAST THINGS
# ======================================================================

_h('the-civil-magistrate',
   'The Civil Magistrate',
   "God, the supreme Lord and King of all the world, has ordained civil "
   "magistrates to be under him over the people for his own glory and "
   "the public good. WCF XXIII treats the magistrate's authority, "
   "the duty of subjects, and the contested question of the magistrate's "
   "role toward the church (the 1646 text vs the 1788 American revision).",
   locus_key='civil_last_things',
   attribute_keys=['civil_last_things_magistrate_role'],
   wcf_sections=[(20, 4), (23, 1), (23, 2), (23, 3), (23, 4), (30, 1)],
   wsc_questions=[64, 65, 66],
   wlc_questions=[124, 127, 128, 129, 130, 131, 132, 133],
   related_crux_slugs=['the-magistrates-two-tables',
                       'the-1788-american-revision',
                       'the-solemn-league-and-covenant'])

_h('marriage-and-divorce',
   'Marriage and Divorce',
   "Marriage is between one man and one woman, designed for their mutual "
   "help, the increase of mankind, and the prevention of uncleanness "
   "(WCF XXIV). The Standards limit lawful divorce to two grounds: "
   "adultery and wilful desertion. Mixed marriages with infidels, "
   "Papists, and the ungodly are cautioned against.",
   locus_key='civil_last_things',
   attribute_keys=['civil_last_things_lawful_oaths_and_marriage'],
   wcf_sections=[(24, 1), (24, 2), (24, 3), (24, 4), (24, 5), (24, 6)],
   wsc_questions=[70, 71, 72],
   wlc_questions=[137, 138, 139],
   related_crux_slugs=['grounds-of-divorce'])

_h('death-and-intermediate-state',
   'Death and the Intermediate State',
   "The bodies of men after death return to dust and see corruption, "
   "but their souls, which neither die nor sleep, having an immortal "
   "subsistence, immediately return to God who gave them. The souls "
   "of the righteous are received into the highest heavens; the souls "
   "of the wicked are cast into hell (WCF XXXII). This is the "
   "Standards' rejection of soul-sleep and purgatory.",
   locus_key='civil_last_things',
   attribute_keys=['civil_last_things_intermediate_state'],
   wcf_sections=[(32, 1), (32, 2), (32, 3)],
   wsc_questions=[37],
   wlc_questions=[82, 83, 84, 85, 86],
   related_crux_slugs=['the-conscious-intermediate-state'])

_h('resurrection-and-final-judgment',
   'The Resurrection and Final Judgment',
   "At the last day the bodies of all the dead shall be raised up with "
   "the self-same bodies and none other, though with different qualities, "
   "and shall be united again to their souls forever. God has appointed "
   "a day wherein he will judge the world in righteousness by Jesus "
   "Christ (WCF XXXII-XXXIII). The Standards do not adopt a millennial "
   "scheme but teach a single universal judgment.",
   locus_key='civil_last_things',
   attribute_keys=['civil_last_things_final_judgment'],
   wcf_sections=[(9, 5), (32, 2), (32, 3), (33, 1), (33, 2), (33, 3)],
   wsc_questions=[38],
   wlc_questions=[86, 87, 88, 89, 90],
   related_crux_slugs=['the-final-judgment'])


# ======================================================================
# DIRECTORY-WORK SECTION MAPPINGS
#
# Applied after all _h() calls. Each mapping is a precise editorial
# assignment of specific DPW/FPCG/SSK sections to specific heads —
# not a broad locus-based match.
# ======================================================================

_DIR_MAPPINGS = {
    # Scripture heads
    'doctrine-of-scripture': {'dpw_sections': [2]},
    'revelation': {'dpw_sections': [2]},

    # Covenant heads
    'covenant-of-works': {'ssk_sections': [1]},
    'covenant-of-grace': {'ssk_sections': [2, 3]},
    'covenant-of-redemption': {'ssk_sections': [2]},
    'fall-and-original-sin': {'ssk_sections': [1]},

    # Christology heads
    'offices-of-christ': {'ssk_sections': [2]},
    'the-atonement': {'ssk_sections': [2]},

    # Soteriology heads
    'effectual-calling': {'ssk_sections': [4]},
    'justification': {'ssk_sections': [4, 6]},
    'adoption': {'ssk_sections': [4]},
    'sanctification': {'ssk_sections': [4, 12]},
    'saving-faith': {'ssk_sections': [4, 7, 8, 9, 10, 13, 14]},
    'repentance': {'ssk_sections': [4, 5]},
    'good-works': {'ssk_sections': [12]},
    'perseverance-of-the-saints': {'ssk_sections': [4]},
    'assurance-of-grace': {'ssk_sections': [10, 14]},

    # Law & sanctification heads
    'moral-law-and-decalogue': {'dpw_sections': [8], 'ssk_sections': [5, 11]},
    'religious-worship-and-sabbath': {'dpw_sections': [1, 3, 4, 5, 8, 12, 13, 14, 15]},
    'christian-liberty': {'dpw_sections': [15]},

    # Ecclesiology heads
    'the-church': {
        'dpw_sections': [1],
        'fpcg_sections': [1, 2, 3, 8, 9, 10],
        'ssk_sections': [3],
    },
    'the-sacraments-general': {
        'dpw_sections': [6, 7],
        'fpcg_sections': [10],
    },
    'baptism': {'dpw_sections': [6]},
    'the-lords-supper': {'dpw_sections': [7]},
    'prayer-and-the-lords-prayer': {'dpw_sections': [3, 5]},
    'church-government-and-discipline': {
        'fpcg_sections': [3, 4, 5, 6, 7, 11, 12, 13, 14, 15, 16, 17, 18, 19],
    },

    # Civil & last things heads
    'marriage-and-divorce': {'dpw_sections': [9]},
    'death-and-intermediate-state': {'dpw_sections': [10, 11]},
}

for _slug, _refs in _DIR_MAPPINGS.items():
    _head = get_head_by_slug(_slug)
    if _head:
        for key in ('dpw_sections', 'fpcg_sections', 'ssk_sections'):
            if key in _refs:
                _head[key] = _refs[key]
