"""Westminster Standards — ontology of the Westminster theological landscape.

This module mirrors the role of `puritans/data.py` (and `core/data.py`),
but its eight loci are shaped to the Westminster Standards specifically:
the Confession of Faith (1646), the Larger Catechism (1647), and the
Shorter Catechism (1647), together with their two service-books, the
Directory for Public Worship (1645) and the Form of Presbyterial
Church Government (1645).

The Westminster Standards are not one position among many — they are a
*confessional consensus* that the Westminster Assembly hammered out from
mid-1643 to early 1649 over more than a thousand sessions. The ontology
below therefore differs from the wider Puritan ontology in three ways:

  1. The loci are organised by the *internal* shape of the Standards
     themselves — Scripture first (WCF I), God and decree (WCF II–V),
     covenant and Christ (WCF VII–VIII), the *ordo salutis* (WCF
     X–XVIII), law and sanctification (WCF XIX–XXII), polity and
     worship (WCF XXV–XXXI), civil and last things (WCF XXIII–XXIV,
     XXXII–XXXIII).
  2. The contested positions inside each attribute are read off the
     Westminster *debates* themselves — supra- vs infralapsarianism,
     particular vs hypothetical-universal atonement, jure divino
     presbyterianism vs Independency vs Erastianism, strict vs moderate
     regulative principle, papal-antichrist vs reserved, and so on.
     Where the Standards *deliberately* refuse to adjudicate (as on the
     order of the decrees), that is marked explicitly.
  3. The default `attrs` for a Westminster-confessional persona/work
     are the Standards' own positions; deviations from the Standards
     (Independency among the Dissenting Brethren, Erastianism among
     Selden and Lightfoot, hypothetical universalism among Calamy,
     Vines and Seaman) are marked as overrides on the relevant
     attribute.

The eight loci:

    I.    Scripture           — sufficiency, canon, authority,
                                interpretation, necessity
    II.   God & Decree        — Trinity, decree-order, atonement,
                                reprobation, pactum salutis
    III.  Covenant            — number of covenants, Mosaic,
                                children, testamental continuity
    IV.   Christology         — natures, offices, states & descent,
                                imputation of active obedience
    V.    Soteriology         — calling, justification, faith,
                                perseverance, assurance
    VI.   Law & Sanctification— uses, tripartite division, Sabbath,
                                good works
    VII.  Ecclesiology &      — polity, sacramental efficacy,
          Worship               regulative principle, censures & synods
    VIII. Civil & Last Things — magistrate, oaths & marriage,
                                intermediate state, final judgment

Each locus has 4-5 attributes; 35 attributes in all, matching the
Puritan ontology's shape so that the downstream machinery (the
value-detail page, dimension intersections, school/persona placement)
can be reused as is.
"""


DIMENSIONS = [
    # ==================================================================
    # I. SCRIPTURE
    # ==================================================================
    {
        'key': 'scripture',
        'label': 'Scripture',
        'numeral': 'I',
        'color': 'scripture',
        'icon': '✦',
        'tagline': "Sola scriptura — the rule of faith and life",
        'prose': {
            'overview': (
                "The Westminster Standards begin not with God but with Scripture (WCF "
                "I), and the order is deliberate. The Confession's opening chapter is "
                "the most fully developed Reformed treatment of Scripture in any "
                "confessional document of the seventeenth century: ten paragraphs "
                "covering the necessity of Scripture in the noetic condition of fallen "
                "humanity, the inscripturation of the prophetic and apostolic word, "
                "the canon of 66 books, the rejection of the Apocrypha as non-canonical, "
                "the church's testimony as historically valuable but not foundational, "
                "the internal witness of the Holy Spirit as the persuasive ground of "
                "saving conviction, the sufficiency of Scripture for the whole counsel "
                "of God 'either expressly set down in Scripture, or by good and "
                "necessary consequence,' the perspicuity of Scripture in things "
                "necessary for salvation, the authority of the original Hebrew and "
                "Greek, the necessity of vernacular translation, and finally the "
                "supremacy of Scripture over all other authorities."
            ),
            'philosophical_significance': (
                "The Westminster doctrine of Scripture stakes a precise position in "
                "the early modern controversies over religious epistemology. Against "
                "Tridentine Catholicism it denies parity between Scripture and "
                "tradition; against the radical spiritualists it denies that the "
                "Spirit speaks apart from the Word; against Rationalism (already "
                "emergent in Herbert of Cherbury) it denies that natural religion "
                "suffices. The phrase 'good and necessary consequence' (I.6) is a "
                "carefully reasoned warrant for confessional system-building — the "
                "Standards' Trinitarianism, paedobaptism, and Sabbatarianism all "
                "rest on it. The internal-witness clause (I.5) is the Standards' "
                "answer to the Cartesian problem of certainty: the believer's "
                "assurance of Scripture's authority rests on the testimony of the "
                "Spirit *with and by* the Word, not on the church and not on bare "
                "reason."
            ),
            'scriptural_perspective': (
                "The Confession proof-texts WCF I from 2 Timothy 3:15–17, 2 Peter "
                "1:19–21, Hebrews 1:1–2, John 5:39, Isaiah 8:20, 1 Corinthians "
                "2:9–14, and Galatians 1:8–9, with extensive supporting catenae. "
                "The Larger Catechism Q. 3–5 expounds the same doctrine "
                "catechetically, defining Scripture as 'the Word of God, the only "
                "rule of faith and obedience'; Shorter Catechism Q. 2 — 'The Word "
                "of God, which is contained in the Scriptures of the Old and New "
                "Testaments' — is the most compressed statement."
            ),
            'key_controversies': [
                {
                    'title': 'Scripture vs Tradition (Trent)',
                    'body': (
                        "Trent's fourth session (1546) had decreed that Scripture and "
                        "unwritten apostolic traditions are received 'pari pietatis "
                        "affectu' (with equal pious affection). WCF I.6 directly "
                        "rejects this: 'The whole counsel of God concerning all things "
                        "necessary for his own glory, man's salvation, faith, and life, "
                        "is either expressly set down in Scripture, or by good and "
                        "necessary consequence may be deduced from Scripture: unto "
                        "which nothing at any time is to be added, whether by new "
                        "revelations of the Spirit, or traditions of men.'"
                    ),
                },
                {
                    'title': 'Scripture and the Spirit (the radicals)',
                    'body': (
                        "Familists, Seekers, Ranters, and early Quakers (Fox began "
                        "preaching in 1647, the year the Catechisms were finished) "
                        "all elevated immediate Spirit-illumination above the written "
                        "Word. The Standards' careful pairing of Word and Spirit — "
                        "the Spirit *with and by* the Word — was the Assembly's "
                        "considered response, hammered out against both Catholic and "
                        "radical alternatives."
                    ),
                },
                {
                    'title': 'The Apocrypha',
                    'body': (
                        "WCF I.3 explicitly excludes the Apocrypha from the canon: "
                        "'not being of divine inspiration, are no part of the canon "
                        "of Scripture; and therefore are of no authority in the "
                        "Church of God, nor to be any otherwise approved, or made "
                        "use of, than other human writings.' This was a sharper "
                        "rejection than Article VI of the Thirty-Nine Articles, "
                        "which permitted Apocryphal reading 'for example of life "
                        "and instruction of manners' though not for doctrine."
                    ),
                },
            ],
        },
        'attributes': [
            {
                'key': 'sufficiency',
                'label': 'Sufficiency',
                'values': [
                    {'key': 'express_and_consequence', 'label': 'Express-And-Good-Consequence',
                     'definition': "Whatever is necessary for God's glory and human salvation is either expressly stated in Scripture, or may be deduced from it by good and necessary consequence (WCF I.6)."},
                    {'key': 'express_only', 'label': 'Express-Statements-Only',
                     'definition': "Only what is expressly stated in Scripture binds the conscience; rejects deduction by good and necessary consequence — a Socinian and later Anabaptist tendency."},
                    {'key': 'scripture_plus_tradition', 'label': 'Scripture-And-Tradition',
                     'definition': "Scripture is sufficient only when supplemented by the unwritten apostolic tradition preserved in the church — the Tridentine position rejected by WCF I.6."},
                ],
            },
            {
                'key': 'canon',
                'label': 'Canon',
                'values': [
                    {'key': 'sixty_six', 'label': '66-Book-Protestant-Canon',
                     'definition': "The 39 books of the Old Testament and 27 of the New, enumerated in WCF I.2; the Apocrypha is explicitly excluded (I.3)."},
                    {'key': 'with_apocrypha', 'label': 'With-Apocrypha',
                     'definition': "Includes the Apocryphal books as canonical (Trent) or as 'second canon' useful for instruction (some Anglican readings of Article VI)."},
                    {'key': 'reduced', 'label': 'Reduced-Canon',
                     'definition': "Excludes some New Testament books (Hebrews, James, Revelation in Luther's reservations; or further reductions in radical groups)."},
                ],
            },
            {
                'key': 'authority',
                'label': 'Authority',
                'values': [
                    {'key': 'self_authenticating_with_spirit', 'label': 'Self-Authenticating-With-Internal-Witness',
                     'definition': "Scripture's authority is grounded in God its author and is sealed to the believer's heart by the inward work of the Holy Spirit bearing witness *with and by* the Word (WCF I.4–5)."},
                    {'key': 'church_bestowed', 'label': 'Church-Bestowed',
                     'definition': "Scripture's authority depends on the church's reception and definition — the Tridentine and high-mediaeval position."},
                    {'key': 'private_spirit', 'label': 'Immediate-Spirit-Only',
                     'definition': "Scripture's authority is subordinate to the immediate witness of the Spirit in the believer apart from the written Word — the radical-spiritualist position."},
                    {'key': 'rationalist', 'label': 'Rationally-Demonstrated',
                     'definition': "Scripture's authority must be established by external rational proofs alone — the early-modern rationalist tendency the Confession resists."},
                ],
            },
            {
                'key': 'interpretation',
                'label': 'Interpretation',
                'values': [
                    {'key': 'analogia_scripturae', 'label': 'Scripture-Interprets-Scripture',
                     'definition': "The infallible rule of interpretation is Scripture itself: when there is a question about the true sense of any passage, it must be searched and known by other places that speak more clearly (WCF I.9)."},
                    {'key': 'church_magisterium', 'label': 'Church-Magisterium',
                     'definition': "Authoritative interpretation belongs to the church's teaching office — the Roman position rejected by WCF I.10."},
                    {'key': 'private_spirit', 'label': 'Private-Spirit',
                     'definition': "Each believer's immediate Spirit-illumination decides the meaning of Scripture without ecclesial regulation — the radical position."},
                    {'key': 'critical_reason', 'label': 'Critical-Reason',
                     'definition': "Scripture is interpreted under the rule of autonomous human reason — the rationalist tendency."},
                ],
            },
            {
                'key': 'necessity',
                'label': 'Necessity',
                'values': [
                    {'key': 'necessary_post_fall', 'label': 'Necessary-After-The-Fall',
                     'definition': "Although the light of nature and the works of creation manifest God's goodness, wisdom, and power, they are not sufficient to give the knowledge of God and his will necessary for salvation; therefore the Lord committed his revelation wholly unto writing (WCF I.1)."},
                    {'key': 'merely_useful', 'label': 'Merely-Useful',
                     'definition': "Natural revelation suffices for salvation; Scripture is helpful but not strictly necessary — an Arminian-rationalist tendency rejected by the Confession."},
                    {'key': 'unnecessary', 'label': 'Unnecessary',
                     'definition': "The inner light alone suffices; Scripture is an aid, not a necessity — the position of the most radical spiritualists."},
                ],
            },
        ],
    },

    # ==================================================================
    # II. GOD & DECREE
    # ==================================================================
    {
        'key': 'god_decree',
        'label': 'God & Decree',
        'numeral': 'II',
        'color': 'god_decree',
        'icon': '✠',
        'tagline': "The triune God and his eternal counsel",
        'prose': {
            'overview': (
                "WCF II–V is the Standards' theology proper: God's being and "
                "attributes (II), the Trinity (II.3), the eternal decree (III), "
                "creation (IV), and providence (V). The doctrine of God is "
                "classical: 'one only, living, and true God, who is infinite in "
                "being and perfection, a most pure spirit, invisible, without "
                "body, parts, or passions, immutable, immense, eternal, "
                "incomprehensible, almighty, most wise, most holy, most free, "
                "most absolute' (II.1). The Trinity is Nicene-Chalcedonian "
                "with the Western *filioque*: 'the Son is eternally begotten of "
                "the Father, the Holy Ghost eternally proceeding from the Father "
                "and the Son' (II.3). The decree (III) is the locus on which "
                "the Assembly worked hardest and reached its most carefully "
                "balanced formulation. On the order of decrees the Assembly "
                "deliberately permitted both supra- and infralapsarianism. On "
                "the extent of the atonement (III.6, VIII.5) it taught particular "
                "redemption while leaving room for the hypothetical-universal "
                "language of Davenant, Calamy, Vines, and Seaman."
            ),
            'philosophical_significance': (
                "Westminster's God is the God of classical theism — simple, "
                "impassible, atemporally eternal, omnipotent — but also "
                "Trinitarian in a determinately Western shape. The decree (III) "
                "is the Assembly's most ambitious metaphysical claim: a single "
                "eternal act of will whose 'order' (supra/infra) is logical, "
                "not temporal, and whose efficacy is unconditioned by foreseen "
                "creaturely action. The doctrine of providence (V) couples this "
                "with a robust concursus: secondary causes act freely or "
                "contingently while remaining wholly under the first cause's "
                "ordination. This is not occasionalism (Malebranche's later "
                "answer) but rather the Reformed scholastic synthesis worked "
                "out by Voetius and Turretin."
            ),
            'scriptural_perspective': (
                "WCF III.1 proof-texts the decree from Ephesians 1:11, Romans "
                "11:33, Hebrews 6:17, and Romans 9:15–18; III.5 grounds election "
                "in Ephesians 1:4–6 and 2 Thessalonians 2:13; III.7 reads "
                "reprobation through Romans 9 and 1 Peter 2:8; III.8 cautions "
                "the use of the doctrine of predestination by appealing to "
                "Romans 9:20, Deuteronomy 29:29, and 2 Peter 1:10. The Larger "
                "Catechism Q. 12–13 develops the same material; Shorter "
                "Catechism Q. 7 — 'The decrees of God are, his eternal purpose, "
                "according to the counsel of his will, whereby, for his own "
                "glory, he hath foreordained whatsoever comes to pass' — is the "
                "compressed catechetical form."
            ),
            'key_controversies': [
                {
                    'title': 'Supra- or infralapsarian?',
                    'body': (
                        "Twisse (the prolocutor), Rutherford, and Gillespie tilted "
                        "supralapsarian; Calamy, Burgess, and most of the English "
                        "majority were infralapsarian. The Confession III.7's "
                        "language — God 'was pleased…to pass by' the rest of "
                        "mankind 'for the glory of his sovereign power' — was "
                        "deliberately drafted to allow both readings; Twisse's "
                        "supra preferences were neither imposed nor excluded. This "
                        "deliberate latitude is one of the Standards' most "
                        "important and underappreciated features."
                    ),
                },
                {
                    'title': 'Extent of the atonement',
                    'body': (
                        "Edmund Calamy (in the famous January 1646 debate), Lazarus "
                        "Seaman, and Richard Vines argued for hypothetical "
                        "universalism — that Christ's death is sufficient for all "
                        "and intended conditionally for all, though efficacious "
                        "only for the elect. Rutherford and Gillespie pressed for "
                        "strict particularism. The Confession's language — Christ "
                        "'purchased' redemption 'for all those whom the Father "
                        "hath given unto him' (III.6, VIII.5, VIII.8) — secures "
                        "particular redemption while remaining compatible with "
                        "the Davenant-Calamy-Vines reading of sufficient-for-all."
                    ),
                },
                {
                    'title': 'Reprobation: positive or permissive?',
                    'body': (
                        "WCF III.7 distinguishes God's *passing by* the non-elect "
                        "(preterition) from the *ordaining* of them 'to dishonor "
                        "and wrath for their sin.' Reprobation is *positive* as to "
                        "the eternal decree but *just* as to its execution — the "
                        "non-elect are condemned for their sin, not despite their "
                        "innocence. The carefully balanced language is the "
                        "Standards' attempt to be more rigorous than Dort's "
                        "without falling into the harder supralapsarianism of "
                        "Beza or Twisse."
                    ),
                },
                {
                    'title': 'The pactum salutis',
                    'body': (
                        "The Larger Catechism Q. 31 ('With whom was the covenant "
                        "of grace made?…with Christ as the second Adam, and in "
                        "him with all the elect as his seed') and WCF VIII.1 "
                        "('It pleased God…to choose and ordain the Lord Jesus, "
                        "his only begotten Son, to be the Mediator between God "
                        "and man') give the pactum salutis a confessional "
                        "footing without the developed apparatus of Cocceius or "
                        "Witsius. The Standards leave the technical exposition "
                        "to the divines who developed it (Rutherford, Goodwin, "
                        "later Owen and Boston)."
                    ),
                },
            ],
        },
        'attributes': [
            {
                'key': 'trinity_processions',
                'label': 'Trinity',
                'values': [
                    {'key': 'nicene_with_filioque', 'label': 'Nicene-With-Filioque',
                     'definition': "One God in three persons; the Son eternally begotten of the Father, the Spirit eternally proceeding from the Father *and the Son* (WCF II.3)."},
                    {'key': 'nicene_east', 'label': 'Eastern-Procession-From-Father-Only',
                     'definition': "Spirit proceeds from the Father alone; the Eastern Orthodox position rejected (implicitly) by WCF II.3's filioque."},
                    {'key': 'subordinationist', 'label': 'Subordinationist',
                     'definition': "Son or Spirit ontologically subordinate to the Father — Arian/Socinian; rejected by II.3."},
                    {'key': 'modalist', 'label': 'Modalist',
                     'definition': "One person in three modes or operations — Sabellian; rejected by II.3's 'three persons of one substance.'"},
                ],
            },
            {
                'key': 'order_of_decrees',
                'label': 'Order of Decrees',
                'values': [
                    {'key': 'permitted_both', 'label': 'Deliberately-Permits-Both',
                     'definition': "WCF III's language is deliberately drafted to permit both supra- and infralapsarianism without imposing either."},
                    {'key': 'supralapsarian', 'label': 'Supralapsarian',
                     'definition': "Election and reprobation logically precede the decree of the fall; the order favoured by Twisse and Rutherford within Westminster's permitted range."},
                    {'key': 'infralapsarian', 'label': 'Infralapsarian',
                     'definition': "Election and reprobation logically follow the decree of the fall; the order held by the English majority within Westminster's permitted range."},
                ],
            },
            {
                'key': 'extent_of_atonement',
                'label': 'Extent of Atonement',
                'values': [
                    {'key': 'particular', 'label': 'Particular',
                     'definition': "Christ purchased redemption only for the elect; the atonement is intended, designed, and applied for the elect alone (WCF III.6, VIII.5, VIII.8)."},
                    {'key': 'hypothetical_universal', 'label': 'Hypothetical-Universal',
                     'definition': "Christ's death is sufficient for all and intended conditionally for all who believe, while efficacious only for the elect — the Calamy-Davenant-Vines reading the Standards' language does not exclude."},
                    {'key': 'general', 'label': 'General-Arminian',
                     'definition': "Christ died indifferently for all, the application conditioned on foreseen faith — the Arminian position rejected by III.6."},
                ],
            },
            {
                'key': 'reprobation',
                'label': 'Reprobation',
                'values': [
                    {'key': 'preterition_and_just_condemnation', 'label': 'Preterition-And-Just-Condemnation',
                     'definition': "God passes by the non-elect and ordains them to dishonour and wrath *for their sin* (WCF III.7); a positive decree as to election, a just condemnation as to its execution."},
                    {'key': 'positive_double', 'label': 'Positive-Double-Predestination',
                     'definition': "God positively decrees the damnation of the reprobate as an end in itself — the sharper supralapsarian inflection beyond what III.7 states."},
                    {'key': 'single_predestination', 'label': 'Single-Predestination',
                     'definition': "Affirms election but denies any decree of reprobation — a minority view in seventeenth-century Reformed theology, not entertained by the Standards."},
                    {'key': 'conditional', 'label': 'Conditional-On-Foreseen-Unbelief',
                     'definition': "Reprobation is grounded in foreseen unbelief — the Arminian position rejected by III.5–7."},
                ],
            },
            {
                'key': 'covenant_of_redemption',
                'label': 'Covenant of Redemption',
                'values': [
                    {'key': 'implicit_affirmed', 'label': 'Implicit-Affirmed',
                     'definition': "The Standards affirm the substance of the pactum salutis — God's choosing of Christ as Mediator (WCF VIII.1) and the covenant of grace made with Christ as the second Adam (LC Q. 31) — without the developed apparatus of Cocceius or Witsius."},
                    {'key': 'explicit_developed', 'label': 'Explicit-Developed',
                     'definition': "A distinct eternal covenant between the Father and the Son, fully developed as a third covenant alongside works and grace — the Cocceian-Witsian elaboration."},
                    {'key': 'rejected', 'label': 'Rejected',
                     'definition': "Treats the pactum salutis as speculative and not warranted by Scripture — a minority Reformed view."},
                ],
            },
        ],
    },

    # ==================================================================
    # III. COVENANT
    # ==================================================================
    {
        'key': 'covenant',
        'label': 'Covenant',
        'numeral': 'III',
        'color': 'covenant',
        'icon': '⊕',
        'tagline': "Federal theology — works, grace, and the unity of redemption",
        'prose': {
            'overview': (
                "WCF VII — 'Of God's Covenant with Man' — is the Standards' "
                "structural hinge between theology proper and Christology. It "
                "teaches two covenants: the covenant of works, made with Adam, "
                "and the covenant of grace, made with Christ and in him with "
                "the elect. The covenant of grace is one in substance through "
                "both testaments, though *differently administered* — under "
                "the law by promises, prophecies, sacrifices, circumcision, "
                "the paschal lamb and other types and ordinances; under the "
                "gospel by the preaching of the Word and the administration of "
                "the sacraments of Baptism and the Lord's Supper. The Larger "
                "Catechism Q. 30–35 develops the covenant of grace at length; "
                "Q. 31 mentions Christ as the second Adam and the elect as his "
                "seed — language with strong pactum-salutis resonances. WCF "
                "VII.6's 'one and the same' covenant of grace 'under various "
                "dispensations' is the Standards' most important statement on "
                "the unity of the testaments and is the basis of paedobaptism "
                "(XXVIII.4)."
            ),
            'philosophical_significance': (
                "Westminster's covenant theology is a philosophy of "
                "historical-redemptive intelligibility: God's dealings with "
                "humankind across the testaments are *one* story, governed by "
                "*two* covenants and unified by the person and work of Christ. "
                "It is also a philosophy of moral obligation: the covenant of "
                "works grounds the natural law's claim on every human, while "
                "the covenant of grace grounds the gospel's free offer. The "
                "Standards' bi-covenantal frame deliberately avoids the "
                "tri-covenantal architecture of later Cocceian dogmatics, but "
                "leaves materials for it (LC 31; WCF VIII.1)."
            ),
            'scriptural_perspective': (
                "WCF VII proof-texts the bi-covenantal frame from Galatians "
                "3:12 ('the man that doeth them shall live in them'), Romans "
                "10:5, Genesis 2:17, Romans 5:12–21, Genesis 3:15, Galatians "
                "3:7–9, Hebrews 8–10, and Luke 22:20. The unity of the "
                "covenant of grace across the testaments (VII.6) is grounded "
                "in Galatians 3 and Hebrews 8."
            ),
            'key_controversies': [
                {
                    'title': 'How many covenants?',
                    'body': (
                        "The mainstream Westminster position is bi-covenantal: "
                        "works with Adam, grace through Christ. The pactum "
                        "salutis is materially present (LC Q. 31; WCF VIII.1) "
                        "without being a formal third covenant. The "
                        "tri-covenantal architecture — Cocceius, Witsius, "
                        "Boston — develops later as an elaboration of, not a "
                        "departure from, the Standards."
                    ),
                },
                {
                    'title': 'The Mosaic covenant',
                    'body': (
                        "WCF VII.5–6 places the Mosaic within the covenant of "
                        "grace — 'under the law' as one administration of the "
                        "one covenant of grace 'unto the foreordained time of "
                        "Christ.' The republication thesis — that Sinai also "
                        "re-publishes the covenant of works in a typological "
                        "mode — is taken up by Owen, Petto, and Boston in the "
                        "decades after the Assembly and remains a live "
                        "intra-Reformed question; the Standards themselves "
                        "tilt away from it."
                    ),
                },
                {
                    'title': 'The covenant and the children',
                    'body': (
                        "WCF XXV.2 includes the children of professing "
                        "believers in the visible church; XXVIII.4 grounds "
                        "paedobaptism in covenant inclusion. The 1689 "
                        "Particular Baptist Confession, which adopted "
                        "Westminster's language *de novo* for the rest of its "
                        "structure, departed here: only professing believers "
                        "and their profession-marked baptism belong to the "
                        "visible covenant."
                    ),
                },
            ],
        },
        'attributes': [
            {
                'key': 'number_of_covenants',
                'label': 'Number of Covenants',
                'values': [
                    {'key': 'bi', 'label': 'Bi-Covenantal',
                     'definition': "Two covenants — works (with Adam) and grace (with Christ and his elect) — WCF VII.2–3; the Standards' express scheme."},
                    {'key': 'tri', 'label': 'Tri-Covenantal',
                     'definition': "Adds an eternal covenant of redemption between Father and Son as a formal third — the Cocceian-Witsian elaboration."},
                    {'key': 'mono', 'label': 'Mono-Covenantal',
                     'definition': "One covenant of grace across both testaments; minimises a pre-fall covenant of works — a minority Reformed view, not the Standards'."},
                ],
            },
            {
                'key': 'mosaic_covenant',
                'label': 'Mosaic Covenant',
                'values': [
                    {'key': 'administration_of_grace', 'label': 'Administration-Of-Grace',
                     'definition': "The Mosaic dispensation is one administration of the one covenant of grace 'under the law,' awaiting the foreordained time of Christ (WCF VII.5–6)."},
                    {'key': 'republication', 'label': 'Republication-Of-Works',
                     'definition': "Sinai re-publishes the covenant of works in a typological mode while the covenant of grace continues underneath — developed by Owen and Boston after the Assembly."},
                    {'key': 'subservient', 'label': 'Subservient-Covenant',
                     'definition': "Sinai is a third covenant subservient to grace — a Particular Baptist development."},
                ],
            },
            {
                'key': 'children_of_believers',
                'label': 'Children of Believers',
                'values': [
                    {'key': 'paedo_federal', 'label': 'Federal-Inclusion-Paedobaptist',
                     'definition': "Children of one or both believing parents are in the visible church and receive its sign (WCF XXV.2, XXVIII.4)."},
                    {'key': 'credo', 'label': 'Credo-Baptist',
                     'definition': "Only professing believers and their profession-marked baptism belong to the visible covenant — the 1689 Particular Baptist departure."},
                    {'key': 'national', 'label': 'National-Comprehensive',
                     'definition': "All nationally baptised infants are full visible church members — the broader Erastian-Anglican settlement, rejected by Westminster's stricter discipline."},
                ],
            },
            {
                'key': 'testamental_continuity',
                'label': 'Testamental Continuity',
                'values': [
                    {'key': 'one_substance_different_administrations', 'label': 'One-Substance-Different-Administrations',
                     'definition': "The covenant of grace is one and the same in substance through both testaments, differently administered (WCF VII.6) — the bedrock of the Standards' use of OT material."},
                    {'key': 'discontinuity', 'label': 'Testamental-Discontinuity',
                     'definition': "The new covenant is materially different from the old, not merely differently administered — a dispensationalist tendency rejected by the Standards."},
                    {'key': 'replacement', 'label': 'Replacement-Of-Israel',
                     'definition': "The church wholly replaces ethnic Israel with no remaining peculiar covenantal relation — the Standards leave open a future of ethnic Israel (cf. LC's silence)."},
                ],
            },
        ],
    },

    # ==================================================================
    # IV. CHRISTOLOGY
    # ==================================================================
    {
        'key': 'christology',
        'label': 'Christology',
        'numeral': 'IV',
        'color': 'christology',
        'icon': '☧',
        'tagline': "Christ the Mediator — natures, offices, states",
        'prose': {
            'overview': (
                "WCF VIII — 'Of Christ the Mediator' — is the Standards' "
                "Christology. The chapter integrates the conciliar inheritance "
                "(Chalcedon, Constantinople II and III) with the Reformed "
                "doctrine of the offices: 'It pleased God…to choose and "
                "ordain the Lord Jesus, his only begotten Son, to be the "
                "Mediator between God and man, the Prophet, Priest, and King' "
                "(VIII.1). Two natures, one person; God and man, yet 'two "
                "whole, perfect, and distinct natures, the Godhead and the "
                "manhood, were inseparably joined together in one person, "
                "without conversion, composition, or confusion. Which person "
                "is very God and very man, yet one Christ, the only Mediator "
                "between God and man' (VIII.2). The chapter then runs the "
                "three offices, the active and passive obedience (VIII.4–5), "
                "the application of redemption (VIII.6, 8), and the union of "
                "the believer with Christ (VIII.5, 8). The Larger Catechism "
                "Q. 36–57 develops the same material catechetically over "
                "twenty-two questions — the most extensive expansion of any "
                "topic in the Catechism."
            ),
            'philosophical_significance': (
                "Westminster's Christology is a philosophical balancing act: "
                "two natures must remain genuinely *two* against monophysite "
                "fusion, genuinely *one person* against Nestorian division, "
                "and *communicative* across the two (the *communicatio "
                "idiomatum*) without confusion of properties. The doctrine of "
                "the three offices is also a doctrine of the three "
                "deficiencies of fallen humanity: ignorance (met by the "
                "prophetic office), guilt (met by the priestly), and bondage "
                "(met by the kingly). The active-obedience clause (VIII.4–5) "
                "secures the imputation of Christ's whole righteousness — "
                "both his fulfilment of the law and his bearing of its curse "
                "— against the Piscatorian denial of active-obedience "
                "imputation."
            ),
            'scriptural_perspective': (
                "WCF VIII proof-texts the Mediator from 1 Timothy 2:5, Acts "
                "3:22, Hebrews 5:5–6, Psalm 2:6, and Luke 1:33; the union of "
                "natures from John 1:1, 14, Galatians 4:4, Luke 1:35, and "
                "Romans 9:5; the offices from Hebrews 1:1–2, John 1:18, "
                "Hebrews 9:14, 26, and Acts 5:31. The Shorter Catechism Q. "
                "21–26 is the compressed catechetical form."
            ),
            'key_controversies': [
                {
                    'title': 'Active-obedience imputation',
                    'body': (
                        "Johannes Piscator (Herborn) had denied the "
                        "imputation of Christ's active obedience, arguing "
                        "that only Christ's passive obedience (his bearing of "
                        "the law's curse) is imputed to the believer. The "
                        "Assembly debated this hard in 1645 and resolved it "
                        "by including both 'his obedience' and 'sacrifice' "
                        "in WCF VIII.5 and 'the whole obedience and "
                        "satisfaction of Christ' in XI.3."
                    ),
                },
                {
                    'title': "Christ's descent into hell",
                    'body': (
                        "The Apostles' Creed's *descendit ad inferna* is "
                        "handled by the Larger Catechism Q. 50: 'Christ's "
                        "humiliation after his death consisted in his being "
                        "buried, and continuing in the state of the dead, and "
                        "under the power of death till the third day; which "
                        "hath been otherwise expressed in these words, He "
                        "descended into hell.' This is not the *Limbus "
                        "Patrum* of Roman teaching but a state of continued "
                        "humiliation between death and resurrection — "
                        "Calvin's reading."
                    ),
                },
                {
                    'title': 'The two states',
                    'body': (
                        "The Larger Catechism (Q. 46–56) distinguishes "
                        "Christ's *estate of humiliation* (conception, birth, "
                        "life, death, burial, continuance in the state of "
                        "the dead) from his *estate of exaltation* "
                        "(resurrection, ascension, session, return to "
                        "judgment). The two-state schema is taken from "
                        "Philippians 2 and is the structural backbone of the "
                        "Catechism's Christology."
                    ),
                },
            ],
        },
        'attributes': [
            {
                'key': 'natures',
                'label': 'Natures',
                'values': [
                    {'key': 'chalcedonian_two', 'label': 'Chalcedonian-Two-Natures',
                     'definition': "Two whole, perfect, and distinct natures — Godhead and manhood — inseparably joined in one person, without conversion, composition, or confusion (WCF VIII.2)."},
                    {'key': 'monophysite', 'label': 'Monophysite',
                     'definition': "One nature after the union (Eutychian/monophysite); rejected by VIII.2."},
                    {'key': 'nestorian', 'label': 'Nestorian',
                     'definition': "Two persons in Christ; rejected by VIII.2's 'one person.'"},
                ],
            },
            {
                'key': 'offices',
                'label': 'Offices',
                'values': [
                    {'key': 'prophet_priest_king', 'label': 'Prophet-Priest-King',
                     'definition': "Three offices answering to the three deficiencies of fallen humanity (WCF VIII.1; LC Q. 42–45; SC Q. 23–26)."},
                    {'key': 'two_fold', 'label': 'Two-Office',
                     'definition': "Priest and King only — a minority schema that the Standards reject."},
                    {'key': 'one_office', 'label': 'One-Office',
                     'definition': "A single mediatorial work without the prophet-priest-king distinction — Socinian reductionism."},
                ],
            },
            {
                'key': 'states_and_descent',
                'label': 'States & Descent',
                'values': [
                    {'key': 'two_states_no_local_descent', 'label': 'Humiliation-And-Exaltation; No-Local-Descent',
                     'definition': "Two states (humiliation, exaltation); the *descendit* is interpreted as the continued state of death between cross and resurrection, not a local descent (LC Q. 50)."},
                    {'key': 'local_descent', 'label': 'Local-Descent',
                     'definition': "Christ literally descended into a place called Hades — variously to liberate OT saints, to suffer further, or to triumph over hell; not the Standards' reading."},
                    {'key': 'metaphorical_only', 'label': 'Metaphorical-Only',
                     'definition': "The *descendit* is merely metaphor for the depth of Christ's suffering on the cross — Calvin's secondary suggestion, not preferred by the LC."},
                ],
            },
            {
                'key': 'active_obedience_imputation',
                'label': 'Active-Obedience Imputation',
                'values': [
                    {'key': 'both_imputed', 'label': 'Active-And-Passive-Obedience-Imputed',
                     'definition': "Both Christ's obedience and his sacrifice — his whole righteousness — are imputed to the justified believer (WCF VIII.5; XI.1, 3)."},
                    {'key': 'passive_only', 'label': 'Passive-Only',
                     'definition': "Only Christ's suffering of the curse is imputed; his active obedience is required for his own person — Piscator's denial, rejected by the Assembly."},
                    {'key': 'neither_imputed', 'label': 'Faith-As-Righteousness',
                     'definition': "Faith itself counted as righteousness, not the imputation of Christ's obedience — the Arminian/Socinian position rejected by XI.1."},
                ],
            },
        ],
    },

    # ==================================================================
    # V. SOTERIOLOGY
    # ==================================================================
    {
        'key': 'soteriology',
        'label': 'Soteriology',
        'numeral': 'V',
        'color': 'soteriology',
        'icon': '✚',
        'tagline': "The application of redemption — calling, justifying, sanctifying",
        'prose': {
            'overview': (
                "WCF X–XVIII traces the *ordo salutis*: effectual calling "
                "(X), justification (XI), adoption (XII), sanctification "
                "(XIII), saving faith (XIV), repentance unto life (XV), good "
                "works (XVI), perseverance of the saints (XVII), and "
                "assurance of grace and salvation (XVIII). Each chapter is "
                "carefully drafted to balance God's monergistic grace with "
                "the integrity of the renewed human faculties: effectual "
                "calling renews the mind, will, and affections (X.1–2) "
                "without violating creaturely freedom; justification is a "
                "forensic declaration on the ground of Christ's imputed "
                "righteousness alone (XI.1–4) yet inseparable from a faith "
                "that also works (XI.2, XVI); perseverance is certain for "
                "the elect (XVII.1) yet pastoral assurance is attainable "
                "without being of the essence of faith (XVIII)."
            ),
            'philosophical_significance': (
                "The Westminster ordo is the most careful Reformed answer to "
                "the Roman, Arminian, and Antinomian challenges. Against "
                "Rome it secures forensic justification by imputed "
                "righteousness alone, received by faith alone (XI). Against "
                "Arminius it secures effectual calling as irresistible in "
                "its act though not coercive in its mode (X). Against the "
                "Antinomians it secures the necessity of repentance, good "
                "works, and pastoral self-examination without making them "
                "the ground of justification (XV, XVI, XVIII). The "
                "Standards' particular contribution to the Reformed tradition "
                "is the assurance chapter (XVIII), which decisively answered "
                "the post-Beza pastoral question: must every true believer "
                "have assurance? Westminster answers *no* — assurance is "
                "attainable but is not of the essence of saving faith."
            ),
            'scriptural_perspective': (
                "Effectual calling: Romans 8:30; 2 Thessalonians 2:13–14; "
                "John 6:44–45. Justification: Romans 3:24; 4:5–8; 5:17–19; "
                "Galatians 2:16; 3:11; Philippians 3:9. Faith: Ephesians "
                "2:8; Hebrews 11:1; Galatians 2:20. Perseverance: John 10:28; "
                "Romans 8:38–39; 1 John 2:19; Philippians 1:6. Assurance: "
                "1 John 5:13; 2 Peter 1:10; Romans 8:16; Hebrews 6:11."
            ),
            'key_controversies': [
                {
                    'title': 'The free offer and the will',
                    'body': (
                        "WCF X.1–2 teaches that the same Spirit who "
                        "effectually calls the elect also genuinely *offers* "
                        "Christ to those who hear the gospel, and that "
                        "effectual calling renews the will so that the "
                        "sinner comes 'most freely.' The Arminians charged "
                        "Reformed teaching with making the gospel offer "
                        "insincere; the Standards' careful pairing of the "
                        "outward call (sincere to all) with the inward call "
                        "(efficacious for the elect) is the Reformed answer."
                    ),
                },
                {
                    'title': 'Justification and the antinomian crisis',
                    'body': (
                        "The 1640s saw the publication of Tobias Crisp's "
                        "*Christ Alone Exalted* (1643) and a fresh outbreak "
                        "of antinomian preaching. WCF XI–XVI was drafted "
                        "with this controversy in view: XI.1–4 secures sola "
                        "fide; XI.2 insists that 'faith…is no dead faith, "
                        "but worketh by love'; XVI–XVII make good works "
                        "necessary fruits without making them the ground of "
                        "justification."
                    ),
                },
                {
                    'title': 'Assurance: essence of faith or distinct from it?',
                    'body': (
                        "Calvin and Beza had tended to equate full assurance "
                        "with saving faith; Perkins and many English "
                        "Puritans softened this. WCF XVIII.3 codifies the "
                        "Puritan softening: assurance 'doth not so belong to "
                        "the essence of faith, but that a true believer may "
                        "wait long, and conflict with many difficulties, "
                        "before he be partaker of it.' This is the "
                        "Standards' great pastoral concession to the "
                        "experimental tradition."
                    ),
                },
            ],
        },
        'attributes': [
            {
                'key': 'effectual_calling',
                'label': 'Effectual Calling',
                'values': [
                    {'key': 'irresistible_renewing', 'label': 'Effectual-And-Renewing',
                     'definition': "The Spirit effectually calls the elect by enlightening their minds, renewing their wills, and drawing them to Christ, yet so as they come most freely (WCF X.1–2)."},
                    {'key': 'resistible', 'label': 'Resistible-Sufficient-Grace',
                     'definition': "Grace is sufficient for all who hear and is finally resistible — the Arminian position rejected by X.2."},
                    {'key': 'cooperative', 'label': 'Cooperative-Synergistic',
                     'definition': "The will cooperates with grace as a co-equal cause — the Tridentine position rejected by X.1."},
                    {'key': 'hyper_unconditional', 'label': 'Eternal-Justification',
                     'definition': "The elect are eternally justified prior to faith; calling is the discovery, not the application, of justification — Eternal-Justification antinomianism."},
                ],
            },
            {
                'key': 'justification_ground',
                'label': 'Justification Ground',
                'values': [
                    {'key': 'imputed_righteousness', 'label': 'Imputed-Righteousness-Of-Christ',
                     'definition': "Justification is a forensic act of pardon and acceptance grounded in the imputation of Christ's whole obedience and satisfaction, received by faith alone (WCF XI.1–4)."},
                    {'key': 'infused', 'label': 'Infused-Righteousness',
                     'definition': "Justification is by infused habitual grace making the believer righteous — the Tridentine position rejected by XI.1."},
                    {'key': 'faith_as_righteousness', 'label': 'Faith-As-Righteousness',
                     'definition': "Faith itself is counted as the formal righteousness — the Arminian-Socinian reading rejected by XI.1."},
                    {'key': 'eternal_in_decree', 'label': 'Eternal-In-The-Decree',
                     'definition': "Justification is eternal in the decree, only manifested in time — antinomian, rejected by XI.4."},
                ],
            },
            {
                'key': 'saving_faith',
                'label': 'Saving Faith',
                'values': [
                    {'key': 'receptive_resting', 'label': 'Receptive-Resting-On-Christ-Alone',
                     'definition': "Saving faith is the act of the soul receiving and resting upon Christ alone for salvation, as he is offered in the gospel (WCF XIV.2; SC Q. 86)."},
                    {'key': 'formed_by_love', 'label': 'Formed-By-Love',
                     'definition': "Faith justifies as it is *formed* by love (*fides caritate formata*) — the Tridentine position rejected by WCF XI.2."},
                    {'key': 'mere_assent', 'label': 'Mere-Assent',
                     'definition': "Faith is bare intellectual assent without trust — the Socinian and (in some readings) the strict-orthodox-only inflection; rejected by XIV.2."},
                ],
            },
            {
                'key': 'perseverance',
                'label': 'Perseverance',
                'values': [
                    {'key': 'certain_for_elect', 'label': 'Certain-For-The-Elect',
                     'definition': "Those whom God hath accepted in his Beloved, effectually called and sanctified by his Spirit, can neither totally nor finally fall away from the state of grace (WCF XVII.1)."},
                    {'key': 'conditional', 'label': 'Conditional-On-Continued-Faith',
                     'definition': "Perseverance is conditional on the believer's continued faith and obedience; final apostasy of the truly regenerate is possible — the Arminian position rejected by XVII.1."},
                    {'key': 'fall_from_grace', 'label': 'Fall-From-Grace',
                     'definition': "A regenerate believer may finally fall away — the Wesleyan and later Arminian reading, rejected by XVII.1."},
                ],
            },
            {
                'key': 'assurance',
                'label': 'Assurance',
                'values': [
                    {'key': 'attainable_not_essence', 'label': 'Attainable-But-Not-Essence-Of-Faith',
                     'definition': "An infallible assurance is attainable in this life but does not belong to the essence of faith; a true believer may wait long and conflict with many difficulties before partaking of it (WCF XVIII.3)."},
                    {'key': 'essence_of_faith', 'label': 'Essence-Of-Faith',
                     'definition': "Assurance is of the essence of saving faith; every true believer enjoys full assurance — the early-Calvin and Beza tendency softened by the Standards."},
                    {'key': 'unattainable', 'label': 'Ordinarily-Unattainable',
                     'definition': "Assurance is so rare as to be ordinarily unattainable — the Tridentine position rejected by XVIII.1–4."},
                    {'key': 'both_grounds', 'label': 'Both-Spirit-Witness-And-Marks',
                     'definition': "Assurance is built upon the divine truth of the promises, the inward evidence of those graces unto which the promises are made, and the testimony of the Spirit of adoption (WCF XVIII.2)."},
                ],
            },
        ],
    },

    # ==================================================================
    # VI. LAW & SANCTIFICATION
    # ==================================================================
    {
        'key': 'law_sanctification',
        'label': 'Law & Sanctification',
        'numeral': 'VI',
        'color': 'law_sanctification',
        'icon': '⚖',
        'tagline': "The moral law, the Sabbath, the Christian life",
        'prose': {
            'overview': (
                "WCF XIX–XXII handles the law (XIX), Christian liberty and "
                "liberty of conscience (XX), religious worship and the "
                "Sabbath day (XXI), and lawful oaths and vows (XXII). The "
                "Larger Catechism Q. 91–151 exposits the Decalogue in "
                "extraordinary detail — sixty questions on the law alone, "
                "treating each commandment positively (what it requires) "
                "and negatively (what it forbids). WCF XIX establishes the "
                "tripartite division of the law (moral, judicial, ceremonial) "
                "and the perpetual obligation of the moral law on all "
                "persons. WCF XXI codifies the regulative principle of "
                "worship and the change of the Sabbath from the seventh to "
                "the first day of the week, kept holy from the Creation to "
                "the Resurrection on the seventh day, and from the "
                "Resurrection to the end of the world on the first day."
            ),
            'philosophical_significance': (
                "The Westminster doctrine of the law is the most fully "
                "developed Protestant moral theology of the seventeenth "
                "century, and the Larger Catechism's exposition of the "
                "Decalogue is its most striking achievement. The law has "
                "three uses (Calvin's *triplex usus*) — civil, pedagogical, "
                "and normative for the regenerate — and the third use is "
                "made central to sanctification (WCF XIX.5–6). The Sabbath "
                "is treated as a creation ordinance (perpetually moral), "
                "with its day changed to the Lord's Day (XXI.7) — the "
                "strict-Sabbatarian position that became the spine of "
                "Reformed piety on both sides of the Atlantic."
            ),
            'scriptural_perspective': (
                "WCF XIX is grounded in Romans 5:12–19, Galatians 3:10, "
                "James 2:10–11, Matthew 5:17–19, Romans 13:8–10, and Hebrews "
                "9–10. The Sabbath chapter (XXI.7–8) is grounded in Genesis "
                "2:2–3, Exodus 20:8–11, Isaiah 58:13, Revelation 1:10, "
                "Acts 20:7, 1 Corinthians 16:1–2, and Matthew 12:1–13."
            ),
            'key_controversies': [
                {
                    'title': 'The third use of the law',
                    'body': (
                        "Antinomians (Crisp, the Familists) had pressed sola "
                        "fide so hard that the law's normative use for the "
                        "regenerate was either denied or attenuated. WCF "
                        "XIX.5–6 secures the third use: 'The moral law doth "
                        "for ever bind all, as well justified persons as "
                        "others, to the obedience thereof…although true "
                        "believers be not under the law as a covenant of "
                        "works, to be thereby justified or condemned, yet "
                        "is it of great use to them, as well as to others.'"
                    ),
                },
                {
                    'title': 'The strict Sabbath',
                    'body': (
                        "Continental Reformed theology generally allowed "
                        "more lenience on the Lord's Day. Westminster "
                        "codified the strict English-Puritan position: "
                        "'whole time' to be 'kept holy unto the Lord' "
                        "(XXI.8), 'observing an holy rest all the day from "
                        "their own works, words, and thoughts about their "
                        "worldly employments and recreations,' apart from "
                        "works of necessity and mercy. The Westminster "
                        "Sabbath became the defining mark of English- and "
                        "Scottish-Reformed piety."
                    ),
                },
                {
                    'title': 'Good works and merit',
                    'body': (
                        "WCF XVI carefully threads between Rome and the "
                        "antinomians: good works are 'the fruits and "
                        "evidences of a true and lively faith' (XVI.2), "
                        "they 'cannot make satisfaction for the debt of our "
                        "former sins' (XVI.5), they are 'accepted in him' "
                        "though not 'in their own nature' (XVI.6), and "
                        "'works done by unregenerate men' though "
                        "'commanded by God' are sinful 'because they "
                        "proceed not from an heart purified by faith' "
                        "(XVI.7)."
                    ),
                },
            ],
        },
        'attributes': [
            {
                'key': 'uses_of_the_law',
                'label': 'Uses of the Law',
                'values': [
                    {'key': 'three_uses', 'label': 'Three-Uses-Affirmed',
                     'definition': "Civil (restraint), pedagogical (driving to Christ), and normative (rule of life for the regenerate) — WCF XIX.5–6."},
                    {'key': 'two_uses', 'label': 'Two-Uses-No-Third',
                     'definition': "Civil and pedagogical only; denies the third use for the regenerate — the antinomian position rejected by XIX.6."},
                    {'key': 'pedagogical_only', 'label': 'Pedagogical-Only',
                     'definition': "The law only convicts; it has no civil or normative office — radical-spiritualist."},
                ],
            },
            {
                'key': 'tripartite_division',
                'label': 'Tripartite Division',
                'values': [
                    {'key': 'moral_judicial_ceremonial', 'label': 'Moral-Judicial-Ceremonial',
                     'definition': "Moral law (perpetually binding), judicial law (expired with the Jewish polity except for general equity), ceremonial law (abrogated in Christ) — WCF XIX.3–5."},
                    {'key': 'unitary', 'label': 'Unitary',
                     'definition': "The Mosaic law is one undifferentiated whole — denying the tripartite division on which Reformed casuistry rests."},
                    {'key': 'theonomic', 'label': 'Theonomic-General-Equity-Expanded',
                     'definition': "The judicial law's general equity binds the modern magistrate in its substance — a reading of XIX.4's 'general equity' clause beyond what the Assembly intended."},
                ],
            },
            {
                'key': 'sabbath',
                'label': 'Sabbath',
                'values': [
                    {'key': 'lords_day_perpetual', 'label': 'Lords-Day-Fourth-Commandment-Perpetual',
                     'definition': "A creation ordinance; one day in seven is to be kept holy; changed to the first day of the week from the resurrection of Christ (WCF XXI.7–8) — the strict-Sabbatarian position."},
                    {'key': 'continental', 'label': 'Continental-Moral-Only',
                     'definition': "The Sabbath's perpetual element is the principle of regular public worship, not strict cessation; permits ordered recreation after public worship — the Continental Reformed inflection."},
                    {'key': 'abrogated', 'label': 'Abrogated',
                     'definition': "The fourth commandment is wholly ceremonial and abrogated in Christ — rejected by WCF XXI.7."},
                ],
            },
            {
                'key': 'good_works',
                'label': 'Good Works',
                'values': [
                    {'key': 'necessary_fruit_not_meritorious', 'label': 'Necessary-Fruit-Not-Meritorious',
                     'definition': "Good works are the fruits and evidences of a true and lively faith; they cannot merit pardon of sin or eternal life (WCF XVI.2, 5)."},
                    {'key': 'meritorious_condignly', 'label': 'Meritorious-De-Condigno',
                     'definition': "Good works done in grace merit eternal life by condign worth — the Tridentine position rejected by XVI.5."},
                    {'key': 'not_required', 'label': 'Not-Required',
                     'definition': "Good works are unnecessary in the Christian life — the antinomian position rejected by XVI.2."},
                ],
            },
        ],
    },

    # ==================================================================
    # VII. ECCLESIOLOGY & WORSHIP
    # ==================================================================
    {
        'key': 'ecclesiology_worship',
        'label': 'Ecclesiology & Worship',
        'numeral': 'VII',
        'color': 'ecclesiology_worship',
        'icon': '☩',
        'tagline': "Church, sacraments, worship, discipline",
        'prose': {
            'overview': (
                "WCF XXV–XXXI plus XXI handle the church (XXV), the "
                "communion of saints (XXVI), the sacraments (XXVII), baptism "
                "(XXVIII), the Lord's Supper (XXIX), church censures (XXX), "
                "synods and councils (XXXI), and religious worship (XXI). "
                "The Form of Presbyterial Church Government (1645) and the "
                "Directory for Public Worship (1645) supply the ordering "
                "detail. The Confession's polity is presbyterian *jure "
                "divino* in the Scottish reading (Rutherford, Gillespie) "
                "and *jure ecclesiastico* in the more cautious English "
                "reading; both held that the visible church is governed by "
                "officers (pastors, teachers, ruling elders, deacons) and "
                "by graded assemblies (session, presbytery, synod, general "
                "assembly). The sacramental theology is signs-and-seals: "
                "the sacraments 'really exhibit, as well as represent, the "
                "graces signified' (XXVII.1, XXVIII.6) — neither the Roman "
                "*ex opere operato* nor the Zwinglian bare memorial."
            ),
            'philosophical_significance': (
                "The Westminster ecclesiology is the most carefully argued "
                "Reformed polity of the seventeenth century. It is not "
                "merely a procedural church order but a constitutional "
                "theory of ecclesial sovereignty: Christ alone is head; the "
                "civil magistrate has duties around the church but no "
                "authority within it (XXX.1, XXXI.1–5; cf. the original "
                "XXIII.3 rejected in 1788 American adoption). The "
                "regulative principle of worship (XXI.1) — that worship is "
                "limited by God's own revelation in Scripture and not by "
                "human imagination or church tradition — is a determinate "
                "epistemology of worship as well as a polemic against the "
                "ceremonial and sacramental Catholicism the Assembly "
                "displaced."
            ),
            'scriptural_perspective': (
                "Polity: Matthew 16:19; 18:17–20; Acts 6, 15, 20:17–28; "
                "1 Timothy 3 and 5; Titus 1; Hebrews 13:7, 17. Sacraments: "
                "Romans 4:11; 1 Corinthians 10:16–21; 11:23–29; Matthew "
                "28:19–20; Acts 2:38–39. Worship: Deuteronomy 12:32; Matthew "
                "15:9; Colossians 2:23; John 4:23–24. Synods: Acts 15:1–35."
            ),
            'key_controversies': [
                {
                    'title': 'Presbyterian vs Independent',
                    'body': (
                        "The Five Dissenting Brethren (Goodwin, Nye, Bridge, "
                        "Burroughs, Simpson) argued the congregational case "
                        "in *An Apologeticall Narration* (1644); Rutherford, "
                        "Gillespie, and the Scottish commissioners pressed "
                        "presbyterianism. The Standards' polity is broadly "
                        "presbyterian, but WCF XXX–XXXI is general enough "
                        "that 1689 Particular Baptists and post-Savoy "
                        "Congregationalists could adopt most of the "
                        "language without contradiction. The decisive "
                        "Assembly votes (1646) went with the presbyterian "
                        "majority; the Independents protested but stayed."
                    ),
                },
                {
                    'title': 'Erastianism',
                    'body': (
                        "John Selden, John Lightfoot, and Thomas Coleman "
                        "argued at Westminster for the Erastian position: "
                        "ecclesiastical jurisdiction belongs ultimately to "
                        "the civil magistrate, not to a distinct ecclesial "
                        "court. Gillespie's *Aaron's Rod Blossoming* (1646) "
                        "is the canonical refutation. WCF XXX.1 settled the "
                        "matter: 'The Lord Jesus, as King and Head of his "
                        "Church, hath therein appointed a government, in "
                        "the hand of Church officers, distinct from the "
                        "civil magistrate.'"
                    ),
                },
                {
                    'title': 'The regulative principle',
                    'body': (
                        "WCF XXI.1: 'The acceptable way of worshipping the "
                        "true God is instituted by himself, and so limited "
                        "by his own revealed will, that he may not be "
                        "worshipped according to the imaginations and "
                        "devices of men…or any other way not prescribed in "
                        "the Holy Scripture.' This is the strict "
                        "(prescriptive) reading — only what is commanded "
                        "may be done. The contrast is the Anglican-Lutheran "
                        "*normative* principle: whatever is not forbidden "
                        "may be done."
                    ),
                },
            ],
        },
        'attributes': [
            {
                'key': 'polity',
                'label': 'Polity',
                'values': [
                    {'key': 'presbyterian_jure_divino', 'label': 'Presbyterian-Jure-Divino',
                     'definition': "Christ has instituted a graded series of presbyterial assemblies (session, presbytery, synod, general assembly) by divine right (Form of Government 1645; WCF XXX–XXXI) — the Scottish reading."},
                    {'key': 'independent_congregational', 'label': 'Independent-Congregational',
                     'definition': "Christ has given the keys to the local congregation under its officers; synods are advisory — the Dissenting Brethren's reading, accommodated by but not affirmed in the Standards."},
                    {'key': 'episcopal_reformed', 'label': 'Reformed-Episcopal',
                     'definition': "Retains bishops over presbyters as a third order of ministry while affirming the Reformed doctrine — the Anglican settlement Westminster displaced."},
                    {'key': 'erastian', 'label': 'Erastian',
                     'definition': "Civil magistrate is the ultimate ecclesiastical authority — Selden's and Lightfoot's Assembly position, rejected by WCF XXX.1."},
                ],
            },
            {
                'key': 'sacraments_efficacy',
                'label': 'Sacramental Efficacy',
                'values': [
                    {'key': 'signs_and_seals', 'label': 'Signs-And-Seals-Conferring-Grace-By-Spirit',
                     'definition': "Sacraments are signs and seals of the covenant of grace, conferring the grace signified by the work of the Spirit and the word of institution upon worthy receivers (WCF XXVII.1–3; XXVIII.6; XXIX.7)."},
                    {'key': 'ex_opere_operato', 'label': 'Ex-Opere-Operato',
                     'definition': "Sacraments confer grace by the act performed, independent of faith — the Tridentine position rejected by XXVII.3."},
                    {'key': 'bare_memorial', 'label': 'Bare-Memorial',
                     'definition': "Sacraments are merely memorial or instructive signs with no conferral of grace — the Zwinglian position softened by Westminster's seal language."},
                    {'key': 'converting_ordinance', 'label': 'Converting-Ordinance',
                     'definition': "The Lord's Supper functions as a converting ordinance for the morally serious unconverted — Stoddard's later position, rejected by WCF XXIX.7."},
                ],
            },
            {
                'key': 'regulative_principle',
                'label': 'Regulative Principle',
                'values': [
                    {'key': 'strict', 'label': 'Strict-Only-What-Commanded',
                     'definition': "Only what is instituted by God in Scripture (by precept, approved example, or good and necessary consequence) may be done in worship (WCF XXI.1)."},
                    {'key': 'moderate', 'label': 'Moderate-With-Circumstances',
                     'definition': "Regulative in substance but allows circumstantial adiaphora (time, place, posture) governed by light of nature and Christian prudence (WCF I.6, XXI.1)."},
                    {'key': 'normative', 'label': 'Normative-Whatever-Not-Forbidden',
                     'definition': "Whatever is not forbidden may be done in worship — the Anglican-Lutheran principle the Standards reject."},
                ],
            },
            {
                'key': 'censures_and_synods',
                'label': 'Censures & Synods',
                'values': [
                    {'key': 'three_degrees_with_synods', 'label': 'Three-Degrees-With-Graded-Synods',
                     'definition': "Admonition, suspension from the sacrament, and excommunication (WCF XXX.4); synods and councils as a regulative ordinance of Christ for the better government of the church (XXXI.1–2)."},
                    {'key': 'single_degree', 'label': 'Excommunication-Only',
                     'definition': "Discipline collapses into a single degree (excommunication) — a more lax practice rejected by WCF XXX.4."},
                    {'key': 'civil_only', 'label': 'Civil-Discipline-Only',
                     'definition': "Discipline belongs to the magistrate — the Erastian view rejected by XXX.1."},
                ],
            },
        ],
    },

    # ==================================================================
    # VIII. CIVIL & LAST THINGS
    # ==================================================================
    {
        'key': 'civil_last_things',
        'label': 'Civil & Last Things',
        'numeral': 'VIII',
        'color': 'civil_last_things',
        'icon': '⌛',
        'tagline': "Magistrate, oaths, marriage; death, resurrection, judgment",
        'prose': {
            'overview': (
                "WCF XXIII–XXIV (the magistrate; marriage and divorce) and "
                "WCF XXXII–XXXIII (the state of man after death and the "
                "resurrection of the dead; the last judgment) frame the "
                "Standards' civil and eschatological commitments. The "
                "magistrate chapter is the locus of the Standards' great "
                "internal evolution: the 1646 British text gave the "
                "magistrate broad authority over the visible church "
                "(calling synods, suppressing heresies); the 1788 American "
                "revision excised these clauses in favour of "
                "non-establishment. The marriage chapter (XXIV) limits "
                "divorce to adultery and willful desertion. The "
                "intermediate-state chapter (XXXII) teaches the conscious "
                "existence of the souls of the just with God and of the "
                "wicked under judgment — against soul-sleep (mortalism). "
                "The judgment chapter (XXXIII) teaches a single final "
                "judgment of men and angels by Christ, with eternal life "
                "for the just and eternal punishment for the wicked."
            ),
            'philosophical_significance': (
                "The civil chapters carry an unresolved tension. The "
                "establishment language of 1646 reflects the Solemn League "
                "and Covenant's project of a united Reformed Britain — a "
                "magistrate as *custos utriusque tabulae* (keeper of both "
                "tables of the Decalogue). The 1788 American revision "
                "anticipates the disestablishment that became one of the "
                "Constitutional Convention's settlements. Both texts "
                "remain in confessional use; the Reformed Presbyterian "
                "tradition retains the 1646 language, the mainline "
                "American Presbyterians follow the 1788. On eschatology "
                "the Standards are unusually compressed — two short "
                "chapters — and leave the millennial question entirely "
                "open. The papal-antichrist identification at XXV.6 is the "
                "Standards' one direct eschatological identification."
            ),
            'scriptural_perspective': (
                "Magistrate: Romans 13:1–7; 1 Timothy 2:1–2; Psalm 2; "
                "1 Peter 2:13–17. Marriage: Genesis 2:18, 24; Matthew "
                "19:4–9; 1 Corinthians 7:15; Ephesians 5:22–33. "
                "Intermediate state: Luke 23:43; 2 Corinthians 5:1, 6, 8; "
                "Philippians 1:23; Hebrews 12:23; Revelation 6:9–11. "
                "Resurrection and judgment: 1 Corinthians 15:42–44; John "
                "5:28–29; Acts 17:31; Matthew 25:31–46; 2 Corinthians "
                "5:10; 2 Peter 3:7–13."
            ),
            'key_controversies': [
                {
                    'title': "Custos utriusque tabulae?",
                    'body': (
                        "WCF XXIII.3 (1646) gives the civil magistrate "
                        "authority to call synods, to be present at them, "
                        "and to provide that whatsoever is transacted in "
                        "them be according to the mind of God; XX.4 makes "
                        "the magistrate the punisher of the publishers of "
                        "'opinions and maintainers of such practices' "
                        "destructive to the church. The 1788 American "
                        "revision rewrote both clauses to align with the "
                        "Federal disestablishment settlement: the "
                        "magistrate's duty is to protect, not to direct "
                        "or coerce, religion."
                    ),
                },
                {
                    'title': 'Divorce — adultery, desertion, and after',
                    'body': (
                        "WCF XXIV.5–6 lists two scriptural grounds for "
                        "divorce: adultery and 'wilful desertion as can no "
                        "way be remedied by the church or civil magistrate.' "
                        "This is more permissive than the strictest "
                        "Catholic and Anglican readings (which limited "
                        "remarriage even after adultery) and stricter than "
                        "the Erasmian and most later Protestant readings "
                        "(which permitted additional grounds)."
                    ),
                },
                {
                    'title': 'Antichrist',
                    'body': (
                        "WCF XXV.6: 'There is no other head of the Church "
                        "but the Lord Jesus Christ: nor can the Pope of "
                        "Rome in any sense be head thereof; but is that "
                        "Antichrist, that man of sin and son of perdition, "
                        "that exalteth himself in the Church against Christ, "
                        "and all that is called God.' The 1788 American "
                        "revision excised the explicit identification of "
                        "the Pope as Antichrist; the original Scottish text "
                        "retained it."
                    ),
                },
                {
                    'title': 'Soul-sleep vs immediate conscious state',
                    'body': (
                        "WCF XXXII.1: 'The bodies of men, after death, "
                        "return to dust, and see corruption: but their "
                        "souls, which neither die nor sleep, having an "
                        "immortal subsistence, immediately return to God "
                        "who gave them.' This is a direct rejection of "
                        "Christian mortalism (soul-sleep) — Milton's "
                        "later position — and of the Roman *limbus* and "
                        "purgatorial scheme."
                    ),
                },
            ],
        },
        'attributes': [
            {
                'key': 'magistrate_role',
                'label': "Magistrate's Role",
                'values': [
                    {'key': 'custos_utriusque_tabulae', 'label': 'Custos-Utriusque-Tabulae (1646)',
                     'definition': "Magistrate has duty toward both tables of the Decalogue — to suppress public heresy and blasphemy, to call synods (WCF XXIII.3, 1646 text) — the Solemn-League-and-Covenant settlement."},
                    {'key': 'protective_not_directive', 'label': 'Protective-Not-Directive (1788)',
                     'definition': "Magistrate protects the church from violence and danger without preferring one denomination — the American 1788 revision aligning with disestablishment."},
                    {'key': 'mixed', 'label': 'Mixed-Care-Without-Coercion',
                     'definition': "Affirms the magistrate's care for true religion but restricts instruments to non-coercive means."},
                    {'key': 'erastian', 'label': 'Erastian-Magistrate-Over-Church',
                     'definition': "Magistrate holds ultimate ecclesiastical authority — Selden and Lightfoot's Assembly position rejected by XXX.1."},
                ],
            },
            {
                'key': 'lawful_oaths_and_marriage',
                'label': 'Oaths & Marriage',
                'values': [
                    {'key': 'oaths_serious_marriage_two_grounds', 'label': 'Oaths-Lawful-Serious; Divorce-Adultery-Or-Desertion',
                     'definition': "Lawful oaths are a part of religious worship when warranted by truth, judgment and seriousness (WCF XXII.1–7); marriage between one man and one woman, indissoluble except by adultery or willful desertion (XXIV.1, 5–6)."},
                    {'key': 'oaths_forbidden', 'label': 'Oaths-Forbidden-Altogether',
                     'definition': "Christ's words 'Swear not at all' (Matthew 5:34) forbid all oaths — the Quaker position rejected by XXII.1."},
                    {'key': 'marriage_strict', 'label': 'Marriage-No-Divorce',
                     'definition': "Marriage is wholly indissoluble; even adultery does not warrant remarriage — a stricter Catholic position rejected by XXIV.5."},
                    {'key': 'marriage_liberal', 'label': 'Marriage-Liberal-Divorce',
                     'definition': "Multiple grounds for divorce beyond adultery and desertion — the broader Erasmian-Reformed reading not adopted by Westminster."},
                ],
            },
            {
                'key': 'intermediate_state',
                'label': 'Intermediate State',
                'values': [
                    {'key': 'immediate_conscious', 'label': 'Immediate-Conscious-With-God-Or-Judgment',
                     'definition': "Souls of the righteous are immediately received into the highest heavens; souls of the wicked are cast into hell, where they remain in torments and utter darkness, reserved to the judgment of the great day (WCF XXXII.1)."},
                    {'key': 'soul_sleep', 'label': 'Soul-Sleep-Mortalism',
                     'definition': "Souls sleep unconsciously between death and resurrection — the Christian-mortalist position (Milton later) rejected by XXXII.1."},
                    {'key': 'purgatory', 'label': 'Purgatory-And-Limbus',
                     'definition': "Souls of the imperfectly purified pass through purgatorial fire; OT saints in *limbus patrum* — the Roman scheme rejected by XXXII.1's denial of 'any other place' beyond heaven and hell."},
                ],
            },
            {
                'key': 'final_judgment',
                'label': 'Final Judgment',
                'values': [
                    {'key': 'single_universal_judgment', 'label': 'Single-Universal-Judgment-By-Christ',
                     'definition': "God hath appointed a day wherein he will judge the world in righteousness by Jesus Christ; the righteous to everlasting life, the wicked to everlasting destruction (WCF XXXIII.1–2; SC Q. 38)."},
                    {'key': 'two_resurrections', 'label': 'Two-Resurrections-Premillennial',
                     'definition': "Two distinct resurrections separated by a millennial reign — the premillennial scheme; the Standards do not adopt this language but neither do they exclude it."},
                    {'key': 'annihilationism', 'label': 'Annihilationism',
                     'definition': "The wicked are finally annihilated rather than eternally punished — a Socinian-then-conditionalist position rejected by XXXIII.2's 'everlasting destruction.'"},
                    {'key': 'universalism', 'label': 'Universal-Restoration',
                     'definition': "All shall finally be saved (Origen's *apokatastasis*; some seventeenth-century radicals) — rejected by XXXIII.2."},
                ],
            },
        ],
    },
]


# ----------------------------------------------------------------------
# Lookup tables (mirrors the puritans/data.py shape exactly so the same
# downstream machinery — value-detail page, dimension intersections,
# entity placement — can be reused).
# ----------------------------------------------------------------------

# Map (full_attr_key, value_label) → value_key for normalisation.
ATTR_VALUE_KEYS = {}
ATTR_LABELS = {}
ATTR_DIM = {}
for _d in DIMENSIONS:
    for _a in _d['attributes']:
        _full = f"{_d['key']}_{_a['key']}"
        ATTR_LABELS[_full] = _a['label']
        ATTR_DIM[_full] = _d['key']
        for _v in _a['values']:
            ATTR_VALUE_KEYS[(_full, _v['label'])] = _v['key']


# Flat matrix attributes list for the ontology grid view.
MATRIX_ATTRIBUTES = []
for _d in DIMENSIONS:
    for _a in _d['attributes']:
        MATRIX_ATTRIBUTES.append({
            'dim': _d['key'],
            'dim_label': _d['label'],
            'attr_key': f"{_d['key']}_{_a['key']}",
            'attr_label': _a['label'],
            'values': _a['values'],
        })


# Dimension pairs/triplets/etc. (computed lazily — used by intersection views).
def _combinations(items, k):
    n = len(items)
    if k > n or k < 0:
        return []
    if k == 0:
        return [[]]
    if k == n:
        return [list(items)]
    idx = list(range(k))
    out = []
    while True:
        out.append([items[i] for i in idx])
        i = k - 1
        while i >= 0 and idx[i] == i + n - k:
            i -= 1
        if i < 0:
            break
        idx[i] += 1
        for j in range(i + 1, k):
            idx[j] = idx[j - 1] + 1
    return out


_DIM_KEYS = [d['key'] for d in DIMENSIONS]
DIMENSION_PAIRS = _combinations(_DIM_KEYS, 2)
DIMENSION_TRIPLETS = _combinations(_DIM_KEYS, 3)
DIMENSION_QUADRUPLETS = _combinations(_DIM_KEYS, 4)
DIMENSION_QUINTUPLETS = _combinations(_DIM_KEYS, 5)
ALL_EIGHT = _DIM_KEYS


# ----------------------------------------------------------------------
# Westminster baseline — the attrs profile that *is* the Confession's
# own position on each of the 35 attributes. Personas, works, and
# schools that hold the Standards as their confessional position can
# inherit from this baseline and override only on points of departure
# (e.g. hypothetical universalism, supralapsarianism, Independency).
# ----------------------------------------------------------------------

WESTMINSTER_BASELINE_ATTRS = {
    'scripture_sufficiency': 'Express-And-Good-Consequence',
    'scripture_canon': '66-Book-Protestant-Canon',
    'scripture_authority': 'Self-Authenticating-With-Internal-Witness',
    'scripture_interpretation': 'Scripture-Interprets-Scripture',
    'scripture_necessity': 'Necessary-After-The-Fall',

    'god_decree_trinity_processions': 'Nicene-With-Filioque',
    'god_decree_order_of_decrees': 'Deliberately-Permits-Both',
    'god_decree_extent_of_atonement': 'Particular',
    'god_decree_reprobation': 'Preterition-And-Just-Condemnation',
    'god_decree_covenant_of_redemption': 'Implicit-Affirmed',

    'covenant_number_of_covenants': 'Bi-Covenantal',
    'covenant_mosaic_covenant': 'Administration-Of-Grace',
    'covenant_children_of_believers': 'Federal-Inclusion-Paedobaptist',
    'covenant_testamental_continuity': 'One-Substance-Different-Administrations',

    'christology_natures': 'Chalcedonian-Two-Natures',
    'christology_offices': 'Prophet-Priest-King',
    'christology_states_and_descent': 'Humiliation-And-Exaltation; No-Local-Descent',
    'christology_active_obedience_imputation': 'Active-And-Passive-Obedience-Imputed',

    'soteriology_effectual_calling': 'Effectual-And-Renewing',
    'soteriology_justification_ground': 'Imputed-Righteousness-Of-Christ',
    'soteriology_saving_faith': 'Receptive-Resting-On-Christ-Alone',
    'soteriology_perseverance': 'Certain-For-The-Elect',
    'soteriology_assurance': 'Attainable-But-Not-Essence-Of-Faith',

    'law_sanctification_uses_of_the_law': 'Three-Uses-Affirmed',
    'law_sanctification_tripartite_division': 'Moral-Judicial-Ceremonial',
    'law_sanctification_sabbath': 'Lords-Day-Fourth-Commandment-Perpetual',
    'law_sanctification_good_works': 'Necessary-Fruit-Not-Meritorious',

    'ecclesiology_worship_polity': 'Presbyterian-Jure-Divino',
    'ecclesiology_worship_sacraments_efficacy': 'Signs-And-Seals-Conferring-Grace-By-Spirit',
    'ecclesiology_worship_regulative_principle': 'Strict-Only-What-Commanded',
    'ecclesiology_worship_censures_and_synods': 'Three-Degrees-With-Graded-Synods',

    'civil_last_things_magistrate_role': 'Custos-Utriusque-Tabulae (1646)',
    'civil_last_things_lawful_oaths_and_marriage': 'Oaths-Lawful-Serious; Divorce-Adultery-Or-Desertion',
    'civil_last_things_intermediate_state': 'Immediate-Conscious-With-God-Or-Judgment',
    'civil_last_things_final_judgment': 'Single-Universal-Judgment-By-Christ',
}


# Self-check: WESTMINSTER_BASELINE_ATTRS must cover every (dim, attr) and
# every value label must exist in DIMENSIONS. If this assertion fails,
# either an attribute has been added without a baseline value, or a
# baseline label is a typo (the value-detail page would 404 silently).
def _validate_baseline():
    expected = set()
    for d in DIMENSIONS:
        for a in d['attributes']:
            expected.add(f"{d['key']}_{a['key']}")
    have = set(WESTMINSTER_BASELINE_ATTRS.keys())
    missing = expected - have
    extra = have - expected
    assert not missing, f"WESTMINSTER_BASELINE_ATTRS missing keys: {sorted(missing)}"
    assert not extra, f"WESTMINSTER_BASELINE_ATTRS has unknown keys: {sorted(extra)}"
    for full_key, label in WESTMINSTER_BASELINE_ATTRS.items():
        assert (full_key, label) in ATTR_VALUE_KEYS, (
            f"WESTMINSTER_BASELINE_ATTRS[{full_key!r}] = {label!r} "
            f"is not a known value label for that attribute."
        )


_validate_baseline()
