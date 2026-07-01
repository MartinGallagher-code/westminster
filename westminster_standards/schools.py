"""Westminster schools — the parties at the Assembly and the receiving traditions.

Each school has:

  - ``slug`` / ``name`` / ``origin`` (when/where)
  - ``description`` — a substantive paragraph on the school's identity
  - ``attrs`` — a complete 35-attribute profile, inheriting from
    ``WESTMINSTER_BASELINE_ATTRS`` and overriding only on points of
    departure
  - ``anchor_persona_slugs`` — the leading figures
  - ``period`` — 'assembly-party' or 'receiving-tradition'

Assembly parties are the blocs discernible in the 1643-1649 debates.
Receiving traditions are the confessional communities that adopted,
adapted, or revised the Standards after the Assembly closed.
"""

from .data import WESTMINSTER_BASELINE_ATTRS


SCHOOLS = []
_COUNTER = [0]


def _s(slug, name, origin, period, description, *,
       overrides=None, anchor_persona_slugs=None):
    _COUNTER[0] += 1
    attrs = dict(WESTMINSTER_BASELINE_ATTRS)
    if overrides:
        attrs.update(overrides)
    SCHOOLS.append({
        'slug': slug,
        'number': _COUNTER[0],
        'name': name,
        'origin': origin,
        'period': period,
        'description': description,
        'attrs': attrs,
        'anchor_persona_slugs': anchor_persona_slugs or [],
    })


def get_school_by_slug(slug):
    for s in SCHOOLS:
        if s.get('slug') == slug:
            return s
    return None


# ======================================================================
# I. ASSEMBLY PARTIES
# ======================================================================

_s('english-presbyterian-majority',
   'English Presbyterian Majority',
   'Westminster Assembly, 1643–1649',
   'assembly-party',
   "The drafting core of the Assembly: the English ministers who held "
   "the majority on every contested polity vote and who produced the "
   "bulk of the Confession's text. They were presbyterian on polity "
   "(though many were jure-ecclesiastico rather than jure-divino), "
   "infralapsarian on the decree, particular on the atonement (with "
   "a significant hypothetical-universalist minority within their "
   "own ranks), strict-Sabbatarian, three-uses-of-the-law, and "
   "signs-and-seals on the sacraments. The Smectymnuans (Calamy, "
   "Marshall, Young, Newcomen, Spurstowe) were the most publicly "
   "visible subgroup. Most were ejected in 1662.",
   overrides={
       'god_decree_order_of_decrees': 'Infralapsarian',
   },
   anchor_persona_slugs=[
       'edmund-calamy-elder', 'stephen-marshall', 'edward-reynolds',
       'anthony-tuckney', 'cornelius-burgess', 'william-gouge',
       'herbert-palmer', 'obadiah-sedgwick', 'jeremiah-whitaker',
       'anthony-burgess', 'daniel-cawdrey',
   ])

_s('scottish-commissioners',
   'Scottish Commissioners',
   'Church of Scotland General Assembly → Westminster, 1643–1647',
   'assembly-party',
   "The four ministerial commissioners (Henderson, Rutherford, "
   "Gillespie, Baillie) and four ruling-elder commissioners "
   "(Lauderdale, Loudoun, Cassillis, Wariston) sent by the Scottish "
   "General Assembly under the Solemn League and Covenant. Advisory "
   "rather than voting members, but enormously influential. They "
   "pressed jure-divino presbyterianism, supralapsarianism (Twisse "
   "aligned with them on the decree), an explicit pactum salutis, "
   "and the custos-utriusque-tabulae magistrate. Gillespie's defeat "
   "of Selden on Erastianism was the Scottish commission's most "
   "consequential intervention.",
   overrides={
       'god_decree_order_of_decrees': 'Supralapsarian',
       'god_decree_covenant_of_redemption': 'Explicit-Developed',
   },
   anchor_persona_slugs=[
       'alexander-henderson', 'samuel-rutherford', 'george-gillespie',
       'robert-baillie', 'archibald-johnston-wariston',
       'john-maitland-lauderdale', 'john-campbell-loudoun',
       'john-kennedy-cassillis',
   ])

_s('dissenting-brethren',
   'The Five Dissenting Brethren (Independents)',
   'Westminster Assembly, 1644 (Apologeticall Narration)',
   'assembly-party',
   "The five ministers — Thomas Goodwin, Philip Nye, Sidrach Simpson, "
   "Jeremiah Burroughs, and William Bridge — who signed An "
   "Apologeticall Narration (1644), the formal statement of the "
   "Independent case at Westminster. Joined by William Greenhill, "
   "Joseph Caryl, Peter Sterry, and William Carter among others. "
   "They agreed with the Presbyterian majority on almost every "
   "doctrinal point but departed on ecclesiology: the keys of the "
   "kingdom belong to the local gathered congregation, not to a "
   "graded series of presbyterial courts. Synods advise but cannot "
   "bind. The Dissenting Brethren lost the polity vote but stayed "
   "at the Assembly and continued to vote on doctrine. Their "
   "ecclesiology was codified in the Savoy Declaration (1658).",
   overrides={
       'ecclesiology_worship_polity': 'Independent-Congregational',
       'ecclesiology_worship_censures_and_synods': 'Three-Degrees-With-Graded-Synods',
   },
   anchor_persona_slugs=[
       'thomas-goodwin', 'philip-nye', 'jeremiah-burroughs',
       'william-bridge', 'sidrach-simpson', 'william-greenhill',
       'joseph-caryl', 'peter-sterry',
   ])

_s('erastians',
   'The Erastians',
   'Westminster Assembly, 1645–1646',
   'assembly-party',
   "John Selden (the jurist and lay assessor), John Lightfoot and "
   "Thomas Coleman (the two ministerial Erastians), and Bulstrode "
   "Whitelocke. They argued that ecclesiastical jurisdiction belongs "
   "ultimately to the civil magistrate, not to a distinct church "
   "court. The Assembly rejected the position decisively — "
   "Gillespie's Aaron's Rod Blossoming (1646) is the canonical "
   "refutation — and WCF XXX.1 secured the church's independent "
   "jurisdiction. But the Erastians forced the Assembly to articulate "
   "the church-state distinction with more precision than any "
   "previous Reformed confession had managed.",
   overrides={
       'ecclesiology_worship_polity': 'Erastian',
       'civil_last_things_magistrate_role': 'Erastian-Magistrate-Over-Church',
   },
   anchor_persona_slugs=[
       'john-selden', 'john-lightfoot', 'thomas-coleman',
       'bulstrode-whitelocke',
   ])

_s('hypothetical-universalists',
   'The Hypothetical Universalists (Davenant-Calamy Line)',
   'Westminster Assembly, January 1646',
   'assembly-party',
   "The bloc — led by Edmund Calamy the Elder and including Richard "
   "Vines, Lazarus Seaman, John Arrowsmith, Stephen Marshall, "
   "William Spurstowe, Thomas Young, and Matthew Newcomen — that "
   "defended hypothetical universalism in the atonement: Christ's "
   "death is sufficient for all and intended conditionally for all "
   "who believe, while efficacious only for the elect. The position "
   "descended from John Davenant (the British delegate at the Synod "
   "of Dort who had taught Calamy at Pembroke Cambridge). The "
   "Confession's language (WCF III.6, VIII.5, VIII.8) was drafted "
   "broadly enough to accommodate both the strict-particularist "
   "majority and the hypothetical-universalist minority. This is "
   "perhaps the Standards' most significant deliberate latitude.",
   overrides={
       'god_decree_extent_of_atonement': 'Hypothetical-Universal',
   },
   anchor_persona_slugs=[
       'edmund-calamy-elder', 'richard-vines', 'lazarus-seaman',
       'john-arrowsmith', 'stephen-marshall', 'william-spurstowe',
       'thomas-young', 'matthew-newcomen',
   ])

_s('supralapsarians',
   'The Supralapsarians',
   'Westminster Assembly, 1644–1645',
   'assembly-party',
   "The minority who held that election and reprobation logically "
   "precede the decree to permit the fall. Led by the Prolocutor "
   "William Twisse (whose Vindiciae Gratiae is the most rigorous "
   "Latin defence of the position) and aligned with the Scottish "
   "Commissioners (Rutherford, Gillespie, Henderson). Thomas "
   "Goodwin, the chief Independent, was also supralapsarian. The "
   "Confession's decree chapter (III) was deliberately drafted to "
   "permit both supra- and infralapsarianism without imposing either "
   "— a latitude that remains confessionally operative in every "
   "Reformed body that subscribes to Westminster.",
   overrides={
       'god_decree_order_of_decrees': 'Supralapsarian',
       'god_decree_covenant_of_redemption': 'Explicit-Developed',
   },
   anchor_persona_slugs=[
       'william-twisse', 'samuel-rutherford', 'george-gillespie',
       'alexander-henderson', 'thomas-goodwin',
   ])

_s('reformed-episcopal-absentees',
   'The Reformed Episcopal Absentees',
   'Named to the Assembly, 1643 (declined)',
   'assembly-party',
   "The bishops and high-church divines who were named to the "
   "Assembly's original ordinance but refused to sit out of loyalty "
   "to episcopal polity and the king. The group includes James "
   "Ussher (Archbishop of Armagh, the most learned Reformed "
   "Episcopalian), Joseph Hall (Bishop of Norwich, whose Episcopacie "
   "by Divine Right provoked the Smectymnuan tracts), Ralph Brownrig "
   "(Bishop of Exeter), Robert Sanderson (the great casuist), Henry "
   "Hammond (royal chaplain, father of English biblical criticism), "
   "George Morley (later Bishop of Winchester), Thomas Fuller (the "
   "church historian), Thomas Westfield (Bishop of Bristol), Walter "
   "Balcanqual (Dean of Durham), and John Williams (Archbishop of "
   "York). Doctrinally they were mostly Calvinist; polity-wise they "
   "were episcopalian — retaining bishops as a third order of "
   "ministry while affirming Reformed doctrine. Their absence meant "
   "the Assembly's ecclesiology was decided without the strongest "
   "episcopal voices present.",
   overrides={
       'ecclesiology_worship_polity': 'Reformed-Episcopal',
       'ecclesiology_worship_regulative_principle': 'Normative-Whatever-Not-Forbidden',
   },
   anchor_persona_slugs=[
       'james-ussher', 'joseph-hall', 'ralph-brownrig',
       'robert-sanderson', 'henry-hammond', 'george-morley',
       'thomas-fuller', 'walter-balcanqual',
   ])


# ======================================================================
# II. RECEIVING TRADITIONS
# ======================================================================

_s('savoy-1658',
   'The Savoy Declaration (1658)',
   'Savoy Palace, London, 29 September – 12 October 1658',
   'receiving-tradition',
   "The Independent recension of the Westminster Confession, adopted "
   "by a conference of Independent ministers and churches at the "
   "Savoy Palace in London. Chaired by Philip Nye and Thomas Goodwin, "
   "the Savoy Declaration adopted the Westminster Confession nearly "
   "verbatim on doctrine (including the decree, justification, the "
   "law, and the sacraments) but rewrote the polity chapters to "
   "replace presbyterianism with gathered-church Independency and "
   "softened the magistrate chapters. The Savoy preface (by John "
   "Owen) is the most articulate Independent statement of confessional "
   "principle. The Savoy became the confessional standard of English "
   "Congregationalism and (via the Cambridge Platform and later "
   "revisions) of American Congregationalism.",
   overrides={
       'ecclesiology_worship_polity': 'Independent-Congregational',
       'civil_last_things_magistrate_role': 'Protective-Not-Directive (1788)',
   },
   anchor_persona_slugs=['thomas-goodwin', 'philip-nye'])

_s('particular-baptists-1689',
   'The Second London Confession (1689)',
   'London, 1677 (drafted); 1689 (published under toleration)',
   'receiving-tradition',
   "The Particular Baptist adaptation of the Westminster Confession, "
   "drafted in 1677 by Nehemiah Coxe and William Collins and "
   "published in 1689 after the Toleration Act. The 1689 Confession "
   "adopted Westminster's language de novo on virtually every "
   "doctrinal locus — the decree, justification, sanctification, "
   "the law, the last things — but departed sharply on baptism "
   "(believers only, by immersion), polity (congregational, not "
   "presbyterian), the covenant (denying the covenantal-continuity "
   "argument for paedobaptism), and the magistrate (disestablishment). "
   "The 1689 remains the confessional standard of Reformed Baptist "
   "churches worldwide.",
   overrides={
       'ecclesiology_worship_polity': 'Independent-Congregational',
       'covenant_children_of_believers': 'Credo-Baptist',
       'covenant_mosaic_covenant': 'Subservient-Covenant',
       'civil_last_things_magistrate_role': 'Protective-Not-Directive (1788)',
   },
   anchor_persona_slugs=[])

_s('american-1788-revision',
   'The American Presbyterian Revision (1788)',
   'Philadelphia Synod, 1787–1788',
   'receiving-tradition',
   "The revision of the Westminster Confession adopted by the "
   "first American Presbyterian General Assembly. The 1788 revision "
   "rewrote WCF XX.4, XXIII.3, and XXXI.2 to align with American "
   "disestablishment: the magistrate protects the church but does "
   "not prefer one denomination, suppress heresy, or call synods. "
   "The Pope-as-Antichrist identification in XXV.6 was also softened. "
   "The rest of the Confession — doctrine, soteriology, law, "
   "sacraments, polity — remained verbatim. The 1788 text is "
   "confessional for the PCA, OPC, and most American Presbyterian "
   "bodies. The major confessional fracture of the Westminster "
   "tradition.",
   overrides={
       'civil_last_things_magistrate_role': 'Protective-Not-Directive (1788)',
   },
   anchor_persona_slugs=[])

_s('free-church-scotland-1843',
   'The Free Church of Scotland (1843)',
   'Edinburgh, 18 May 1843 (the Disruption)',
   'receiving-tradition',
   "When 474 ministers (out of ~1,200) walked out of the General "
   "Assembly of the Church of Scotland on 18 May 1843 over the "
   "patronage question and state interference in spiritual matters, "
   "they constituted the Free Church of Scotland — confessionally "
   "committed to the Westminster Standards in the original 1647 "
   "Scottish text, including the custos-utriusque-tabulae magistrate "
   "clause. The Disruption was the most dramatic assertion of the "
   "anti-Erastian principle Gillespie had argued at Westminster. "
   "The Free Church preserved strict Sabbath observance, exclusive "
   "metrical psalmody, and the complete 1647 confessional text "
   "through the nineteenth and twentieth centuries.",
   anchor_persona_slugs=[])

_s('reformed-presbyterian-covenanters',
   'Reformed Presbyterian (Covenanter) Tradition',
   'Scotland, 1680s – present',
   'receiving-tradition',
   "The Reformed Presbyterian Church descends from the Cameronians — "
   "the strictest Covenanter wing that refused the Restoration "
   "settlement and continued to treat the Solemn League and Covenant "
   "as binding. The RPCNA (Reformed Presbyterian Church of North "
   "America) and the RPCS (Reformed Presbyterian Church of Scotland) "
   "retain the 1646 Westminster text in its entirety, including the "
   "custos-utriusque-tabulae magistrate clause, the Pope-as-Antichrist "
   "identification, and exclusive metrical psalmody. They are the "
   "most conservative confessional subscribers to Westminster.",
   anchor_persona_slugs=[])

_s('marrow-men',
   'The Marrow Men (1717–1722)',
   'Scotland, 1717–1722',
   'receiving-tradition',
   "When Thomas Boston rediscovered Edward Fisher's Marrow of Modern "
   "Divinity (1645) in 1700 and republished it with notes, the "
   "General Assembly of the Church of Scotland condemned it in 1720, "
   "and twelve ministers ('the Twelve Apostles') protested — the "
   "Marrow controversy. The Marrow Men (Boston, Ralph and Ebenezer "
   "Erskine, James Hog, and others) argued that the Westminster "
   "Standards permitted a freer offer of Christ than the Assembly's "
   "condemnation implied, and that the pactum salutis grounded a "
   "universal gospel offer even within particular redemption. The "
   "controversy is one of the most consequential post-Assembly "
   "readings of the Standards and shaped later Scottish free-offer "
   "theology.",
   overrides={
       'god_decree_covenant_of_redemption': 'Explicit-Developed',
       'soteriology_assurance': 'Both-Spirit-Witness-And-Marks',
   },
   anchor_persona_slugs=[])

_s('cumberland-presbyterians',
   'Cumberland Presbyterians (1810)',
   'Dickson County, Tennessee, 1810',
   'receiving-tradition',
   "The Cumberland Presbyterian Church was formed in 1810 on the "
   "American frontier by ministers who found Westminster's doctrine "
   "of the decree too restrictive for frontier revivalism. They "
   "adopted a revised confession (1814, further revised 1883) that "
   "softened the decree: God sincerely desires the salvation of all, "
   "election is not unconditional in the hard Calvinist sense, and "
   "the atonement is general. They retained Westminster's polity, "
   "Sabbath, and sacramental theology. The Cumberland revision is "
   "the most explicitly Arminian-softened offshoot of the Westminster "
   "tradition.",
   overrides={
       'god_decree_order_of_decrees': 'Infralapsarian',
       'god_decree_extent_of_atonement': 'Hypothetical-Universal',
       'god_decree_reprobation': 'Conditional-On-Foreseen-Unbelief',
       'soteriology_effectual_calling': 'Resistible-Sufficient-Grace',
       'soteriology_perseverance': 'Conditional-On-Continued-Faith',
   },
   anchor_persona_slugs=[])

_s('opc-1936',
   'The Orthodox Presbyterian Church (1936)',
   'Philadelphia, 11 June 1936',
   'receiving-tradition',
   "Founded by J. Gresham Machen and other confessional Presbyterians "
   "who left the PCUSA over the Auburn Affirmation (1924) and the "
   "modernist controversy. The OPC subscribes to the Westminster "
   "Standards in the American 1788 text, rejecting the 1903 PCUSA "
   "Declaratory Statements that had softened the decree and added a "
   "chapter on the Holy Spirit. The OPC is arguably the most "
   "rigorously Westminster-subscribing American Presbyterian body — "
   "its confessional practice requires strict subscription to the "
   "Standards as the system of doctrine taught in Scripture.",
   overrides={
       'civil_last_things_magistrate_role': 'Protective-Not-Directive (1788)',
   },
   anchor_persona_slugs=[])

_s('pca-1973',
   'The Presbyterian Church in America (1973)',
   'Birmingham, Alabama, 4 December 1973',
   'receiving-tradition',
   "The PCA was formed by conservative Southern Presbyterians who "
   "left the PCUS (the southern mainline body) over doctrinal "
   "liberalism and the 1969 plan of reunion with the UPCUSA. The "
   "PCA subscribes to the Westminster Standards in the American "
   "1788 text and is now the largest confessionally Westminster "
   "Presbyterian body in the United States (~380,000 members). Its "
   "confessional practice — 'good faith subscription' with declared "
   "exceptions — is slightly broader than the OPC's strict "
   "subscription but still anchored in Westminster.",
   overrides={
       'civil_last_things_magistrate_role': 'Protective-Not-Directive (1788)',
   },
   anchor_persona_slugs=[])
