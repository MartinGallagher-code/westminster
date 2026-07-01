"""Westminster Cruxes — the hard points at which the Assembly navigated
competing positions, reached confessional language, or deliberately
preserved latitude.

A 'crux' (Latin *crux*: cross, hard problem; pl. *cruces* / *cruxes*) is
a Reformed-scholastic term for a difficult interpretive or doctrinal
knot — a point at which a tradition has to choose, or refuse to choose,
between live alternatives. The Westminster Assembly worked through
several dozen such cruxes from July 1643 to early 1649; this file
collects the most consequential, in roughly the order they bear on
the loci of the ontology.

Each crux has:

  - ``slug`` / ``number`` / ``title`` / ``dates``
  - ``locus_key`` and ``attribute_keys`` — which locus and which
    attribute(s) of the Westminster ontology the crux bears on
  - ``tagline`` — one-line characterisation
  - ``background`` — the state of the question going into the Assembly
  - ``summary`` — what the Assembly did with the question
  - ``parties`` — the discernible positions, with persona slugs
  - ``outcome`` — ``settled-clear``, ``settled-with-latitude``,
    ``rejected-alternative``, ``deferred``, or ``mixed``
  - ``language`` — the actual confessional formulation adopted
  - ``legacy`` — how the question continued after the Assembly

Outcomes:

  - ``settled-clear`` — the Standards take a definite position and
    reject the alternatives (e.g. presbyterian polity; particular
    atonement language; the regulative principle)
  - ``settled-with-latitude`` — the Standards adopt language broad
    enough to accommodate two live positions (e.g. supra- and
    infralapsarianism on the decree; the Davenant-Rutherford spread
    on the atonement's intended sufficiency)
  - ``rejected-alternative`` — the position rejected is named or
    clearly excluded (e.g. Erastianism; Roman ex opere operato;
    antinomian rejection of the law's third use)
  - ``mixed`` — the Standards take a position but leave significant
    ambiguity later traditions worked over (e.g. the magistrate
    question, revised in 1788)
"""

from .data import WESTMINSTER_BASELINE_ATTRS


CRUXES = []
_COUNTER = [0]


def _c(slug, title, dates, *, locus_key, attribute_keys=None,
       tagline, background, summary, parties=None, outcome,
       language=None, legacy=None, references=None):
    _COUNTER[0] += 1
    CRUXES.append({
        'slug': slug,
        'number': _COUNTER[0],
        'title': title,
        'dates': dates,
        'locus_key': locus_key,
        'attribute_keys': attribute_keys or [],
        'tagline': tagline,
        'background': background,
        'summary': summary,
        'parties': parties or [],
        'outcome': outcome,
        'language': language or '',
        'legacy': legacy or '',
        'references': references or [],
    })


def get_crux_by_slug(slug):
    for c in CRUXES:
        if c.get('slug') == slug:
            return c
    return None


def cruxes_by_locus(locus_key):
    return [c for c in CRUXES if c.get('locus_key') == locus_key]


_PERSONA_CRUX_INDEX = None


def cruxes_for_persona(persona_slug):
    """Return a list of ``{'crux', 'party_name', 'position'}`` entries
    for every appearance of ``persona_slug`` as a party in any crux.

    The reverse index is built lazily on first access.
    """
    global _PERSONA_CRUX_INDEX
    if _PERSONA_CRUX_INDEX is None:
        idx = {}
        for crux in CRUXES:
            for party in crux.get('parties', []):
                for pslug in party.get('persona_slugs', []):
                    idx.setdefault(pslug, []).append({
                        'crux': crux,
                        'party_name': party.get('name', ''),
                        'position': party.get('position', ''),
                    })
        _PERSONA_CRUX_INDEX = idx
    return _PERSONA_CRUX_INDEX.get(persona_slug, [])


# ======================================================================
# I. SCRIPTURE
# ======================================================================

_c('the-canon-and-the-apocrypha', 'The Canon and the Apocrypha', 'August 1645',
   locus_key='scripture',
   attribute_keys=['scripture_canon'],
   tagline='The Assembly drew a sharper line against the Apocrypha than Article VI of the Thirty-Nine Articles.',
   background=(
       "The Tridentine session IV (1546) had decreed that the books of Tobit, "
       "Judith, Wisdom, Sirach, Baruch, 1-2 Maccabees, and the additions to "
       "Daniel and Esther were canonical and to be received 'with equal pious "
       "affection' (*pari pietatis affectu*) alongside the Hebrew Bible. The "
       "Reformed had unanimously rejected this — Calvin in the *Institutes*, "
       "the Belgic Confession (1561), the Helvetic Confessions, and the Synod "
       "of Dort — but the Church of England's Article VI (1571) had taken a "
       "milder line: the Apocrypha was not canonical for doctrine but might "
       "still be read 'for example of life and instruction of manners.' "
       "Lancelot Andrewes and the moderate-Anglican tradition kept the "
       "Apocrypha in the lectionary and on the printed page of the Authorized "
       "Version (1611) between the Testaments."
   ),
   summary=(
       "The Assembly's debate on canon ran in August 1645 alongside the "
       "drafting of WCF I.2-3. The Reformed majority pressed for the sharper "
       "Continental line; no significant voice argued the Article VI middle "
       "position; and Selden, who might have done so on antiquarian grounds, "
       "did not. The English bishops who would have defended the Article VI "
       "language were either absent (Ussher, Hall, Brownrig) or excluded "
       "(Featley, expelled by then). The committee's report carried."
   ),
   parties=[
       {
           'name': 'The Reformed majority',
           'persona_slugs': ['edmund-calamy-elder', 'stephen-marshall', 'cornelius-burgess',
                             'thomas-gataker', 'anthony-tuckney'],
           'position': "The Apocrypha is 'no part of the canon of Scripture' "
                       "and is to be treated as 'other human writings' — not "
                       "to be used for doctrine, not to be 'made use of' in "
                       "worship beyond such reading as one would give to any "
                       "pious but uninspired text.",
       },
       {
           'name': 'The (absent) Article VI position',
           'persona_slugs': ['james-ussher', 'joseph-hall', 'ralph-brownrig'],
           'position': "The Apocrypha is not canonical for doctrine but is "
                       "useful 'for example of life and instruction of "
                       "manners' and properly read in public worship as "
                       "the Anglican lectionary prescribed.",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF I.3: 'The books commonly called Apocrypha, not being of divine "
       "inspiration, are no part of the canon of Scripture; and therefore "
       "are of no authority in the Church of God, nor to be any otherwise "
       "approved, or made use of, than other human writings.'"
   ),
   legacy=(
       "The Westminster line on the Apocrypha became the standard "
       "English-speaking Reformed position. Printed Bibles in Reformed "
       "use omitted the Apocrypha entirely after the mid-17th century — "
       "the British and Foreign Bible Society's 1826 decision to exclude "
       "it from its editions confirmed the practice that Westminster had "
       "made confessional."
   ),
   references=['WCF I.2', 'WCF I.3'])


_c('good-and-necessary-consequence', 'Good and Necessary Consequence',
   '1644–1645',
   locus_key='scripture',
   attribute_keys=['scripture_sufficiency'],
   tagline='How does Scripture warrant doctrines it does not explicitly state?',
   background=(
       "Reformed theology had always claimed sufficiency for Scripture — "
       "*sola scriptura* — but the polemic against the Socinians (who "
       "rejected the Trinity on the ground that the term *Trinitas* is not "
       "in Scripture) and against the Roman appeal to unwritten tradition "
       "required a more articulated answer. How could Reformed divines "
       "ground the homoousion, paedobaptism, the Sabbath's transfer to the "
       "Lord's Day, and the bi-covenantal structure of redemption, none of "
       "which are stated in so many words? The Polish Socinians (Crellius, "
       "Schlichting) had argued that whatever was not in the *very letter* "
       "of Scripture was not binding. The Reformed needed a doctrine of "
       "warranted inference."
   ),
   summary=(
       "Anthony Tuckney's drafting committee produced the phrase that "
       "became WCF I.6: doctrines binding on conscience are those "
       "'expressly set down in Scripture, *or by good and necessary "
       "consequence may be deduced from Scripture*.' The phrase walked a "
       "fine line — broad enough to ground Trinitarian and confessional "
       "deduction, narrow enough to exclude tradition and mere reason — "
       "and was defended on the floor by Tuckney, Cheynell (who wielded "
       "it against the Socinians), and Reynolds. No significant voice "
       "opposed it; the Assembly's anti-Socinian and anti-Roman "
       "consensus held."
   ),
   parties=[
       {
           'name': 'The "good and necessary consequence" drafters',
           'persona_slugs': ['anthony-tuckney', 'francis-cheynell',
                             'edward-reynolds', 'cornelius-burgess'],
           'position': "Scripture is sufficient not only in what it "
                       "expressly states but also in what may be drawn "
                       "from it by good and necessary consequence — the "
                       "deductive warrant that grounds the Trinity, "
                       "paedobaptism, the Lord's Day, and the confessional "
                       "system as a whole.",
       },
       {
           'name': 'The Socinian alternative (rejected, not present)',
           'persona_slugs': [],
           'position': "Only what is expressly stated in Scripture binds "
                       "the conscience; deduced doctrines are human "
                       "inferences and not warrants for confessional "
                       "subscription. Crellius and the Polish Socinians "
                       "pressed this against Trinitarian creeds.",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF I.6: 'The whole counsel of God concerning all things necessary "
       "for his own glory, man's salvation, faith, and life, is either "
       "expressly set down in Scripture, or by good and necessary "
       "consequence may be deduced from Scripture: unto which nothing at "
       "any time is to be added, whether by new revelations of the Spirit, "
       "or traditions of men.'"
   ),
   legacy=(
       "The clause has been the bedrock of Reformed systematic theology "
       "ever since. It is invoked in every subsequent confessional "
       "controversy that turns on whether a doctrine binds — the Marrow "
       "controversy (1717-22), the New Side / Old Side disputes, the "
       "1903 PCUSA revisions over the decree, and twentieth-century "
       "debates over inerrancy. Twentieth-century theonomists and "
       "general-equity theorists have stretched the clause in various "
       "directions; the OPC and PCA confessional standards retain "
       "Westminster's exact phrasing."
   ),
   references=['WCF I.6'])


# ======================================================================
# II. GOD & DECREE
# ======================================================================

_c('the-order-of-the-decrees', 'The Order of the Decrees',
   '1644–1645',
   locus_key='god_decree',
   attribute_keys=['god_decree_order_of_decrees'],
   tagline='Did God decree the election of particular persons before or after the fall?',
   background=(
       "The Reformed scholastic question of the order of the decrees had "
       "split the tradition since Theodore Beza's *Tabula Praedestinationis* "
       "(1555). The supralapsarian held that election and reprobation of "
       "particular persons logically *precede* the decree to permit the "
       "fall: God chose the elect 'above' (*supra*) the lapse, treating "
       "humans as creabiles et labiles — creatable and apt to fall — but "
       "not yet fallen. The infralapsarian held that the decree of election "
       "and reprobation logically *follows* the decree to permit the fall: "
       "God chose from a fallen mass. Dort (1618-19) had refused to "
       "adjudicate; the Synod's Canons accommodated both positions. The "
       "question was technical but theologically loaded: supralapsarianism "
       "made God's sovereignty more starkly the *whole* cause of the "
       "elect/reprobate distinction, infralapsarianism made the fall the "
       "context for the distinction."
   ),
   summary=(
       "The Prolocutor William Twisse was a famous supralapsarian — "
       "*Vindiciae Gratiae* (1632) is the most rigorous Latin defence of "
       "the position in any Reformed dogmatics — and on the Scottish side "
       "Rutherford and Gillespie tilted supra. The English majority "
       "(Calamy, Reynolds, Marshall, Tuckney) was infralapsarian. Rather "
       "than fight the matter to a confessional verdict, the drafters "
       "produced language deliberately broad enough to permit both "
       "readings. WCF III.7's phrasing — God 'was pleased…to pass by' the "
       "rest of mankind 'for the glory of his sovereign power' — does not "
       "specify whether the passing-by is logically before or after the "
       "fall, and is compatible with either reading."
   ),
   parties=[
       {
           'name': 'Supralapsarians',
           'persona_slugs': ['william-twisse', 'samuel-rutherford',
                             'george-gillespie', 'alexander-henderson',
                             'thomas-goodwin'],
           'position': "The decree of election and reprobation logically "
                       "precedes the decree to permit the fall; God's "
                       "sovereign choice of the elect is the foundation "
                       "of the whole order of redemption, not a response "
                       "to a fallen condition.",
       },
       {
           'name': 'Infralapsarians',
           'persona_slugs': ['edmund-calamy-elder', 'edward-reynolds',
                             'stephen-marshall', 'anthony-tuckney',
                             'cornelius-burgess'],
           'position': "The decree to permit the fall logically precedes "
                       "the decree of election and reprobation; God chose "
                       "the elect from a fallen and condemnable mass, so "
                       "that mercy is the gracious side and justice the "
                       "punitive side of one decree.",
       },
   ],
   outcome='settled-with-latitude',
   language=(
       "WCF III.7: 'The rest of mankind God was pleased, according to "
       "the unsearchable counsel of his own will, whereby he extendeth "
       "or withholdeth mercy, as he pleaseth, for the glory of his "
       "sovereign power over his creatures, to pass by; and to ordain "
       "them to dishonor and wrath for their sin, to the praise of his "
       "glorious justice.'"
   ),
   legacy=(
       "The deliberate latitude has proved durable. Both supra- and "
       "infralapsarian Reformed divines have claimed Westminster as "
       "consistent with their reading: Herman Hoeksema and the "
       "Protestant Reformed have read it supra; Charles Hodge and the "
       "Princeton tradition have read it infra. The 1903 PCUSA "
       "Declaratory Statement explicitly affirmed that the Confession "
       "permits both positions — language Westminster's own drafters "
       "would have recognised as fair."
   ),
   references=['WCF III.6-7'])


_c('the-extent-of-the-atonement', 'The Extent of the Atonement',
   'January 1646',
   locus_key='god_decree',
   attribute_keys=['god_decree_extent_of_atonement'],
   tagline="One of the Assembly's bruising sessions: Christ died for whom?",
   background=(
       "Dort (1618-19) had taught that Christ's death was 'sufficient for "
       "all, efficient for the elect' (Canons II.3 and II.8), language "
       "broad enough to accommodate both strict particularists (who said "
       "Christ died with intent and design only for the elect) and "
       "hypothetical universalists (who said Christ died sufficiently and "
       "with conditional intent for all, and efficaciously for the elect). "
       "John Davenant, the British delegate at Dort, had developed the "
       "hypothetical-universalist line in *Dissertatio de Morte Christi* "
       "(1650, but lectures from the 1620s). At Westminster the question "
       "came up because the Assembly had to draft the clause on Christ's "
       "purchase in WCF III.6 and the chapter on Christ the Mediator "
       "(VIII), and the two parties did not agree on what language to use."
   ),
   summary=(
       "In a famous session in January 1646 Edmund Calamy the Elder, one "
       "of the most senior London Presbyterians and a Pembroke Cambridge "
       "man trained under Davenant, defended hypothetical universalism on "
       "the floor: Christ's death is sufficient for all, intended "
       "conditionally for all (if they believe), and efficaciously for "
       "the elect. Richard Vines, Lazarus Seaman, John Arrowsmith, and "
       "Stephen Marshall held similar positions. Samuel Rutherford and "
       "George Gillespie pressed strict particularism. The Assembly's "
       "majority were particularists, but the hypothetical-universalist "
       "bloc was substantial enough that the drafters again chose language "
       "broad enough to accommodate both. WCF III.6 and VIII.5, 8 secure "
       "that Christ 'purchased' redemption only for the elect — the strict "
       "particularist requirement — while not excluding the wider "
       "intended-sufficiency reading."
   ),
   parties=[
       {
           'name': 'Strict particularists',
           'persona_slugs': ['samuel-rutherford', 'george-gillespie',
                             'alexander-henderson', 'thomas-goodwin',
                             'john-arrowsmith'],
           'position': "Christ's death is intended, designed, and applied "
                       "only for the elect. Its sufficiency 'for all' is "
                       "an intrinsic infinite worth, not a conditional "
                       "design. To say Christ died for the non-elect in "
                       "any sense compromises the unity of God's purpose.",
       },
       {
           'name': 'Hypothetical universalists (the Davenant-Calamy line)',
           'persona_slugs': ['edmund-calamy-elder', 'richard-vines',
                             'lazarus-seaman', 'stephen-marshall',
                             'william-spurstowe', 'thomas-young',
                             'matthew-newcomen'],
           'position': "Christ's death is sufficient for all and "
                       "intended conditionally for all who believe, while "
                       "efficacious for the elect alone. The conditional "
                       "design grounds the sincere universal offer of "
                       "the gospel and protects God's revealed will to "
                       "save sinners.",
       },
   ],
   outcome='settled-with-latitude',
   language=(
       "WCF VIII.5: 'The Lord Jesus, by his perfect obedience, and "
       "sacrifice of himself, which he, through the eternal Spirit, once "
       "offered up unto God, hath fully satisfied the justice of his "
       "Father; and purchased, not only reconciliation, but an "
       "everlasting inheritance in the kingdom of heaven, for all those "
       "whom the Father hath given unto him.' "
       "WCF VIII.8: 'To all those for whom Christ hath purchased "
       "redemption, he doth certainly and effectually apply and "
       "communicate the same…'"
   ),
   legacy=(
       "The deliberate latitude has been disputed ever since. John Owen's "
       "*Death of Death in the Death of Christ* (1647) is the classic "
       "Reformed defence of strict particularism, written explicitly to "
       "close down the Davenant reading. Richard Baxter's *Universal "
       "Redemption* (1675) revived the hypothetical-universalist line. "
       "The Marrow controversy (1717-22) in Scotland turned partly on "
       "whether the Confession's language permitted the 'crisp' offer of "
       "Christ as a Saviour to all. Modern Reformed scholarship "
       "(Moore's *English Hypothetical Universalism*, 2007) has "
       "rehabilitated the Calamy-Davenant reading as a position the "
       "Confession's drafters knew about and accommodated."
   ),
   references=['WCF III.6', 'WCF VIII.5', 'WCF VIII.8'])


_c('the-decree-of-reprobation', 'The Decree of Reprobation',
   '1645',
   locus_key='god_decree',
   attribute_keys=['god_decree_reprobation'],
   tagline='Does God positively decree the damnation of the reprobate, or merely pass them by?',
   background=(
       "Reformed theology had always held that God's eternal counsel "
       "concerns both the elect and the non-elect, but how that was to "
       "be stated varied sharply. The hardest reading — Beza's, sometimes "
       "Twisse's — described reprobation as a positive divine decree, "
       "parallel to election: God positively decrees the damnation of "
       "the reprobate as an end. The milder reading — Calvin's late "
       "*Institutes*, the Synod of Dort, most English divines — "
       "distinguished *preterition* (God's passing by the non-elect) "
       "from *praedamnation* (the just condemnation that follows on the "
       "non-elect's sin). On the milder reading, election is positive "
       "and reprobation is just."
   ),
   summary=(
       "The Assembly took the milder line but with a sharpening clause "
       "about the divine decree itself. WCF III.7 distinguishes "
       "preterition (God 'was pleased…to pass by') from the eventual "
       "condemnation ('to ordain them to dishonor and wrath *for their "
       "sin*'). The 'for their sin' clause secures that the execution of "
       "reprobation is just — the non-elect are condemned for their sin, "
       "not despite their innocence — while the 'pass by' language keeps "
       "the eternal decree's asymmetry between mercy (positively given) "
       "and judgement (justly administered). Twisse may have wished for "
       "sharper supralapsarian language; the English majority did not."
   ),
   parties=[
       {
           'name': 'The drafting majority: preterition + just condemnation',
           'persona_slugs': ['edmund-calamy-elder', 'edward-reynolds',
                             'anthony-tuckney', 'stephen-marshall'],
           'position': "Reprobation has two moments: the eternal decree "
                       "to pass by the non-elect (preterition), and the "
                       "just condemnation of the non-elect for their "
                       "sin. The decree is sovereign; the condemnation "
                       "is just.",
       },
       {
           'name': 'Stricter supralapsarian inflection (minority)',
           'persona_slugs': ['william-twisse', 'samuel-rutherford'],
           'position': "Reprobation is a positive eternal decree to "
                       "damnation, parallel in structure to election; "
                       "the 'pass by' language is too mild and "
                       "underplays the symmetry of the decree.",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF III.7: 'The rest of mankind God was pleased…to pass by; "
       "and to ordain them to dishonor and wrath for their sin, to "
       "the praise of his glorious justice.'"
   ),
   legacy=(
       "The carefully balanced clause has been read both ways. Strict "
       "Reformed dogmatics (Hoeksema, Engelsma) have argued that the "
       "'to ordain them to dishonor and wrath' clause grounds a positive "
       "decree of reprobation. Most Reformed divines — Hodge, Bavinck, "
       "Berkhof — have read it as preterition followed by just "
       "condemnation. The clause has been the basis of every Reformed "
       "discussion of double predestination since."
   ),
   references=['WCF III.7'])


_c('the-covenant-of-redemption', 'The Covenant of Redemption',
   '1645–1647',
   locus_key='god_decree',
   attribute_keys=['god_decree_covenant_of_redemption'],
   tagline='Is there an eternal covenant between the Father and the Son for the elect?',
   background=(
       "By the 1640s a development was emerging in Reformed dogmatics: "
       "alongside the bi-covenantal scheme of works (with Adam) and grace "
       "(with the elect in Christ), some divines posited a third, eternal "
       "covenant between the persons of the Trinity — the *pactum salutis* "
       "or covenant of redemption, in which the Father appoints the Son "
       "as Mediator and the Son freely accepts the office for the elect. "
       "The idea had antecedents in earlier Reformed thought (Olevianus, "
       "Witsius drew on it later) but had not been confessionally stated. "
       "Cocceius, on the Continent, would later make it the architectural "
       "backbone of his system."
   ),
   summary=(
       "The Assembly was sympathetic but did not formalise the pactum as "
       "a distinct third covenant. WCF VIII.1 — 'It pleased God, in his "
       "eternal purpose, to choose and ordain the Lord Jesus, his only "
       "begotten Son, to be the Mediator between God and man' — gives "
       "the pactum its substance without the developed scholastic "
       "apparatus. The Larger Catechism Q. 31 goes a step further: 'With "
       "whom was the covenant of grace made? The covenant of grace was "
       "made with Christ as the second Adam, and in him with all the "
       "elect as his seed.' This is materially the pactum but stitched "
       "into the covenant of grace rather than detached as a third "
       "covenant. The Standards therefore *affirm-implicitly* without "
       "going as far as the Cocceian-Witsian tri-covenantal scheme."
   ),
   parties=[
       {
           'name': 'The implicit-affirmation drafters',
           'persona_slugs': ['anthony-tuckney', 'edward-reynolds',
                             'herbert-palmer', 'edmund-calamy-elder'],
           'position': "The substance of the pactum is biblical — the "
                       "Father chooses the Son as Mediator (Ps. 2, John "
                       "17, Heb. 5) — and should be confessionally "
                       "affirmed, but a formal third covenant is "
                       "scholastic elaboration the Standards need not "
                       "adopt.",
       },
       {
           'name': 'The explicit-developed wing',
           'persona_slugs': ['samuel-rutherford', 'george-gillespie',
                             'thomas-goodwin'],
           'position': "The pactum is a distinct eternal covenant "
                       "between the persons, grounding the bi-covenantal "
                       "structure of history. Rutherford's *The Covenant "
                       "of Life Opened* (1655) develops the position at "
                       "length.",
       },
   ],
   outcome='mixed',
   language=(
       "WCF VIII.1: 'It pleased God, in his eternal purpose, to choose "
       "and ordain the Lord Jesus, his only begotten Son, to be the "
       "Mediator between God and man…' "
       "Larger Catechism Q. 31: 'The covenant of grace was made with "
       "Christ as the second Adam, and in him with all the elect as his "
       "seed.'"
   ),
   legacy=(
       "Witsius's *De Oeconomia Foederum Dei cum Hominibus* (1677), "
       "Boston's *A View of the Covenant of Grace*, and Hodge's "
       "*Systematic Theology* (1872-73) all develop the pactum as a "
       "formal third covenant on warrants the Standards provided. The "
       "Marrow men in early-18th-century Scotland made the pactum "
       "central to their preaching of the free offer. The 1689 "
       "Particular Baptist Confession adopted the substance of "
       "Westminster on this point but with a sharper distinction "
       "between the pactum and the covenant of grace."
   ),
   references=['WCF VIII.1', 'LC Q. 31'])


# ======================================================================
# III. COVENANT
# ======================================================================

_c('the-mosaic-covenant', 'The Mosaic Covenant',
   '1645–1646',
   locus_key='covenant',
   attribute_keys=['covenant_mosaic_covenant'],
   tagline='Sinai: republication of the covenant of works, or administration of the covenant of grace?',
   background=(
       "The Reformed had to account for the relation of the Sinaitic "
       "covenant to the bi-covenantal scheme. Two options were live: "
       "(1) Sinai is one administration of the covenant of grace, "
       "containing the moral law as the rule of life for an already-"
       "redeemed people; (2) Sinai is in some sense a republication of "
       "the covenant of works in a typological mode, alongside the "
       "covenant of grace which continues underneath. The first reading "
       "(Calvin, Bullinger, Ursinus) emphasised continuity. The second "
       "(developing in Owen, Petto, Boston after the Assembly) emphasised "
       "the law's pedagogical function and the typological structure of "
       "the OT economy. A third position — the 'subservient covenant' "
       "view of Cameron and the Particular Baptists — treated Sinai as a "
       "third covenant subservient to grace, distinct from both works and "
       "grace proper."
   ),
   summary=(
       "WCF VII.5-6 places the Mosaic firmly within the covenant of grace "
       "as one of its administrations. There is no republication-of-works "
       "language. The Mosaic is the time when the covenant of grace was "
       "administered 'under the law' — by promises, prophecies, "
       "sacrifices, circumcision, the paschal lamb, and other types and "
       "ordinances delivered to the Jews 'all foresignifying Christ to "
       "come' — and is unified in substance with the gospel "
       "administration which follows. The republication view that would "
       "develop after the Assembly is not adopted, though the language "
       "does not exclude all forms of it."
   ),
   parties=[
       {
           'name': 'The administration-of-grace drafters',
           'persona_slugs': ['anthony-tuckney', 'edmund-calamy-elder',
                             'edward-reynolds', 'francis-roberts'],
           'position': "The Mosaic dispensation is one administration of "
                       "the one covenant of grace, differing from the "
                       "New Testament administration in form but not in "
                       "substance. The moral law given at Sinai is the "
                       "rule of life for an already redeemed people, "
                       "not a republication of the covenant of works.",
       },
       {
           'name': 'Republication-leaning (not pressed at the Assembly)',
           'persona_slugs': [],
           'position': "Sinai re-publishes the covenant of works in a "
                       "typological mode alongside the covenant of "
                       "grace; the law functions as a pedagogue driving "
                       "Israel to Christ. (Developed later by Owen, "
                       "Petto, Boston, and the 'Marrow' tradition.)",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF VII.5: 'This covenant was differently administered in the "
       "time of the law, and in the time of the gospel: under the law, "
       "it was administered by promises, prophecies, sacrifices, "
       "circumcision, the paschal lamb, and other types and ordinances "
       "delivered to the people of the Jews, all foresignifying Christ "
       "to come; which were, for that time, sufficient and efficacious, "
       "through the operation of the Spirit, to instruct and build up "
       "the elect in faith in the promised Messiah…' "
       "WCF VII.6: '…There are not therefore two covenants of grace, "
       "differing in substance, but one and the same, under various "
       "dispensations.'"
   ),
   legacy=(
       "John Owen's *Exposition of Hebrews* (1668-84) developed the "
       "republication thesis at length, holding the Sinaitic covenant "
       "to be in some respect a covenant of works re-published, while "
       "the covenant of grace continued underneath. Thomas Boston and "
       "the Marrow men carried the position forward in Scotland. "
       "Modern Reformed debate (the OPC report on the doctrine of "
       "republication, 2016) has revisited whether the post-Assembly "
       "republication readings are compatible with WCF VII.5-6's "
       "deliberately unified language."
   ),
   references=['WCF VII.5', 'WCF VII.6', 'WCF XIX.2'])


_c('the-children-of-believers', 'The Children of Believers and the Sign of the Covenant',
   '1645',
   locus_key='covenant',
   attribute_keys=['covenant_children_of_believers'],
   tagline='Who belongs in the visible covenant, and what is the sign?',
   background=(
       "Reformed paedobaptism rested on the continuity of the covenant: "
       "the children of believers, included in Abraham's covenant by "
       "circumcision (Gen. 17), are included in the same covenant of "
       "grace under the New Testament administration and receive its "
       "sign (baptism). Particular Baptists, gathering in London in the "
       "1640s and publishing their First London Confession in 1644, "
       "denied this continuity: only professing believers and their "
       "profession-marked baptism belong to the visible covenant. The "
       "Anabaptists more broadly were a long-standing Reformed target. "
       "But Antinomians and some radical Independents also pressed "
       "credobaptist arguments."
   ),
   summary=(
       "The Assembly affirmed paedobaptism without significant internal "
       "dissent — even the Independent Dissenting Brethren held it. WCF "
       "XXV.2 includes 'all those throughout the world that profess the "
       "true religion, together with their children' in the visible "
       "church. XXVIII.4 makes baptism the sign that 'not only those that "
       "do actually profess faith in and obedience unto Christ, but also "
       "the infants of one or both believing parents, are to be baptized.' "
       "The 1644 First London Confession (Particular Baptist) is rejected "
       "implicitly by the Standards' adoption of the covenantal-continuity "
       "argument."
   ),
   parties=[
       {
           'name': 'The paedobaptist consensus (Presbyterian + Independent)',
           'persona_slugs': ['edmund-calamy-elder', 'samuel-rutherford',
                             'thomas-goodwin', 'philip-nye',
                             'william-bridge', 'anthony-tuckney'],
           'position': "The covenant of grace, one in substance through "
                       "both testaments, includes the children of "
                       "believers and gives them its sign. Baptism "
                       "replaces circumcision as the covenant sign "
                       "(Col. 2:11-12).",
       },
       {
           'name': 'The credobaptist alternative (rejected; outside the Assembly)',
           'persona_slugs': [],
           'position': "Only those who profess faith are members of the "
                       "visible covenant and receive its sign. The "
                       "covenant under the New Testament administration "
                       "is differently structured from the Abrahamic, "
                       "with believer-baptism the proper sign. "
                       "Articulated in the First London Confession "
                       "(1644) and later the 1689 Second London "
                       "Confession.",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF XXVIII.4: 'Not only those that do actually profess faith "
       "in and obedience unto Christ, but also the infants of one or "
       "both believing parents, are to be baptized.'"
   ),
   legacy=(
       "The 1689 Particular Baptist Second London Confession — which "
       "adopted the rest of the Westminster Confession nearly verbatim "
       "— rewrote chapter XXVIII on baptism along credobaptist lines, "
       "providing the most thorough Reformed credobaptist confessional "
       "statement. The Halfway Covenant (1657, 1662) in New England "
       "extended visible covenant membership to baptised non-communicants' "
       "children — an innovation Westminster's drafters would have "
       "found puzzling. The Edwards-Stoddard dispute over the Lord's "
       "Supper (1748-50) turned partly on whether the Halfway Covenant "
       "was a legitimate development of WCF XXV.2."
   ),
   references=['WCF XXV.2', 'WCF XXVIII.4'])


# ======================================================================
# IV. CHRISTOLOGY
# ======================================================================

_c('active-obedience-imputation', "The Imputation of Christ's Active Obedience",
   'August–October 1645',
   locus_key='christology',
   attribute_keys=['christology_active_obedience_imputation',
                   'soteriology_justification_ground'],
   tagline='Is Christ’s law-keeping, as well as his suffering, imputed to the justified believer?',
   background=(
       "Johannes Piscator (Herborn) had argued, against Calvin and Beza, "
       "that only Christ's passive obedience — his suffering of the curse "
       "— is imputed to the believer. His active obedience to the law, "
       "Piscator held, was required for Christ's own person as a man under "
       "the law; he did not perform it 'in our place' for imputation. The "
       "consequence was a doctrine of justification by Christ's "
       "punishment-bearing alone, with the believer's obedience following "
       "as the believer's own duty. The mainline Reformed (Ursinus, "
       "Polanus, the Synod of Dort, Davenant, Owen later) held both active "
       "and passive obedience to be imputed: Christ's whole righteousness "
       "— his law-keeping and his curse-bearing — is the believer's "
       "justifying righteousness."
   ),
   summary=(
       "The Assembly debated the question hard through August-October "
       "1645, with Thomas Gataker, Richard Vines, William Twisse, and "
       "Daniel Featley reportedly siding with Piscator on imputation (a "
       "minority view); George Walker, Anthony Burgess, Edward Reynolds, "
       "and most others insisting that both active and passive obedience "
       "are imputed. The drafting committee resolved on language that "
       "secured the mainline position: WCF XI.3 speaks of 'the whole "
       "obedience and satisfaction of Christ' being imputed in "
       "justification, and VIII.5 includes both 'his perfect obedience' "
       "and 'sacrifice of himself' in Christ's mediatorial work. The "
       "Piscatorian minority lost the drafting fight."
   ),
   parties=[
       {
           'name': 'Both active and passive obedience imputed (majority)',
           'persona_slugs': ['george-walker', 'anthony-burgess',
                             'edward-reynolds', 'edmund-calamy-elder',
                             'samuel-rutherford', 'george-gillespie'],
           'position': "Christ's whole righteousness — his perfect "
                       "law-keeping (active obedience) and his "
                       "curse-bearing (passive obedience) — is imputed "
                       "to the believer in justification. The believer "
                       "is forensically righteous in Christ.",
       },
       {
           'name': 'Passive-obedience-only (Piscatorian; minority)',
           'persona_slugs': ['thomas-gataker', 'richard-vines',
                             'william-twisse', 'daniel-featley'],
           'position': "Only Christ's passive obedience is imputed; his "
                       "active obedience was required for his own person "
                       "as a man under the law. Justification consists "
                       "in the imputation of Christ's suffering of the "
                       "curse, with the believer's renewed obedience "
                       "following as the believer's own duty.",
       },
   ],
   outcome='rejected-alternative',
   language=(
       "WCF XI.3: 'Christ, by his obedience and death, did fully discharge "
       "the debt of all those that are thus justified, and did make a "
       "proper, real, and full satisfaction to his Father's justice in "
       "their behalf…' "
       "Larger Catechism Q. 70: 'Justification is an act of God's free "
       "grace unto sinners, in which he pardoneth all their sins, "
       "accepteth and accounteth their persons righteous in his sight; "
       "not for any thing wrought in them, or done by them, but only "
       "for the perfect obedience and full satisfaction of Christ, by "
       "God imputed to them.'"
   ),
   legacy=(
       "The full-imputation position became orthodox Reformed teaching "
       "and the basis of Owen's *Justification* (1677), Hodge, "
       "Bavinck, Murray. Twentieth-century discussions (Daniel Doriani; "
       "the OPC report on justification, 2006) have returned to the "
       "Piscatorian position only briefly. The 'New Perspective on "
       "Paul' (Wright, Dunn) has revisited the imputation question in "
       "ways the Assembly would have considered closer to the "
       "Piscatorian minority. The Westminster language — 'whole "
       "obedience and satisfaction' — remains the touchstone for "
       "subsequent Reformed debate."
   ),
   references=['WCF VIII.5', 'WCF XI.3', 'LC Q. 70'])


_c('the-descent-into-hell', 'The Descent into Hell',
   '1647',
   locus_key='christology',
   attribute_keys=['christology_states_and_descent'],
   tagline='What does the Apostles’ Creed’s "descendit ad inferna" mean?',
   background=(
       "The Apostles' Creed includes the clause *descendit ad inferna* — "
       "'He descended into hell' — between the burial and the resurrection. "
       "Patristic and medieval interpretation had varied widely: some read "
       "it as a local descent to a place of the dead (the *Limbus Patrum*); "
       "some as Christ's triumphant proclamation to the damned or to OT "
       "saints; some as a continued state of humiliation under death. "
       "Calvin's *Institutes* II.16.10-11 had given two readings: the clause "
       "may signify the depth of Christ's suffering on the cross (the "
       "metaphorical reading), or it may signify the continued state of "
       "humiliation between death and resurrection (the realist reading). "
       "The 1552 Forty-Two Articles of the Church of England included the "
       "local-descent reading; the 1571 Thirty-Nine Articles dropped it. "
       "The Reformed needed a confessional handling."
   ),
   summary=(
       "The Assembly did not include the *descendit* clause in the "
       "Confession itself but addressed it in the Larger Catechism Q. 50, "
       "where it explained the clause as a way of describing Christ's "
       "continued state of humiliation between death and resurrection — "
       "the realist reading, not the local-descent or the metaphorical "
       "reading. This was a deliberate exegetical choice: the Catechism "
       "preserves the Creed's clause but interprets it within the "
       "two-state schema (humiliation and exaltation) of Phil. 2."
   ),
   parties=[
       {
           'name': 'Continued-state-of-the-dead reading (adopted)',
           'persona_slugs': ['anthony-tuckney', 'edmund-calamy-elder',
                             'edward-reynolds', 'herbert-palmer'],
           'position': "The 'descent' is Christ's continued state of "
                       "humiliation between death and resurrection — "
                       "his being buried, his continuing in the state "
                       "of the dead, and remaining under the power of "
                       "death until the third day. No local descent.",
       },
       {
           'name': 'Local-descent readings (rejected)',
           'persona_slugs': [],
           'position': "Christ literally descended into a place called "
                       "Hades — to liberate OT saints (*Limbus "
                       "Patrum*), to suffer further, or to triumph over "
                       "hell. Various forms of this Roman-Catholic and "
                       "high-Lutheran reading were rejected.",
       },
       {
           'name': 'Calvin\'s metaphorical reading (a possible alternative)',
           'persona_slugs': [],
           'position': "The 'descent' is metaphor for the depth of "
                       "Christ's suffering on the cross — the moment "
                       "of *Eli, Eli, lama sabachthani*. This was a "
                       "live Reformed reading but not adopted by the "
                       "Catechism.",
       },
   ],
   outcome='settled-clear',
   language=(
       "Larger Catechism Q. 50: 'Christ's humiliation after his death "
       "consisted in his being buried, and continuing in the state of "
       "the dead, and under the power of death till the third day; "
       "which hath been otherwise expressed in these words, He "
       "descended into hell.'"
   ),
   legacy=(
       "The continued-state-of-the-dead reading became standard "
       "Reformed teaching. Reformed liturgies that use the Apostles' "
       "Creed often handle the clause by retaining it and "
       "interpreting it as the Catechism does; some Reformed bodies "
       "omit the clause entirely. The Heidelberg Catechism Q. 44 "
       "takes the metaphorical reading (depth of suffering) — a "
       "different Reformed handling, also live but not Westminster's."
   ),
   references=['LC Q. 50'])


# ======================================================================
# V. SOTERIOLOGY
# ======================================================================

_c('justification-and-the-antinomian-crisis',
   'Justification and the Antinomian Crisis',
   '1643–1647',
   locus_key='soteriology',
   attribute_keys=['soteriology_justification_ground',
                   'law_sanctification_good_works',
                   'law_sanctification_uses_of_the_law'],
   tagline='How do you secure sola fide without letting the law fall away?',
   background=(
       "The 1640s saw a fresh outbreak of antinomian preaching in London "
       "and the army. Tobias Crisp's *Christ Alone Exalted* (published "
       "posthumously 1643) pressed *sola fide* so hard that the law's "
       "role in the Christian life seemed to evaporate: Christ's "
       "righteousness covered the believer so absolutely that the "
       "believer's sins were 'as if they had never been,' and the "
       "Christian life consisted in resting in justification rather than "
       "in any pursuit of holiness. John Saltmarsh, Henry Denne, William "
       "Dell, and others preached variants of the position to army "
       "audiences. The Assembly's drafters had to write chapters on "
       "justification (XI), sanctification (XIII), good works (XVI), and "
       "the law (XIX) in the shadow of this crisis — securing imputed "
       "righteousness against Rome while securing the third use of the "
       "law against the antinomians."
   ),
   summary=(
       "The Assembly's response is one of the Confession's masterstrokes "
       "of confessional engineering. WCF XI.1-4 secures forensic "
       "justification by imputed righteousness alone, received by faith "
       "alone. XI.2 insists that 'faith…is no dead faith, but worketh by "
       "love.' XVI.2 makes good works 'the fruits and evidences of a "
       "true and lively faith.' XVI.5 denies all merit. XVI.7 holds that "
       "even the works of unregenerate persons, though commanded by God, "
       "are 'sinful and cannot please God' because not proceeding 'from "
       "an heart purified by faith.' XIX.5-6 affirms the third use of "
       "the moral law for the regenerate. Anthony Burgess's *Vindiciae "
       "Legis* (1646) is the canonical Reformed reply to Crisp and the "
       "deepest expression of the Assembly's collective mind on the "
       "question."
   ),
   parties=[
       {
           'name': 'The Assembly\'s anti-antinomian consensus',
           'persona_slugs': ['anthony-burgess', 'edward-reynolds',
                             'george-walker', 'edmund-calamy-elder',
                             'anthony-tuckney', 'daniel-cawdrey'],
           'position': "Justification is forensic and by faith alone, "
                       "on the ground of Christ's imputed obedience and "
                       "satisfaction. But true faith is never alone — "
                       "it works by love, produces good works as its "
                       "necessary fruits, and submits to the third use "
                       "of the moral law as the rule of life for the "
                       "regenerate.",
       },
       {
           'name': 'The antinomians (rejected; mostly outside the Assembly)',
           'persona_slugs': [],
           'position': "Justification covers the believer so absolutely "
                       "that the law has no continuing normative claim "
                       "on the regenerate. The Christian life is rest "
                       "in finished work, not pursuit of holiness "
                       "under the law. Tobias Crisp, John Saltmarsh, "
                       "John Eaton.",
       },
   ],
   outcome='rejected-alternative',
   language=(
       "WCF XI.2: 'Faith, thus receiving and resting on Christ and his "
       "righteousness, is the alone instrument of justification: yet "
       "is it not alone in the person justified, but is ever "
       "accompanied with all other saving graces, and is no dead "
       "faith, but worketh by love.' "
       "WCF XIX.6: 'Although true believers be not under the law as a "
       "covenant of works, to be thereby justified or condemned, yet "
       "is it of great use to them, as well as to others; in that, as "
       "a rule of life, informing them of the will of God and their "
       "duty, it directs and binds them to walk accordingly…'"
   ),
   legacy=(
       "The Assembly's careful threading between Rome and antinomianism "
       "has defined the Reformed handling ever since. Richard Baxter's "
       "*Aphorisms of Justification* (1649) attempted a different "
       "synthesis (the 'neonomian' reading of faith as the believer's "
       "evangelical righteousness) which John Owen and the Reformed "
       "mainline rejected as betraying Westminster. The Marrow "
       "controversy (1717-22) revived the antinomian question in "
       "Scotland. Modern Reformed debates over 'gospel sanctification' "
       "(Tullian Tchividjian and the controversy of the 2010s) have "
       "rehearsed the same crisis at a smaller scale."
   ),
   references=['WCF XI.1-4', 'WCF XVI.2-7', 'WCF XIX.6'])


_c('assurance-of-the-essence-of-faith',
   'Assurance: Of the Essence of Saving Faith?',
   '1646–1647',
   locus_key='soteriology',
   attribute_keys=['soteriology_assurance'],
   tagline='Does every true believer have full assurance, or is assurance a separate gift?',
   background=(
       "Calvin in the *Institutes* III.2 had tended to equate full "
       "assurance with the substance of saving faith: 'we make the "
       "foundation of faith the gracious promise…firm and certain "
       "knowledge of the divine benevolence toward us.' Beza pushed the "
       "equation harder. The early English Reformers (Cranmer, Latimer) "
       "took the same line: a true believer simply *is* assured. But "
       "Perkins's experimental tradition and the great Puritan casuists "
       "(Hooker, Shepard, Sibbes, Goodwin) had encountered too many "
       "troubled believers whose faith was real but whose assurance was "
       "wanting. By the 1640s the pastoral data demanded a softening of "
       "Calvin's strict equation. The Heidelberg Catechism Q. 21 still "
       "took the strict reading; the Belgic Confession was ambiguous."
   ),
   summary=(
       "The Assembly produced one of the Standards' most pastorally "
       "consequential clauses: WCF XVIII.3, that 'this infallible "
       "assurance doth not so belong to the essence of faith, but that "
       "a true believer may wait long, and conflict with many "
       "difficulties, before he be partaker of it.' This was the "
       "Puritan-experimental softening of the early Reformed equation. "
       "Assurance is attainable, ordinary for the regenerate to seek, "
       "but not constitutive of saving faith. The chapter goes on (XVIII.2) "
       "to ground assurance on the divine promises, the inward evidences "
       "of grace, and the testimony of the Spirit of adoption — "
       "three-fold rather than one-fold, accommodating both the "
       "Spirit-witness party (Goodwin, Cotton) and the marks-of-grace "
       "party (Hooker, Shepard, the syllogismus practicus tradition)."
   ),
   parties=[
       {
           'name': 'The Westminster pastoral softening',
           'persona_slugs': ['anthony-tuckney', 'herbert-palmer',
                             'edmund-calamy-elder', 'edward-reynolds',
                             'samuel-rutherford'],
           'position': "Saving faith and assurance are distinguishable. "
                       "A true believer may have faith without yet "
                       "having infallible assurance; assurance is "
                       "attainable but is not of the essence of "
                       "saving faith. Assurance has three grounds: the "
                       "divine promises, inward graces, and the "
                       "Spirit's witness.",
       },
       {
           'name': 'The early-Calvin strict equation (not pressed at the Assembly)',
           'persona_slugs': [],
           'position': "Saving faith is itself the assurance of God's "
                       "gracious favour; a believer without assurance "
                       "lacks (to that extent) the substance of saving "
                       "faith. The Heidelberg Catechism's Q. 21 takes "
                       "this line.",
       },
       {
           'name': 'The Tridentine alternative (rejected)',
           'persona_slugs': [],
           'position': "Assurance of perseverance is impossible in this "
                       "life (Trent, Session VI, canon 16); a believer "
                       "may have hope but not certain assurance. "
                       "Rejected by the Assembly.",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF XVIII.3: 'This infallible assurance doth not so belong to "
       "the essence of faith, but that a true believer may wait long, "
       "and conflict with many difficulties, before he be partaker of "
       "it: yet, being enabled by the Spirit to know the things which "
       "are freely given him of God, he may, without extraordinary "
       "revelation, in the right use of ordinary means, attain "
       "thereunto.' "
       "WCF XVIII.2: 'This certainty…is founded upon the divine truth "
       "of the promises of salvation, the inward evidence of those "
       "graces unto which these promises are made, the testimony of "
       "the Spirit of adoption witnessing with our spirits that we "
       "are the children of God…'"
   ),
   legacy=(
       "The Westminster handling of assurance has shaped Reformed "
       "pastoral practice more than perhaps any other locus of the "
       "Standards. Owen's *The Holy Spirit*, Edwards's *Religious "
       "Affections* (1746), Spurgeon's pastoral counselling, and "
       "every subsequent Reformed treatment of the troubled "
       "conscience build on WCF XVIII.3. The 'free offer' debates of "
       "the 18th and 19th centuries (the Marrow controversy; the "
       "Erskines; M'Cheyne) are downstream of the Assembly's "
       "threefold-grounds account in XVIII.2."
   ),
   references=['WCF XVIII.1-4', 'WCF XIV.3'])


_c('perseverance-of-the-saints', 'The Perseverance of the Saints',
   '1646',
   locus_key='soteriology',
   attribute_keys=['soteriology_perseverance'],
   tagline='Can the truly regenerate finally fall from grace?',
   background=(
       "The Remonstrants at Dort (1618-19) had argued that final "
       "perseverance is conditional on the believer's continued faith "
       "and obedience, with the implication that a truly regenerate "
       "believer might finally apostatise. The Synod of Dort had "
       "rejected this in its Fifth Head of Doctrine and affirmed the "
       "indefectibility of grace: those whom God effectually calls and "
       "justifies cannot totally or finally fall away. Westminster had "
       "to restate the Dort position with reference to the English "
       "situation — where Arminians in the Church of England (Hammond, "
       "Bramhall, later Jeremy Taylor) and Wesleyan Arminians a century "
       "later would press the conditional reading."
   ),
   summary=(
       "WCF XVII.1 affirms the indefectibility of grace in language "
       "deliberately close to Dort's: 'They, whom God hath accepted in "
       "his Beloved, effectually called and sanctified by his Spirit, "
       "can neither totally nor finally fall away from the state of "
       "grace; but shall certainly persevere therein to the end, and be "
       "eternally saved.' XVII.2 grounds perseverance not in the "
       "believer's own free will but in the immutability of God's "
       "decree, the merit of Christ, the abiding indwelling of the "
       "Spirit, and the seed of God remaining in the believer. XVII.3 "
       "addresses the pastoral cases of believers falling into grievous "
       "sin — they may grieve the Spirit, deprive themselves of "
       "comforts, and bring temporal judgements on themselves, but the "
       "decree stands."
   ),
   parties=[
       {
           'name': 'The Westminster doctrine of indefectible grace',
           'persona_slugs': ['samuel-rutherford', 'anthony-tuckney',
                             'edmund-calamy-elder', 'thomas-goodwin',
                             'edward-reynolds'],
           'position': "The regenerate cannot totally or finally fall "
                       "from grace. Perseverance is grounded not in the "
                       "believer's own will but in God's decree, "
                       "Christ's merit, and the Spirit's indwelling. "
                       "The believer may sin grievously but cannot "
                       "fall away.",
       },
       {
           'name': 'The Arminian alternative (rejected)',
           'persona_slugs': [],
           'position': "Perseverance is conditional on continued faith "
                       "and obedience. A truly regenerate believer may "
                       "finally apostatise. The Remonstrant Articles "
                       "(1610) and the Wesleyan-Arminian tradition "
                       "later.",
       },
   ],
   outcome='rejected-alternative',
   language=(
       "WCF XVII.1: 'They, whom God hath accepted in his Beloved, "
       "effectually called and sanctified by his Spirit, can neither "
       "totally nor finally fall away from the state of grace; but "
       "shall certainly persevere therein to the end, and be eternally "
       "saved.'"
   ),
   legacy=(
       "The Wesleyan-Arminian rejection of perseverance in the 18th "
       "century, and the 19th-century 'second blessing' holiness "
       "movements, treated Westminster as the canonical articulation "
       "of the position they opposed. Within Reformed orthodoxy, "
       "Owen's *The Doctrine of the Saints' Perseverance Explained "
       "and Confirmed* (1654) is the great post-Assembly defence; "
       "Jonathan Edwards's writing on perseverance and the "
       "indwelling Spirit develops the doctrine pastorally."
   ),
   references=['WCF XVII.1-3'])


# ======================================================================
# VI. LAW & SANCTIFICATION
# ======================================================================

_c('the-third-use-of-the-law', 'The Third Use of the Moral Law',
   '1645–1646',
   locus_key='law_sanctification',
   attribute_keys=['law_sanctification_uses_of_the_law'],
   tagline='Does the moral law remain the rule of life for the regenerate?',
   background=(
       "Calvin in *Institutes* II.7.6-12 had taught three uses of the "
       "moral law: civil (restraining sin in society), pedagogical "
       "(driving sinners to Christ), and normative (instructing the "
       "regenerate as the rule of life). The antinomians of the 1640s — "
       "Crisp, Saltmarsh, Eaton, Dell — denied the third use: the "
       "regenerate believer is no longer 'under the law' in any "
       "normative sense, and Christ's righteousness is the believer's "
       "only standard. The pastoral consequence was a Christian life "
       "without a rule, which the Assembly's drafters saw as collapsing "
       "into license. The Reformed (Calvin, Ursinus, the Heidelberg "
       "Catechism Q. 92-115) had always taught the third use; Westminster "
       "had to restate it confessionally."
   ),
   summary=(
       "WCF XIX.5-6 secures the third use with great care. XIX.5 affirms "
       "that the moral law 'doth for ever bind all, as well justified "
       "persons as others, to the obedience thereof.' XIX.6 — the chapter's "
       "longest paragraph — distinguishes the law as covenant of works "
       "(from which the believer is free) from the law as rule of life "
       "(to which the believer is bound): 'although true believers be "
       "not under the law as a covenant of works, to be thereby "
       "justified or condemned, yet is it of great use to them, as well "
       "as to others; in that, as a rule of life, informing them of the "
       "will of God and their duty, it directs and binds them to walk "
       "accordingly.' Anthony Burgess's *Vindiciae Legis* (1646) is the "
       "canonical Reformed companion treatment."
   ),
   parties=[
       {
           'name': 'The Westminster anti-antinomian consensus',
           'persona_slugs': ['anthony-burgess', 'george-walker',
                             'edmund-calamy-elder', 'anthony-tuckney',
                             'samuel-rutherford', 'edward-reynolds'],
           'position': "The moral law has three uses, including a "
                       "third (normative) use for the regenerate. The "
                       "believer is free from the law as a covenant of "
                       "works but bound to the law as a rule of life.",
       },
       {
           'name': 'The antinomian denial (rejected)',
           'persona_slugs': [],
           'position': "The regenerate are not under the moral law in "
                       "any sense; Christ has fulfilled the law for "
                       "them, and the Christian life proceeds by "
                       "indwelling Spirit rather than external rule. "
                       "Crisp, Saltmarsh, Eaton.",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF XIX.5: 'The moral law doth for ever bind all, as well "
       "justified persons as others, to the obedience thereof; and "
       "that, not only in regard of the matter contained in it, but "
       "also in respect of the authority of God the Creator, who gave "
       "it. Neither doth Christ, in the gospel, any way dissolve, but "
       "much strengthen this obligation.' "
       "WCF XIX.6: 'Although true believers be not under the law as a "
       "covenant of works…yet is it of great use to them…as a rule of "
       "life, informing them of the will of God and their duty…'"
   ),
   legacy=(
       "The third use of the law has remained the Reformed pastoral "
       "norm. Wesley's distinction between law and gospel in 1740s "
       "evangelical preaching, the Marrow controversy's handling of "
       "the law-gospel distinction, and modern Reformed engagements "
       "with the 'sanctification debates' of the 2010s all play out "
       "on the ground WCF XIX laid down. The Lutheran 'law and "
       "gospel' tradition (the Formula of Concord Article VI) shares "
       "the third use in principle but applies it more cautiously "
       "than Westminster."
   ),
   references=['WCF XIX.5-6'])


_c('the-strict-sabbath', 'The Strict Sabbath',
   '1645',
   locus_key='law_sanctification',
   attribute_keys=['law_sanctification_sabbath'],
   tagline='The Lord’s Day as the perpetual fourth commandment, kept holy whole-day.',
   background=(
       "Sabbatarianism had developed sharply in English Puritan thought "
       "from Nicholas Bownde's *True Doctrine of the Sabbath* (1595), "
       "Richard Greenham's casuistry, and the campaigns against Sunday "
       "sport — culminating in James I's *Book of Sports* (1618, "
       "republished 1633) which Puritans regarded as a deliberate provocation. "
       "The Continental Reformed view was less strict: Calvin had treated "
       "the Sabbath as a ceremonial institution, abrogated as to the day "
       "but binding as to the principle of regular public worship; the "
       "Synod of Dort took a similar line. The English Puritans had "
       "tightened: the Sabbath is a creation ordinance (Gen. 2:3), "
       "perpetually moral, with its day changed from the seventh to the "
       "first by Christ's resurrection. Whole-day cessation from labour "
       "and recreation was required."
   ),
   summary=(
       "WCF XXI.7-8 codified the strict English-Puritan Sabbath as the "
       "Reformed confessional position. XXI.7 establishes the Sabbath as "
       "a positive moral commandment, perpetually binding, with the day "
       "changed from the seventh to the first by the apostolic example "
       "(Acts 20:7, 1 Cor. 16:1-2, Rev. 1:10). XXI.8 prescribes the "
       "manner of observance: 'the whole time' is to be kept holy unto "
       "the Lord, with cessation from 'worldly employments and "
       "recreations' apart from 'works of necessity and mercy.' The "
       "Continental Lord's Day tradition, more permissive of recreation "
       "after public worship, is rejected. The Larger Catechism Q. 115-121 "
       "develops the case at length."
   ),
   parties=[
       {
           'name': 'The strict-Sabbatarian consensus',
           'persona_slugs': ['samuel-rutherford', 'george-gillespie',
                             'edmund-calamy-elder', 'thomas-young',
                             'anthony-tuckney', 'humphrey-chambers'],
           'position': "The Sabbath is a creation ordinance and a "
                       "perpetually moral commandment; the day is "
                       "changed to the first day by Christ's "
                       "resurrection; whole-day cessation from ordinary "
                       "labour and recreation is required.",
       },
       {
           'name': 'Continental Lord\'s Day (less strict; not pressed)',
           'persona_slugs': [],
           'position': "The Sabbath's perpetual element is regular "
                       "public worship and a day of rest, but ordered "
                       "recreation after public worship is permitted. "
                       "Calvin, the Synod of Dort, the Heidelberg "
                       "tradition.",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF XXI.7-8: '…[God] hath particularly appointed one day in "
       "seven, for a Sabbath, to be kept holy unto him; which, from "
       "the beginning of the world to the resurrection of Christ, was "
       "the last day of the week; and, from the resurrection of "
       "Christ, was changed into the first day of the week, which, "
       "in Scripture, is called the Lord's Day, and is to be "
       "continued to the end of the world, as the Christian Sabbath. "
       "This Sabbath is then kept holy unto the Lord, when men, after "
       "a due preparing of their hearts, and ordering of their common "
       "affairs beforehand, do not only observe an holy rest, all the "
       "day, from their own works, words, and thoughts about their "
       "worldly employments and recreations…'"
   ),
   legacy=(
       "The Westminster Sabbath became the defining mark of "
       "English- and Scottish-Reformed piety. Sabbatarianism shaped "
       "Scottish-Sabbath law into the 20th century; the New England "
       "blue laws derive their structure from Westminster. The Free "
       "Church of Scotland's continued strict Sabbath observance and "
       "the post-1903 American Presbyterian softening of the clause "
       "mark the two later trajectories. Modern Reformed debates "
       "about Sunday cessation, regulative principles of worship, "
       "and Sabbath observance all turn on Westminster XXI."
   ),
   references=['WCF XXI.7-8', 'LC Q. 115-121', 'SC Q. 57-62'])


_c('the-tripartite-division-of-the-law',
   'The Tripartite Division of the Law',
   '1645',
   locus_key='law_sanctification',
   attribute_keys=['law_sanctification_tripartite_division'],
   tagline='Moral, judicial, ceremonial — and what binds after Christ?',
   background=(
       "Patristic and medieval theology had developed a threefold "
       "division of the Mosaic law into moral, ceremonial, and judicial "
       "(or civil/political) commandments. Aquinas's *Summa* I-II q. 99 "
       "is the locus classicus. The Reformed inherited the division and "
       "used it to handle the question of OT continuity: the moral law "
       "(summarized in the Decalogue) binds perpetually; the ceremonial "
       "law (the temple, the sacrifices, the dietary and purity laws) "
       "is fulfilled and abrogated in Christ; the judicial law (the "
       "civil legislation of Israel) is expired with the Jewish polity, "
       "though its 'general equity' may inform later civil legislation. "
       "Anabaptists and some radical sects rejected the division "
       "(treating the whole Mosaic law as superseded). Some later "
       "theonomic readings would press the judicial law as continuing "
       "in its substance."
   ),
   summary=(
       "WCF XIX.3-4 affirms the tripartite division in classical form. "
       "XIX.3 handles the ceremonial law as 'now abrogated under the "
       "New Testament.' XIX.4 handles the judicial law as 'expired "
       "together with the State of that people' (Israel), 'not "
       "obliging any other now, further than the general equity "
       "thereof may require.' XIX.5 then affirms the perpetual "
       "obligation of the moral law. The 'general equity' clause has "
       "been the most contested element ever since: theonomists read "
       "it expansively; most Reformed read it as a hermeneutical "
       "principle for applying biblical wisdom to later legislation, "
       "not as a code binding modern magistrates."
   ),
   parties=[
       {
           'name': 'The Assembly\'s classical-tripartite consensus',
           'persona_slugs': ['anthony-burgess', 'edward-reynolds',
                             'edmund-calamy-elder', 'anthony-tuckney'],
           'position': "The Mosaic law divides into moral, ceremonial, "
                       "and judicial; the moral binds perpetually, the "
                       "ceremonial is abrogated in Christ, the "
                       "judicial expired with the Jewish polity except "
                       "for its general equity.",
       },
       {
           'name': 'Anabaptist abrogation (rejected)',
           'persona_slugs': [],
           'position': "The whole Mosaic law is superseded by Christ; "
                       "the tripartite division is a Reformed "
                       "scholastic invention without scriptural "
                       "warrant.",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF XIX.3: 'Besides this law, commonly called moral, God was "
       "pleased to give to the people of Israel, as a church under "
       "age, ceremonial laws…all which ceremonial laws are now "
       "abrogated, under the New Testament.' "
       "WCF XIX.4: 'To them also, as a body politic, he gave sundry "
       "judicial laws, which expired together with the State of that "
       "people; not obliging any other now, further than the general "
       "equity thereof may require.'"
   ),
   legacy=(
       "The 'general equity' clause has been the locus of the "
       "20th-century theonomy debate. Rousas Rushdoony and Greg "
       "Bahnsen pressed an expansive reading of general equity as "
       "binding modern magistrates to the substance of the Mosaic "
       "judicial code; mainline Reformed (Meredith Kline, the OPC "
       "majority) rejected this as misreading Westminster. The "
       "Anabaptist abrogation reading has continued in various "
       "Mennonite and dispensationalist forms."
   ),
   references=['WCF XIX.3-4'])


# ======================================================================
# VII. ECCLESIOLOGY & WORSHIP
# ======================================================================

_c('the-grand-debate-polity', 'The Grand Debate over Polity',
   'October 1644 – January 1646',
   locus_key='ecclesiology_worship',
   attribute_keys=['ecclesiology_worship_polity'],
   tagline='Presbyterian or Independent: who exercises the keys of the kingdom?',
   background=(
       "Both the Presbyterians and the Independents at the Assembly "
       "agreed that episcopacy was not jure divino — the Long Parliament "
       "had already abolished it (October 1646 by ordinance, after the "
       "Assembly's debate). The question was what should replace it. The "
       "Five Dissenting Brethren (Goodwin, Nye, Bridge, Burroughs, "
       "Simpson) — all formed in the Dutch Reformed exile congregations "
       "of the 1630s — argued for Independency: the visible church to "
       "whom Christ gave the keys is the local congregation, gathered "
       "by covenant; synods and councils may advise but cannot bind. "
       "The English Presbyterian majority and the Scottish Commissioners "
       "argued for graded presbyterianism: the keys are given to elders "
       "in a series of courts (session, presbytery, synod, general "
       "assembly), with each higher court having authoritative "
       "jurisdiction over the lower. The Scots pressed jure divino "
       "Presbyterianism — divinely required by Scripture — while many "
       "English Presbyterians took a milder jure ecclesiastico position."
   ),
   summary=(
       "The Grand Debate ran for more than a year, with the most "
       "consequential sessions through 1645. The Independents published "
       "*An Apologeticall Narration* (1644) to take their case to the "
       "public; the Scots responded with Rutherford's *Due Right of "
       "Presbyteries* (1644) and Gillespie's *Aaron's Rod Blossoming* "
       "(1646, the demolition of Erastianism that also defended jure "
       "divino presbyterianism). The Assembly's votes went with the "
       "Presbyterian majority; the Independents protested but stayed "
       "and continued to vote on other matters. The Form of "
       "Presbyterial Church Government (1645) is the polity document, "
       "WCF XXX-XXXI is the confessional language. The Confession's "
       "ecclesiology is presbyterian in substance but worded generously "
       "enough that 1689 Particular Baptists and post-Savoy "
       "Congregationalists could adopt most of the language without "
       "contradiction."
   ),
   parties=[
       {
           'name': 'The Scottish jure divino Presbyterians',
           'persona_slugs': ['samuel-rutherford', 'george-gillespie',
                             'alexander-henderson', 'robert-baillie'],
           'position': "Christ has positively instituted a graded "
                       "presbyterial polity (session, presbytery, "
                       "synod, general assembly) by divine right "
                       "warrant; bishops and Independency are both "
                       "departures from his ordinance.",
       },
       {
           'name': 'The English Presbyterian majority',
           'persona_slugs': ['edmund-calamy-elder', 'stephen-marshall',
                             'cornelius-burgess', 'edward-reynolds',
                             'anthony-tuckney', 'lazarus-seaman',
                             'jeremiah-whitaker'],
           'position': "Presbyterian polity is scriptural and the "
                       "right ordering of the visible church; whether "
                       "jure divino in the strict sense or jure "
                       "ecclesiastico, it should be the established "
                       "form.",
       },
       {
           'name': 'The Five Dissenting Brethren (Independent)',
           'persona_slugs': ['thomas-goodwin', 'philip-nye',
                             'william-bridge', 'jeremiah-burroughs',
                             'sidrach-simpson', 'william-greenhill',
                             'joseph-caryl'],
           'position': "The keys are given to the local congregation "
                       "gathered by covenant; synods may advise but "
                       "cannot exercise authoritative jurisdiction. "
                       "The 'gathered church' of believers (and their "
                       "children) is the visible church of the New "
                       "Testament.",
       },
   ],
   outcome='settled-clear',
   language=(
       "Form of Presbyterial Church Government (1645): instituted "
       "the graded courts and the officers (pastors, teachers, ruling "
       "elders, deacons). "
       "WCF XXXI.1: 'For the better government, and further "
       "edification of the church, there ought to be such assemblies "
       "as are commonly called synods or councils.'"
   ),
   legacy=(
       "The English Presbyterian settlement was never fully "
       "implemented before the army and the Independents took control "
       "in 1647-49. The Savoy Declaration (1658) is the Independent "
       "recension of Westminster, adopting the Confession's doctrine "
       "but rewriting the polity chapters. The 1689 Particular Baptist "
       "Second London Confession does the same with credobaptism. The "
       "Westminster polity survived in Scotland and (via the "
       "Solemn League and Covenant) in Northern Ireland; the American "
       "Presbyterian and the Reformed Presbyterian traditions trace "
       "their polity to Westminster."
   ),
   references=['Form of Presbyterial Church Government (1645)',
               'WCF XXV', 'WCF XXX', 'WCF XXXI'])


_c('the-erastian-question', 'The Erastian Question',
   'July 1645 – November 1645',
   locus_key='ecclesiology_worship',
   attribute_keys=['ecclesiology_worship_polity',
                   'ecclesiology_worship_censures_and_synods',
                   'civil_last_things_magistrate_role'],
   tagline='Does ecclesiastical jurisdiction belong to the church or to the civil magistrate?',
   background=(
       "Thomas Erastus (1524-1583), a Heidelberg physician and theologian, "
       "had argued in *Explicatio Gravissimae Quaestionis* (published "
       "posthumously 1589) that the church has no proper jurisdiction "
       "distinct from the civil magistrate's. Ecclesiastical discipline, "
       "Erastus held, is a function of the Christian state, not of a "
       "distinct ecclesial court. The position had been Henry VIII's in "
       "England (in modified form) and Zwingli's in Zurich; it had "
       "supporters at Westminster among the lay assessors — Selden, "
       "Lightfoot, Coleman, Whitelocke — and threatened to derail the "
       "Presbyterian polity settlement at the highest level."
   ),
   summary=(
       "The Erastian question came to a head in the July 1645 sessions "
       "and ran through to November. Selden was the most formidable "
       "Erastian voice — his learning on the Sanhedrin and Hebrew law "
       "made him a uniquely difficult opponent — and Lightfoot pressed "
       "the case from the ministerial side with Coleman's support. "
       "Thomas Coleman's parliamentary sermon of 30 July 1645 (*A "
       "Brotherly Examination Re-examined*) was the public manifesto. "
       "Gillespie's reply, the great *Aaron's Rod Blossoming* (1646), is "
       "the canonical Reformed refutation: Christ has positively "
       "instituted a government in the church distinct from the civil "
       "magistrate's. Rutherford's *Divine Right of Church Government* "
       "(1646) supplied the systematic backing. The Assembly voted "
       "against Erastianism; the Form of Government and WCF XXX.1 "
       "secured the church's independent jurisdiction. Selden lost; "
       "Lightfoot kept his attendance and vote."
   ),
   parties=[
       {
           'name': 'The anti-Erastian majority',
           'persona_slugs': ['george-gillespie', 'samuel-rutherford',
                             'alexander-henderson', 'edmund-calamy-elder',
                             'thomas-goodwin', 'edward-reynolds'],
           'position': "Christ has positively instituted a government "
                       "in the church distinct from the civil "
                       "magistrate's. Ecclesiastical jurisdiction "
                       "(admission, censure, excommunication) belongs "
                       "to officers in the church, not to the "
                       "magistrate.",
       },
       {
           'name': 'The Erastians',
           'persona_slugs': ['john-selden', 'john-lightfoot',
                             'thomas-coleman', 'bulstrode-whitelocke'],
           'position': "Ecclesiastical jurisdiction belongs ultimately "
                       "to the Christian magistrate, not to a "
                       "distinct ecclesial court. The church's "
                       "officers may execute discipline but only as "
                       "agents of the magistrate; excommunication is "
                       "a civil power.",
       },
   ],
   outcome='rejected-alternative',
   language=(
       "WCF XXX.1: 'The Lord Jesus, as King and Head of his Church, "
       "hath therein appointed a government, in the hand of Church "
       "officers, distinct from the civil magistrate.' "
       "WCF XXXI.5: 'Synods and councils are to handle, or conclude "
       "nothing, but that which is ecclesiastical: and are not to "
       "intermeddle with civil affairs which concern the "
       "commonwealth…'"
   ),
   legacy=(
       "Gillespie's *Aaron's Rod Blossoming* (1646) remained the "
       "Reformed standard refutation of Erastianism through the 18th "
       "and 19th centuries. The Scottish Disruption of 1843 — the "
       "Free Church of Scotland's secession over patronage and state "
       "interference — turned on whether the Court of Session had "
       "Erastianised the established church. The American 1788 "
       "revision of WCF XXIII rewrote the magistrate clauses for a "
       "disestablished context but kept XXX.1's distinct-jurisdiction "
       "language intact. Modern church-state debates in Reformed "
       "circles still cite the Westminster anti-Erastian settlement."
   ),
   references=['WCF XXX.1', 'WCF XXXI.5'])


_c('the-regulative-principle', 'The Regulative Principle of Worship',
   '1644–1645',
   locus_key='ecclesiology_worship',
   attribute_keys=['ecclesiology_worship_regulative_principle'],
   tagline='Only what God commands may be done in worship.',
   background=(
       "Reformed worship had been structured by what later writers would "
       "call the regulative principle: only what God commands in "
       "Scripture (by precept, approved example, or good and necessary "
       "consequence) may be used in his worship. Calvin's *Necessity of "
       "Reforming the Church* (1543) had argued the case against the "
       "Roman accretions of the medieval Mass. The contrasting normative "
       "principle (whatever is not forbidden is permitted) had been "
       "Lutheran (the Augsburg Confession), Anglican (Hooker's *Of the "
       "Laws of Ecclesiastical Polity* Book V), and Roman Catholic. The "
       "Westminster divines were unanimous on the regulative side but "
       "had to draft language that would walk the line between strict "
       "prescriptionism (which would forbid even sensible "
       "circumstances) and the looser normative reading."
   ),
   summary=(
       "WCF XXI.1 is the classical statement of the regulative "
       "principle: 'The acceptable way of worshipping the true God is "
       "instituted by himself, and so limited by his own revealed will, "
       "that he may not be worshipped according to the imaginations and "
       "devices of men, or the suggestions of Satan, under any visible "
       "representation, or any other way not prescribed in the Holy "
       "Scripture.' WCF I.6 had earlier handled the question of "
       "'circumstances concerning the worship of God…common to human "
       "actions and societies, which are to be ordered by the light of "
       "nature, and Christian prudence, according to the general rules "
       "of the Word.' The combination gives the regulative principle in "
       "substance (only commanded worship is acceptable) with "
       "circumstantial latitude (the time of services, the posture, the "
       "language). The Directory for Public Worship (1645) is the "
       "applied liturgical document, replacing the Book of Common Prayer."
   ),
   parties=[
       {
           'name': 'The regulative-principle consensus',
           'persona_slugs': ['george-gillespie', 'samuel-rutherford',
                             'edmund-calamy-elder', 'thomas-young',
                             'anthony-tuckney', 'edward-reynolds'],
           'position': "Only what is commanded in Scripture (by "
                       "precept, approved example, or good and "
                       "necessary consequence) may be done in worship. "
                       "Circumstances (time, place, posture) are "
                       "regulated by the light of nature.",
       },
       {
           'name': 'The Anglican normative alternative (rejected)',
           'persona_slugs': [],
           'position': "Whatever is not forbidden in worship is "
                       "permitted; the church has authority to ordain "
                       "rites and ceremonies for order and edification. "
                       "Hooker's *Ecclesiastical Polity*; the 1559 "
                       "Book of Common Prayer.",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF XXI.1: 'The acceptable way of worshipping the true God is "
       "instituted by himself, and so limited by his own revealed "
       "will, that he may not be worshipped according to the "
       "imaginations and devices of men, or the suggestions of Satan, "
       "under any visible representation, or any other way not "
       "prescribed in the Holy Scripture.'"
   ),
   legacy=(
       "The regulative principle has shaped Presbyterian and Reformed "
       "worship into the 21st century — the no-instruments debate in "
       "the 19th-century Free Church of Scotland, the exclusive-psalmody "
       "Reformed Presbyterian tradition, the worship debates in the "
       "PCA over images and contemporary liturgical forms. The Westminster "
       "Directory for Public Worship (1645) provided the framework "
       "until later denominational service-books replaced it."
   ),
   references=['WCF I.6', 'WCF XXI.1', 'WCF XXI.3-6',
               'Directory for the Public Worship of God (1645)'])


_c('sacramental-efficacy', 'Sacramental Efficacy: Signs and Seals',
   '1646',
   locus_key='ecclesiology_worship',
   attribute_keys=['ecclesiology_worship_sacraments_efficacy'],
   tagline='How sacraments confer grace without operating ex opere operato or being bare memorials.',
   background=(
       "Reformed sacramentology had to thread a needle between Rome's "
       "ex opere operato (the sacrament confers grace by the act "
       "performed, by the power of the act itself) and Zwingli's bare "
       "memorialism (the sacrament is only a memorial sign, with no "
       "conferral of grace). Calvin had developed a third position — "
       "the sacraments as signs and seals of the covenant of grace, "
       "conferring the grace signified through the Spirit's work upon "
       "the faith of the worthy receiver. The continental Reformed "
       "confessions (Belgic, Helvetic, Heidelberg) had taken this line. "
       "Westminster needed to reaffirm it confessionally and apply it "
       "to both baptism and the Lord's Supper, in a context where "
       "Particular Baptists were pressing memorialist tendencies and "
       "Lutheran sacramentalism remained a live alternative."
   ),
   summary=(
       "WCF XXVII (sacraments generally), XXVIII (baptism), and XXIX "
       "(the Lord's Supper) work out the signs-and-seals position with "
       "great care. XXVII.1 defines sacraments as 'holy signs and "
       "seals of the covenant of grace…to represent Christ and his "
       "benefits.' XXVII.3 rejects ex opere operato: 'The grace which "
       "is exhibited in or by the sacraments rightly used, is not "
       "conferred by any power in them.' XXVIII.6 affirms the "
       "conferral of grace through baptism upon worthy receivers — "
       "by the Spirit's work, not by mere outward administration. "
       "XXIX.7 rejects both the Roman mass (transubstantiation, the "
       "sacrifice of the mass) and the bare-memorial reading: worthy "
       "receivers 'really and indeed' (yet 'not carnally and "
       "corporally, but spiritually') receive Christ in the Lord's "
       "Supper."
   ),
   parties=[
       {
           'name': 'The Westminster signs-and-seals consensus',
           'persona_slugs': ['edmund-calamy-elder', 'edward-reynolds',
                             'anthony-tuckney', 'william-gouge',
                             'samuel-rutherford', 'george-gillespie',
                             'thomas-bedford'],
           'position': "Sacraments are signs and seals of the covenant "
                       "of grace, conferring the grace signified upon "
                       "worthy receivers by the Spirit's work and the "
                       "word of institution. Not bare memorials, not "
                       "ex opere operato.",
       },
       {
           'name': 'Roman ex opere operato (rejected)',
           'persona_slugs': [],
           'position': "Sacraments confer grace by the act performed, "
                       "independent of the recipient's faith. Trent, "
                       "Session VII, canons 6-8.",
       },
       {
           'name': 'Zwinglian bare memorialism (rejected)',
           'persona_slugs': [],
           'position': "Sacraments are merely memorial or instructive "
                       "signs with no conferral of grace through "
                       "them. Some early Baptists; some radical "
                       "Independents.",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF XXVII.3: 'The grace which is exhibited in or by the "
       "sacraments rightly used, is not conferred by any power in "
       "them; neither doth the efficacy of a sacrament depend upon "
       "the piety or intention of him that doth administer it: but "
       "upon the work of the Spirit, and the word of institution…' "
       "WCF XXIX.7: 'Worthy receivers, outwardly partaking of the "
       "visible elements in this sacrament, do then also, inwardly "
       "by faith, really and indeed, yet not carnally and corporally "
       "but spiritually, receive and feed upon Christ crucified, and "
       "all benefits of his death…'"
   ),
   legacy=(
       "The Westminster handling of the sacraments has been the "
       "Reformed standard. Solomon Stoddard's later doctrine of the "
       "Lord's Supper as a converting ordinance (1690s, Northampton) "
       "departed from XXIX.7's restriction to worthy receivers; "
       "Edwards's rejection of his grandfather's practice in the "
       "1740s and his consequent dismissal from Northampton (1750) "
       "was a debate over Westminster's sacramental theology. "
       "Modern Reformed sacramental discussions (Federal Vision, "
       "the OPC reports on baptismal efficacy) all return to "
       "Westminster's signs-and-seals language."
   ),
   references=['WCF XXVII', 'WCF XXVIII.6', 'WCF XXIX.7'])


_c('the-rouse-psalter', 'The Rouse Psalter and Metrical Psalmody',
   '1643–1648',
   locus_key='ecclesiology_worship',
   attribute_keys=['ecclesiology_worship_regulative_principle'],
   tagline='The metrical psalms that became the Scottish Psalter.',
   background=(
       "The Westminster Standards do not formally take a position on "
       "exclusive psalmody vs hymnody, but the Assembly's revision of "
       "Francis Rouse's metrical psalms had enormous practical "
       "consequences. Rouse had published *The Booke of Psalmes in "
       "English Meter* (1643), drawing on Sternhold and Hopkins (the "
       "1562 English metrical psalter, in use for nearly a century) and "
       "on the work of Henry Ainsworth and George Sandys. The Long "
       "Parliament referred the work to the Assembly, which revised it "
       "extensively through 1645-46. The General Assembly of the Church "
       "of Scotland adopted a further revision in 1650 — the Scottish "
       "Metrical Psalter — which has been continuously sung in Scottish "
       "Reformed worship to the present."
   ),
   summary=(
       "The Assembly revised Rouse's Psalter line by line through 1645 "
       "and 1646 — perhaps the most labour-intensive single project at "
       "Westminster after the Catechisms. The committee chairs were "
       "John Lightfoot and Thomas Gataker, working with Rouse himself. "
       "The 1646 revision was published as *The Psalms of David in "
       "Meeter* and adopted by the Long Parliament for use in English "
       "parishes. The Scottish General Assembly's further revision in "
       "1650 produced the Scottish Metrical Psalter, the definitive "
       "form. The Westminster Standards never formally legislate "
       "exclusive psalmody, but the labour the Assembly put into the "
       "Psalter and the prominence of the Directory's prescription of "
       "psalm-singing made metrical psalmody the standard Reformed "
       "worship practice for two centuries."
   ),
   parties=[
       {
           'name': 'The Assembly\'s metrical-psalmody consensus',
           'persona_slugs': ['john-lightfoot', 'thomas-gataker',
                             'francis-rouse', 'william-gouge',
                             'edward-reynolds'],
           'position': "The Psalms are God's own hymnbook, given for "
                       "the worship of the church; their metrical "
                       "rendering for congregational singing is the "
                       "proper Reformed psalmody.",
       },
   ],
   outcome='settled-with-latitude',
   language=(
       "Directory for the Public Worship of God (1645): 'It is the "
       "duty of Christians to praise God publicly, by singing of "
       "psalms together in the congregation, and also privately in "
       "the family.'"
   ),
   legacy=(
       "The Scottish Metrical Psalter (1650) has been sung in "
       "Scottish Presbyterian worship continuously since adoption — "
       "Psalm 23 in its metrical setting ('The Lord's my Shepherd, "
       "I'll not want') is among the best-known religious lyrics in "
       "the English language. Isaac Watts's *Hymns and Spiritual "
       "Songs* (1707) and *The Psalms of David Imitated* (1719) "
       "introduced hymn-singing and a paraphrasal psalmody that "
       "gradually displaced metrical psalmody in English-speaking "
       "Reformed worship through the 18th and 19th centuries. The "
       "Reformed Presbyterian tradition and the Free Church of "
       "Scotland (Continuing) retain exclusive metrical psalmody."
   ),
   references=['Directory for the Public Worship of God (1645)'])


# ======================================================================
# VIII. CIVIL & LAST THINGS
# ======================================================================

_c('the-magistrates-two-tables', "The Magistrate and the Two Tables",
   '1646; revised 1788',
   locus_key='civil_last_things',
   attribute_keys=['civil_last_things_magistrate_role'],
   tagline='Is the civil magistrate the keeper of both tables of the Decalogue?',
   background=(
       "Reformed political theology had held the civil magistrate "
       "responsible for both tables of the Decalogue (*custos utriusque "
       "tabulae*): the second table (duties to neighbour) and also the "
       "first table (duties to God). The magistrate was thus to "
       "suppress public idolatry, blasphemy, and heresy, and to "
       "protect and promote the true religion. This had been Geneva's "
       "practice under Calvin, Heidelberg's under the Electors, and the "
       "Scottish settlement's after 1638. The Solemn League and "
       "Covenant (1643) had committed England, Scotland, and Ireland to "
       "a uniform Reformed religion under magisterial enforcement. But "
       "Roger Williams (in Rhode Island from 1636), the Independents at "
       "Westminster, and the radical sects of the army were pressing "
       "broader religious liberty. The question came to a head in the "
       "drafting of WCF XXIII in 1646."
   ),
   summary=(
       "WCF XXIII (1646 text) committed the magistrate to *custos "
       "utriusque tabulae*: XXIII.3 gave the civil magistrate authority "
       "to take order 'that unity and peace be preserved in the Church, "
       "that the truth of God be kept pure and entire, that all "
       "blasphemies and heresies be suppressed, all corruptions and "
       "abuses in worship and discipline prevented or reformed, and all "
       "the ordinances of God duly settled, administered, and "
       "observed.' XX.4 made the magistrate the punisher of those who "
       "'publish such opinions, or maintain such practices, as are "
       "contrary to the light of nature, or to the known principles of "
       "Christianity.' This is the high-water mark of the *custos "
       "utriusque tabulae* tradition in confessional Reformed thought. "
       "The 1788 American revision rewrote both clauses to align with "
       "the new federal disestablishment settlement: the magistrate's "
       "duty is to protect, not to direct or coerce, religion. The "
       "Reformed Presbyterian (Covenanter) tradition retained the 1646 "
       "language; the mainline American Presbyterian tradition follows "
       "the 1788."
   ),
   parties=[
       {
           'name': 'The 1646 custos-utriusque-tabulae position',
           'persona_slugs': ['samuel-rutherford', 'george-gillespie',
                             'archibald-johnston-wariston',
                             'cornelius-burgess'],
           'position': "The civil magistrate is keeper of both tables "
                       "of the Decalogue. He must suppress public "
                       "heresy and blasphemy, call synods, and "
                       "establish the true religion. The Solemn "
                       "League and Covenant settlement.",
       },
       {
           'name': 'The 1788 American revision',
           'persona_slugs': [],
           'position': "The civil magistrate protects the church "
                       "from violence and danger but does not "
                       "prefer one denomination over another, nor "
                       "compel any to the true religion. The "
                       "disestablishment settlement of the American "
                       "Constitution.",
       },
       {
           'name': 'Roger Williams\'s liberty-of-conscience position '
                   '(outside the Assembly)',
           'persona_slugs': [],
           'position': "The civil sword has no jurisdiction over the "
                       "conscience. The magistrate's domain is civil "
                       "peace and the second table; the first table "
                       "belongs entirely to the conscience and the "
                       "voluntary association. *The Bloudy Tenent of "
                       "Persecution* (1644).",
       },
   ],
   outcome='mixed',
   language=(
       "WCF XXIII.3 (1646): 'The civil magistrate may not assume to "
       "himself the administration of the Word and sacraments, or the "
       "power of the keys of the kingdom of heaven; yet he hath "
       "authority, and it is his duty, to take order, that unity and "
       "peace be preserved in the Church, that the truth of God be "
       "kept pure and entire, that all blasphemies and heresies be "
       "suppressed, all corruptions and abuses in worship and "
       "discipline prevented or reformed, and all the ordinances of "
       "God duly settled, administered, and observed.' "
       "WCF XXIII.3 (American 1788): 'Civil magistrates may not assume "
       "to themselves the administration of the Word and sacraments…"
       "yet, as nursing fathers, it is the duty of civil magistrates "
       "to protect the Church of our common Lord, without giving the "
       "preference to any denomination of Christians above the rest…'"
   ),
   legacy=(
       "The split between the 1646 text (still confessional in the "
       "Reformed Presbyterian and Free Church traditions) and the "
       "1788 American revision (the PCA, OPC, and other American "
       "Presbyterian bodies) is the longest-running confessional "
       "fracture of the Westminster Standards. Modern debates about "
       "the magistrate's role — establishment-versus-disestablishment, "
       "religious liberty, public-square religion — turn on this "
       "fracture. Roger Williams's position, marginal in 1644, became "
       "the eventual American settlement."
   ),
   references=['WCF XX.4', 'WCF XXIII.3'])


_c('the-pope-as-antichrist', 'The Pope as Antichrist',
   '1646',
   locus_key='civil_last_things',
   attribute_keys=[],
   tagline='The Westminster clause that the American 1788 revision dropped.',
   background=(
       "The identification of the Pope with the eschatological "
       "Antichrist had been a Reformation commonplace since Luther — "
       "drawn from the prophecies of Daniel 7, 2 Thessalonians 2, and "
       "Revelation 13. Calvin took the position in the *Institutes*, "
       "the Reformed confessions had taken it (Helvetic, Belgic), and "
       "the Westminster divines unanimously held it. The clause "
       "appears in WCF XXV.6 as a direct identification."
   ),
   summary=(
       "WCF XXV.6 (1646) makes the identification explicit and direct: "
       "'There is no other head of the Church but the Lord Jesus "
       "Christ: nor can the Pope of Rome in any sense be head thereof; "
       "but is that Antichrist, that man of sin and son of perdition, "
       "that exalteth himself in the Church against Christ, and all "
       "that is called God.' The clause was not contested at the "
       "Assembly — the divines were unanimous — but it has been the "
       "most explicitly polemical eschatological identification in the "
       "Standards. The 1788 American revision excised the 'is that "
       "Antichrist' clause; the original Scottish text retained it; "
       "the 1903 PCUSA revisions kept the American softening."
   ),
   parties=[
       {
           'name': 'The 1646 Westminster identification',
           'persona_slugs': ['edmund-calamy-elder', 'samuel-rutherford',
                             'george-gillespie', 'cornelius-burgess',
                             'edward-reynolds'],
           'position': "The Pope of Rome is that Antichrist, the "
                       "man of sin and son of perdition. The "
                       "identification is required by Daniel 7, "
                       "2 Thessalonians 2, and Revelation, and is the "
                       "unanimous Reformation reading.",
       },
       {
           'name': 'The 1788 American revision (softened)',
           'persona_slugs': [],
           'position': "The Pope of Rome cannot in any sense be "
                       "head of the church, but the specific "
                       "identification with the eschatological "
                       "Antichrist is dropped — leaving the "
                       "identification open to historical-prophetic "
                       "judgement.",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF XXV.6 (1646): 'There is no other head of the Church but "
       "the Lord Jesus Christ: nor can the Pope of Rome in any sense "
       "be head thereof; but is that Antichrist, that man of sin and "
       "son of perdition, that exalteth himself in the Church "
       "against Christ, and all that is called God.' "
       "WCF XXV.6 (1788): 'There is no other head of the Church but "
       "the Lord Jesus Christ: nor can the Pope of Rome in any sense "
       "be head thereof.'"
   ),
   legacy=(
       "The 1646 identification has been the most polemical clause "
       "of the Standards through Reformation history. Modern "
       "Reformed bodies that retain the 1646 text (Free Church of "
       "Scotland, Reformed Presbyterian Church of North America) "
       "have continued to affirm the Pope-as-Antichrist "
       "identification, often with explanatory notes. The American "
       "1788 revision has been followed by the PCA, OPC, and most "
       "American Reformed bodies."
   ),
   references=['WCF XXV.6 (1646)', 'WCF XXV.6 (American 1788)'])


_c('lawful-oaths-and-the-quaker-question', 'Lawful Oaths',
   '1646',
   locus_key='civil_last_things',
   attribute_keys=['civil_last_things_lawful_oaths_and_marriage'],
   tagline="May Christians take oaths? May the magistrate require them?",
   background=(
       "Christ's words 'Swear not at all' (Matt. 5:34, James 5:12) had "
       "been taken by Anabaptists and (later) Quakers as a categorical "
       "prohibition: no Christian may take any oath, judicial or "
       "otherwise. The Reformed had always held the contrary: lawful "
       "oaths, taken in truth, judgement, and seriousness, are not only "
       "permissible but are an act of religious worship. The 1640s saw "
       "the Quakers begin (George Fox first preached in 1647); the "
       "Solemn League and Covenant itself was a national oath; and "
       "magistrate-required oaths (the Engagement, the Oath of "
       "Allegiance, judicial oaths) were politically central."
   ),
   summary=(
       "WCF XXII.1-7 affirms the lawfulness of oaths in great detail. "
       "XXII.1: 'A lawful oath is a part of religious worship, wherein, "
       "upon just occasion, the person swearing solemnly calleth God to "
       "witness what he asserteth or promiseth.' XXII.2: oaths are to "
       "be by 'the name of God only.' XXII.3: oaths must be taken in "
       "truth, judgement, and weight; not lightly, not falsely. XXII.4: "
       "oaths bind even when sworn to a person of false religion. "
       "XXII.5-7 handle vows similarly. Thomas Gataker was the chapter's "
       "principal drafter; his learning in classical and rabbinical "
       "sources made him the natural choice for the locus."
   ),
   parties=[
       {
           'name': 'The Reformed pro-oath consensus',
           'persona_slugs': ['thomas-gataker', 'anthony-tuckney',
                             'edward-reynolds', 'edmund-calamy-elder'],
           'position': "Lawful oaths, taken in truth, judgement, and "
                       "seriousness, are a part of religious worship. "
                       "Christ's prohibition of 'swearing at all' is "
                       "directed at vain and irreverent swearing, "
                       "not at lawful judicial and covenantal oaths.",
       },
       {
           'name': 'The Anabaptist/Quaker absolute prohibition '
                   '(rejected; mostly outside the Assembly)',
           'persona_slugs': [],
           'position': "All oaths are forbidden by Christ's command "
                       "(Matt. 5:34, James 5:12). The Christian's "
                       "yea is to be yea and nay nay; oaths are an "
                       "accommodation to sinful human society that "
                       "Christ has abolished. George Fox and the "
                       "early Quakers.",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF XXII.1: 'A lawful oath is a part of religious worship, "
       "wherein, upon just occasion, the person swearing solemnly "
       "calleth God to witness what he asserteth or promiseth, and "
       "to judge him according to the truth or falsehood of what he "
       "sweareth.'"
   ),
   legacy=(
       "The Quaker refusal of oaths produced extensive 17th- and "
       "18th-century legal accommodation — the Affirmation Acts of "
       "1696, 1721, and 1722 in England, and corresponding statutes "
       "in colonial America — that allowed Quakers (and later other "
       "scrupling Christians) to substitute affirmations for oaths. "
       "The Westminster doctrine of lawful oaths underlies the "
       "judicial oath system inherited by the common-law world."
   ),
   references=['WCF XXII.1-7'])


_c('grounds-of-divorce', 'Grounds of Divorce: Adultery and Wilful Desertion',
   '1646',
   locus_key='civil_last_things',
   attribute_keys=['civil_last_things_lawful_oaths_and_marriage'],
   tagline='Two scriptural grounds for the dissolution of a true marriage.',
   background=(
       "Roman canon law held marriage absolutely indissoluble: even "
       "adultery did not warrant the dissolution of the bond (though "
       "separation from bed and board was permitted). The Continental "
       "Reformed had broken with this position, allowing divorce on "
       "grounds of adultery (Matt. 19:9) and (in Calvin's reading) "
       "wilful desertion (1 Cor. 7:15). Erasmus had argued more "
       "expansively for additional grounds, but the mainline Reformed "
       "had taken the two-grounds position. Westminster needed to "
       "settle the question for English and Scottish ecclesiastical "
       "practice."
   ),
   summary=(
       "WCF XXIV.5-6 affirms the two-grounds Reformed position. XXIV.5: "
       "'Adultery or fornication committed after a contract, being "
       "detected before marriage, giveth just occasion to the innocent "
       "party to dissolve that contract.' XXIV.6: 'In the case of "
       "adultery after marriage, it is lawful for the innocent party "
       "to sue out a divorce: and after the divorce, to marry "
       "another…' and 'nothing but adultery, or such wilful desertion "
       "as can no way be remedied by the church or civil magistrate, "
       "is cause sufficient of dissolving the bond of marriage.' This "
       "is more permissive than the strictest Catholic and Anglican "
       "readings (which limited remarriage even after adultery) and "
       "stricter than the Erasmian and most later Protestant readings "
       "(which permitted additional grounds)."
   ),
   parties=[
       {
           'name': 'The Reformed two-grounds position',
           'persona_slugs': ['edmund-calamy-elder', 'edward-reynolds',
                             'anthony-tuckney', 'samuel-rutherford'],
           'position': "Marriage is dissoluble only on two scriptural "
                       "grounds: adultery (Matt. 19:9) and wilful "
                       "desertion (1 Cor. 7:15). On either ground "
                       "the innocent party may remarry.",
       },
       {
           'name': 'Roman absolute indissolubility (rejected)',
           'persona_slugs': [],
           'position': "Marriage is absolutely indissoluble; adultery "
                       "permits separation from bed and board but "
                       "not remarriage. Trent, Session XXIV.",
       },
       {
           'name': 'Erasmian expansive grounds (rejected by the Assembly)',
           'persona_slugs': [],
           'position': "Multiple grounds for divorce beyond adultery "
                       "and desertion — including cruelty, incompatibility, "
                       "incurable illness, mutual consent. Erasmus, "
                       "and (later, more radically) John Milton's "
                       "*Doctrine and Discipline of Divorce* (1643).",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF XXIV.6: 'Although the corruption of man be such as is apt "
       "to study arguments unduly to put asunder those whom God hath "
       "joined together in marriage; yet nothing but adultery, or "
       "such wilful desertion as can no way be remedied by the "
       "church or civil magistrate, is cause sufficient of "
       "dissolving the bond of marriage.'"
   ),
   legacy=(
       "Milton's *Doctrine and Discipline of Divorce* (1643), "
       "*Tetrachordon* (1645), and *Colasterion* (1645) had pressed "
       "the case for expansive grounds — incompatibility, irreconcilable "
       "difference — against what would become the Westminster "
       "position; Milton's tracts were attacked by Herbert Palmer "
       "before Parliament in 1644. The two-grounds position remained "
       "the Reformed standard until 20th-century revisions: the "
       "Presbyterian Church in America (PCA) maintains the "
       "Westminster reading; the PCUSA loosened the language in the "
       "20th century."
   ),
   references=['WCF XXIV.5-6'])


_c('the-conscious-intermediate-state', 'The Conscious Intermediate State',
   '1647',
   locus_key='civil_last_things',
   attribute_keys=['civil_last_things_intermediate_state'],
   tagline='No purgatory, no soul-sleep — the soul’s immediate conscious entry into heaven or judgement.',
   background=(
       "The Reformed had to handle two alternatives. (1) Christian "
       "mortalism (also called *psychopannychism* or 'soul-sleep'): "
       "the soul sleeps unconsciously between death and the "
       "resurrection. The position had been held by some Anabaptists, "
       "Henry Vane the Younger arguably tilted that way, and John "
       "Milton would defend it explicitly in *De Doctrina Christiana* "
       "(1820s posthum.). (2) The Roman scheme: souls of the "
       "imperfectly purified pass through purgatorial fire to satisfy "
       "for unremitted temporal punishment; OT saints had been held in "
       "the *Limbus Patrum* until Christ's descent. Both were to be "
       "rejected. The Reformed position — articulated by Calvin in "
       "*Psychopannychia* (1542, his first published treatise) — was "
       "that souls separate consciously from the body at death and "
       "immediately enter into heaven (the righteous) or hell (the "
       "wicked) to await the resurrection."
   ),
   summary=(
       "WCF XXXII.1 articulates the immediate-conscious position with "
       "unusual rhetorical force: 'The bodies of men, after death, "
       "return to dust, and see corruption: but their souls, which "
       "neither die nor sleep, having an immortal subsistence, "
       "immediately return to God who gave them. The souls of the "
       "righteous, being then made perfect in holiness, are received "
       "into the highest heavens, where they behold the face of God in "
       "light and glory, waiting for the full redemption of their "
       "bodies. And the souls of the wicked are cast into hell, where "
       "they remain in torments and utter darkness, reserved to the "
       "judgment of the great day. Beside these two places, for souls "
       "separated from their bodies, the Scripture acknowledgeth "
       "none.' The closing clause is the direct rejection of purgatory "
       "and *limbus*."
   ),
   parties=[
       {
           'name': 'The Westminster immediate-conscious consensus',
           'persona_slugs': ['edmund-calamy-elder', 'edward-reynolds',
                             'anthony-tuckney', 'samuel-rutherford'],
           'position': "The soul neither dies nor sleeps but at death "
                       "immediately enters heaven (the righteous) or "
                       "hell (the wicked) to await the resurrection "
                       "and final judgement. No purgatory, no *limbus*, "
                       "no soul-sleep.",
       },
       {
           'name': 'Christian mortalism / soul-sleep (rejected)',
           'persona_slugs': [],
           'position': "The soul sleeps unconsciously between death "
                       "and resurrection, since 'the dead know not "
                       "anything' (Eccl. 9:5). Some Anabaptists; "
                       "later John Milton.",
       },
       {
           'name': 'Roman purgatory and limbus (rejected)',
           'persona_slugs': [],
           'position': "Souls of the imperfectly purified pass through "
                       "purgatorial fire to satisfy for unremitted "
                       "temporal punishment; OT saints had been in "
                       "*limbus patrum* until Christ's descent. "
                       "Trent, Session XXV.",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF XXXII.1: 'The bodies of men, after death, return to dust, "
       "and see corruption: but their souls, which neither die nor "
       "sleep, having an immortal subsistence, immediately return to "
       "God who gave them. The souls of the righteous, being then "
       "made perfect in holiness, are received into the highest "
       "heavens, where they behold the face of God in light and "
       "glory, waiting for the full redemption of their bodies. And "
       "the souls of the wicked are cast into hell, where they "
       "remain in torments and utter darkness, reserved to the "
       "judgment of the great day. Beside these two places, for "
       "souls separated from their bodies, the Scripture "
       "acknowledgeth none.'"
   ),
   legacy=(
       "The Westminster position has been the Reformed standard ever "
       "since. Milton's *De Doctrina Christiana* (composed 1650s-60s, "
       "discovered 1823) defended Christian mortalism, but Milton's "
       "position remained marginal in the Reformed world. The "
       "doctrine of purgatory has continued to be the major "
       "Catholic-Protestant point of difference on the intermediate "
       "state. Twentieth-century evangelical handlings (Anthony "
       "Hoekema, John Cooper) defend the Westminster position; "
       "Christian materialist and physicalist positions (Nancey Murphy, "
       "Joel Green) revive the soul-sleep alternative."
   ),
   references=['WCF XXXII.1'])


_c('the-final-judgment', 'The Final Judgment and the Last Things',
   '1647',
   locus_key='civil_last_things',
   attribute_keys=['civil_last_things_final_judgment'],
   tagline='One final judgement, by Christ, with eternal consequences.',
   background=(
       "Reformed eschatology had taken a series of positions inherited "
       "from the catholic Christian tradition: a final, universal "
       "judgement of all human persons and angels at the end of the "
       "age; conducted by Jesus Christ as the appointed Judge; with "
       "eternal life for the righteous and eternal punishment for the "
       "wicked. Various alternatives circulated. Annihilationism — "
       "developed by some Socinians — held that the wicked would be "
       "finally destroyed rather than punished eternally. Origenist "
       "*apokatastasis* (universal restoration) — taught by some "
       "radical groups and (later) Peter Sterry — held that all "
       "rational creatures would eventually be saved. The "
       "premillennialists (Fifth Monarchy Men in their radical wing) "
       "held to two distinct resurrections separated by a millennial "
       "reign on earth, with Christ returning before the millennium. "
       "The Assembly handled the question briefly but firmly."
   ),
   summary=(
       "WCF XXXIII.1-3 articulates the doctrine in two short paragraphs. "
       "XXXIII.1: 'God hath appointed a day, wherein he will judge the "
       "world in righteousness by Jesus Christ.' XXXIII.2: 'the "
       "righteous go into everlasting life…the wicked, who know not "
       "God…shall be cast into eternal torments, and be punished with "
       "everlasting destruction.' XXXIII.3 closes with the pastoral "
       "use: the certainty of the day deters from sin and consoles the "
       "godly. The eternal punishment clause excludes annihilationism "
       "and universal restoration. The single-judgement framing does "
       "not adopt the premillennial double-resurrection scheme, but "
       "neither does it explicitly exclude it; the Assembly was "
       "broadly post-millennial in instinct without making millennial "
       "schemes confessional."
   ),
   parties=[
       {
           'name': 'The Westminster final-judgement consensus',
           'persona_slugs': ['edward-reynolds', 'anthony-tuckney',
                             'edmund-calamy-elder', 'samuel-rutherford'],
           'position': "One final, universal judgement by Christ at "
                       "the end of the age, with eternal life for "
                       "the righteous and eternal punishment for "
                       "the wicked.",
       },
       {
           'name': 'Annihilationism (rejected)',
           'persona_slugs': [],
           'position': "The wicked are finally annihilated rather "
                       "than eternally punished. Socinian "
                       "antecedents; later conditionalists.",
       },
       {
           'name': 'Universal restoration (rejected)',
           'persona_slugs': [],
           'position': "All rational creatures are eventually saved "
                       "(*apokatastasis*). Origenist tendency; some "
                       "radical Independents (Peter Sterry's "
                       "tendencies).",
       },
   ],
   outcome='settled-clear',
   language=(
       "WCF XXXIII.1: 'God hath appointed a day, wherein he will judge "
       "the world, in righteousness, by Jesus Christ, to whom all "
       "power and judgment is given of the Father.' "
       "WCF XXXIII.2: '…the righteous go into everlasting life, and "
       "receive that fullness of joy and refreshing, which shall come "
       "from the presence of the Lord; but the wicked who know not "
       "God, and obey not the gospel of Jesus Christ, shall be cast "
       "into eternal torments, and be punished with everlasting "
       "destruction from the presence of the Lord, and from the glory "
       "of his power.'"
   ),
   legacy=(
       "The Westminster handling of the final judgement has been the "
       "Reformed standard. The 'evangelical-conditionalist' movement "
       "(John Stott in *Evangelical Essentials* 1988, Edward Fudge's "
       "*The Fire That Consumes* 1982) revived the annihilationist "
       "alternative as a live option for evangelicals; Reformed "
       "responses (Robert Peterson's *Hell on Trial* 1995, the OPC "
       "responses) defended the Westminster eternal-punishment "
       "reading. The premillennial schemes (dispensationalist "
       "premillennialism in 20th-century evangelicalism) developed in "
       "a direction the Westminster divines would have considered "
       "marginal."
   ),
   references=['WCF XXXIII.1-3'])


# ======================================================================
# IX. PROCEDURAL & STRUCTURAL CRUXES
# ======================================================================

_c('the-solemn-league-and-covenant', 'The Solemn League and Covenant',
   'August–September 1643',
   locus_key='ecclesiology_worship',
   attribute_keys=[],
   tagline='The Anglo-Scottish covenant that brought the Scots into the war and into the Assembly.',
   background=(
       "By summer 1643 the parliamentary side in the English Civil War "
       "was in serious trouble. Royalist forces had taken Bristol and "
       "much of the West Country; the parliamentary army was reduced "
       "and discouraged. The Long Parliament needed Scottish military "
       "support, which the Scottish Convention of Estates and General "
       "Assembly would only give on religious terms. Alexander "
       "Henderson, Archibald Johnston of Wariston, Sir Henry Vane the "
       "Younger, and Philip Nye negotiated the terms in Edinburgh in "
       "August 1643."
   ),
   summary=(
       "The Solemn League and Covenant was sworn by the Westminster "
       "Assembly and the Long Parliament on 25 September 1643 at St "
       "Margaret's, Westminster. Its six articles committed the three "
       "kingdoms (England, Scotland, Ireland) to: the preservation of "
       "the reformed religion in Scotland; the reformation of religion "
       "in England and Ireland according to the Word of God and the "
       "example of the best reformed churches; the extirpation of "
       "popery, prelacy, heresy, schism, profaneness; the preservation "
       "of parliamentary rights and royal authority; mutual defence "
       "and assistance; and personal reformation. The phrase 'according "
       "to the Word of God and the example of the best reformed "
       "churches' was a deliberate ambiguity — the Scots read it as "
       "binding to Presbyterian uniformity, the Independents read it "
       "as binding only to scriptural reform. The Covenant brought a "
       "Scottish army into England (January 1644) and brought the "
       "Scottish Commissioners (Henderson, Rutherford, Gillespie, "
       "Baillie + the lay commissioners) into the Assembly."
   ),
   parties=[
       {
           'name': 'The Scottish Covenanters',
           'persona_slugs': ['alexander-henderson',
                             'archibald-johnston-wariston',
                             'samuel-rutherford',
                             'george-gillespie'],
           'position': "The Covenant binds the three kingdoms to "
                       "Presbyterian uniformity; the phrase 'according "
                       "to the Word of God and the example of the "
                       "best reformed churches' means the Reformed "
                       "Scottish settlement.",
       },
       {
           'name': 'The English negotiators',
           'persona_slugs': ['henry-vane-younger', 'oliver-st-john',
                             'philip-nye', 'stephen-marshall'],
           'position': "The Covenant binds to scriptural reform but "
                       "preserves latitude on the specific polity. "
                       "Vane and Nye drafted the 'according to the "
                       "Word' clause to preserve room for Independent "
                       "polity.",
       },
   ],
   outcome='settled-clear',
   language=(
       "The Solemn League and Covenant, Article I: '…we shall "
       "sincerely, really, and constantly, through the grace of God, "
       "endeavour, in our several places and callings, the "
       "preservation of the reformed religion in the Church of "
       "Scotland, in doctrine, worship, discipline, and government, "
       "against our common enemies; the reformation of religion in "
       "the kingdoms of England and Ireland, in doctrine, worship, "
       "discipline, and government, according to the Word of God, "
       "and the example of the best reformed churches…'"
   ),
   legacy=(
       "The Solemn League was the structural condition of the "
       "Assembly's work — it brought the Scots in and committed the "
       "English to broadly Reformed reformation. Its religious "
       "settlement was never fully implemented in England before "
       "Cromwell's Independents took over (1647-49); after the "
       "Restoration in 1660, Charles II's regime treated the Covenant "
       "as treasonable and prosecuted Covenanters. The Covenant "
       "remains a foundational document for the Reformed Presbyterian "
       "(Covenanter) tradition, which still treats it as binding."
   ),
   references=['Solemn League and Covenant (1643)'])


_c('the-self-denying-ordinance-and-the-new-model',
   'The Self-Denying Ordinance and the New Model Army',
   'December 1644 – April 1645',
   locus_key='ecclesiology_worship',
   attribute_keys=[],
   tagline='The army reorganisation that empowered the Independent interest the Assembly’s Presbyterians had to negotiate with.',
   background=(
       "By autumn 1644 the parliamentary military command was "
       "factionalised: the Earl of Manchester (Eastern Association) "
       "favoured a negotiated settlement with the king; Cromwell, his "
       "Lieutenant-General of Horse, favoured prosecuting the war to "
       "victory. Their famous quarrel after the indecisive Second "
       "Battle of Newbury (October 1644) — Manchester's 'If we beat "
       "the King ninety and nine times yet he is King still…but if "
       "the King beat us once we shall be all hanged' against "
       "Cromwell's 'My Lord, if this be so, why did we take up arms "
       "at first?' — brought the matter to the Long Parliament. Zouch "
       "Tate (a lay assessor at the Assembly) sponsored the Self-"
       "Denying Ordinance in December 1644: members of either House "
       "of Parliament should resign their military commands."
   ),
   summary=(
       "The Self-Denying Ordinance passed on 3 April 1645. The army "
       "was reorganised as the New Model under Sir Thomas Fairfax as "
       "Lord General, with Cromwell exempted (by special vote) and "
       "made Lieutenant-General. The new army was professional, "
       "well-trained, well-paid, and (crucially for the Assembly's "
       "Presbyterian settlement) heavily Independent in religious "
       "sympathies. The New Model won the war (Naseby, June 1645; "
       "Langport, July 1645; the western campaign through 1645-46) "
       "and then politicised in 1647, presenting the Heads of the "
       "Proposals against the parliamentary Presbyterians. The army's "
       "1647-49 dominance, culminating in Pride's Purge and the "
       "regicide, frustrated the Presbyterian settlement the Assembly "
       "had drafted. The Standards remained confessional, but the "
       "polity settlement was never fully implemented in England."
   ),
   parties=[
       {
           'name': 'The Self-Denying parliamentary managers',
           'persona_slugs': ['zouch-tate', 'henry-vane-younger',
                             'oliver-st-john', 'sir-arthur-haselrig'],
           'position': "The army must be professionalised and "
                       "depoliticised; sitting MPs and peers must "
                       "resign their commands. The settlement of the "
                       "kingdom is the parliamentary task; the army's "
                       "task is military.",
       },
       {
           'name': 'The Presbyterian peers (resistant)',
           'persona_slugs': ['edward-montagu-manchester',
                             'algernon-percy-northumberland',
                             'philip-herbert-pembroke'],
           'position': "The Ordinance is a manoeuvre to displace "
                       "moderate aristocratic command in favour of "
                       "the militant Independent interest. It will "
                       "make the army politically independent of "
                       "Parliament.",
       },
   ],
   outcome='settled-clear',
   language=(
       "The Self-Denying Ordinance, 3 April 1645: '…all and every of "
       "the members of either House of Parliament shall be discharged "
       "at the end of forty days, after the passing of this Ordinance, "
       "of, and from all and every office or command, military or "
       "civil, granted or conferred by both, or either of the said "
       "Houses…'"
   ),
   legacy=(
       "The Self-Denying Ordinance and the New Model produced both "
       "the parliamentary victory and the eventual frustration of the "
       "Presbyterian settlement. The army's Independent religious "
       "sympathies — and the political ascendancy that followed — "
       "made the Westminster polity settlement a dead letter in "
       "England within four years of the Confession's completion. "
       "The Standards survived as confessional document; the polity "
       "they prescribed did not."
   ),
   references=['Self-Denying Ordinance (1645)'])


_c('the-1788-american-revision', 'The 1788 American Revision',
   '1787–1788 (post-Assembly)',
   locus_key='civil_last_things',
   attribute_keys=['civil_last_things_magistrate_role'],
   tagline='How the American Presbyterians rewrote the magistrate chapters for a disestablished republic.',
   background=(
       "When the American Presbyterian Church was constituted as a "
       "national body in 1788 (the first General Assembly of the "
       "Presbyterian Church in the United States of America met in "
       "Philadelphia, May 1789), the Westminster Confession was the "
       "natural confessional choice. But the 1646 Confession's "
       "magistrate chapter (XXIII) gave the civil magistrate "
       "authority to suppress heresy and call synods — language that "
       "was not only impracticable but politically incompatible with "
       "the new federal Constitution's First Amendment (1791) "
       "disestablishment. Chapter XX.4 had similar problems. The "
       "American Synod commissioned a revision."
   ),
   summary=(
       "The 1788 revision rewrote WCF XX.4, XXIII.3, and XXXI.2 to "
       "align with disestablishment. The magistrate's duty became "
       "to 'protect the Church of our common Lord, without giving the "
       "preference to any denomination of Christians above the rest' "
       "and 'so to order all public assemblies as may be convenient' "
       "without specifically suppressing heresies or calling "
       "synods. The clause identifying the Pope as Antichrist (XXV.6) "
       "was also softened. The revision is the major confessional "
       "fracture in the Westminster tradition: the Reformed "
       "Presbyterian (Covenanter) tradition kept the 1646 text; the "
       "PCUSA, PCA, OPC, and most American Presbyterian bodies "
       "follow the 1788. Both texts remain confessional in their "
       "respective traditions."
   ),
   parties=[
       {
           'name': 'The 1788 American revisers',
           'persona_slugs': [],
           'position': "The magistrate chapters must be rewritten "
                       "to fit a disestablished republican context; "
                       "the civil magistrate protects the church but "
                       "does not establish, direct, or coerce.",
       },
       {
           'name': 'The Reformed Presbyterian (Covenanter) retention',
           'persona_slugs': [],
           'position': "The 1646 text is confessional; the magistrate's "
                       "duty to suppress heresy and establish the "
                       "true religion is biblical. Disestablishment "
                       "is a departure from biblical magistracy, not "
                       "a progress.",
       },
   ],
   outcome='mixed',
   language=(
       "WCF XXIII.3 (American 1788): 'Civil magistrates may not assume "
       "to themselves the administration of the Word and sacraments; "
       "or the power of the keys of the kingdom of heaven; or, in "
       "the least, interfere in matters of faith. Yet, as nursing "
       "fathers, it is the duty of civil magistrates to protect the "
       "Church of our common Lord, without giving the preference to "
       "any denomination of Christians above the rest…'"
   ),
   legacy=(
       "The 1788 revision became the working confessional text of "
       "American Presbyterianism. The 1903 PCUSA revisions further "
       "softened the language on the decree and the heathen; the "
       "1936 OPC formation reaffirmed the 1788 text without the 1903 "
       "amendments. The PCA at its 1973 formation also adopted the "
       "1788 text. The Reformed Presbyterian Church of North America "
       "and the Reformed Presbyterian Church of Scotland continue to "
       "use the 1646 text. Modern arguments over Christian "
       "nationalism, religious liberty, and church-state relations "
       "continue to play out across this Westminster fracture."
   ),
   references=['WCF XX.4 (1646 vs 1788)',
               'WCF XXIII.3 (1646 vs 1788)',
               'WCF XXV.6 (1646 vs 1788)',
               'WCF XXXI.2 (1646 vs 1788)'])


# ======================================================================
# CROSS-REFERENCES BETWEEN CRUXES
#
# Applied after all _c() calls so that every slug referenced already
# exists.  Each crux gets a 'related_crux_slugs' list of the slugs
# it is meaningfully connected to — not "everything in the same locus"
# but specific doctrinal or procedural ties.
# ======================================================================

_RELATED = {
    'the-canon-and-the-apocrypha': [
        'good-and-necessary-consequence',
    ],
    'good-and-necessary-consequence': [
        'the-canon-and-the-apocrypha',
    ],
    'the-order-of-the-decrees': [
        'the-extent-of-the-atonement',
        'the-decree-of-reprobation',
        'the-covenant-of-redemption',
    ],
    'the-extent-of-the-atonement': [
        'the-order-of-the-decrees',
        'the-decree-of-reprobation',
        'active-obedience-imputation',
    ],
    'the-decree-of-reprobation': [
        'the-order-of-the-decrees',
        'the-extent-of-the-atonement',
    ],
    'the-covenant-of-redemption': [
        'the-order-of-the-decrees',
        'the-mosaic-covenant',
    ],
    'the-mosaic-covenant': [
        'the-children-of-believers',
        'the-covenant-of-redemption',
        'the-tripartite-division-of-the-law',
    ],
    'the-children-of-believers': [
        'the-mosaic-covenant',
        'sacramental-efficacy',
    ],
    'active-obedience-imputation': [
        'the-extent-of-the-atonement',
        'justification-and-the-antinomian-crisis',
    ],
    'the-descent-into-hell': [
        'the-conscious-intermediate-state',
    ],
    'justification-and-the-antinomian-crisis': [
        'the-third-use-of-the-law',
        'assurance-of-the-essence-of-faith',
        'active-obedience-imputation',
    ],
    'assurance-of-the-essence-of-faith': [
        'perseverance-of-the-saints',
        'justification-and-the-antinomian-crisis',
    ],
    'perseverance-of-the-saints': [
        'assurance-of-the-essence-of-faith',
    ],
    'the-third-use-of-the-law': [
        'justification-and-the-antinomian-crisis',
        'the-tripartite-division-of-the-law',
        'the-strict-sabbath',
    ],
    'the-strict-sabbath': [
        'the-regulative-principle',
        'the-third-use-of-the-law',
    ],
    'the-tripartite-division-of-the-law': [
        'the-third-use-of-the-law',
        'the-mosaic-covenant',
    ],
    'the-grand-debate-polity': [
        'the-erastian-question',
        'the-solemn-league-and-covenant',
        'the-self-denying-ordinance-and-the-new-model',
    ],
    'the-erastian-question': [
        'the-grand-debate-polity',
        'the-magistrates-two-tables',
    ],
    'the-regulative-principle': [
        'the-strict-sabbath',
        'the-rouse-psalter',
        'sacramental-efficacy',
    ],
    'sacramental-efficacy': [
        'the-children-of-believers',
        'the-regulative-principle',
    ],
    'the-rouse-psalter': [
        'the-regulative-principle',
    ],
    'the-magistrates-two-tables': [
        'the-erastian-question',
        'the-pope-as-antichrist',
        'the-1788-american-revision',
        'the-solemn-league-and-covenant',
    ],
    'the-pope-as-antichrist': [
        'the-magistrates-two-tables',
        'the-1788-american-revision',
    ],
    'lawful-oaths-and-the-quaker-question': [
        'grounds-of-divorce',
    ],
    'grounds-of-divorce': [
        'lawful-oaths-and-the-quaker-question',
    ],
    'the-conscious-intermediate-state': [
        'the-final-judgment',
        'the-descent-into-hell',
    ],
    'the-final-judgment': [
        'the-conscious-intermediate-state',
    ],
    'the-solemn-league-and-covenant': [
        'the-grand-debate-polity',
        'the-magistrates-two-tables',
        'the-self-denying-ordinance-and-the-new-model',
    ],
    'the-self-denying-ordinance-and-the-new-model': [
        'the-grand-debate-polity',
        'the-solemn-league-and-covenant',
    ],
    'the-1788-american-revision': [
        'the-magistrates-two-tables',
        'the-pope-as-antichrist',
    ],
}

for _slug, _related in _RELATED.items():
    _crux = get_crux_by_slug(_slug)
    if _crux:
        _crux['related_crux_slugs'] = _related
