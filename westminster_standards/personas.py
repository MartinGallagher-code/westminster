"""Westminster personas — the divines of the Westminster Assembly.

The Assembly was convened by the Long Parliament's ordinance of 12 June
1643, which named 121 English and Welsh divines together with ten Lords
and twenty Commons as lay assessors. A further 21 ministers were
'super-added' between August 1643 and the closing years; the Scottish
General Assembly sent four ministerial commissioners (Henderson,
Rutherford, Gillespie, Baillie) and three to four lay commissioners
(Lauderdale, Loudoun, Cassillis, Wariston). The working core was a few
dozen — many of the 121 originally named never appeared, several of
the bishops named (Ussher, Hall, Brownrig, Westfield) declined out of
loyalty to the king, and a few (notably Daniel Featley) were expelled
during the war.

This file lists the substantively documented Assembly members and the
principal absentees and refusers. Each entry inherits the
``WESTMINSTER_BASELINE_ATTRS`` profile from ``data.py`` and overrides
only on points of departure (Independency, Erastianism, hypothetical
universalism, supralapsarianism, etc.). Slugs are unique; numbers are
sequential in the order added below (officers → scribes → Scots →
English Presbyterians → Independents → Erastians → lay assessors →
named-but-declined).
"""

from .data import WESTMINSTER_BASELINE_ATTRS


PERSONAS = []
_COUNTER = [0]


def _p(slug, name, dates, role, tagline, bio, *,
       overrides=None, works=None, influences=None):
    _COUNTER[0] += 1
    attrs = dict(WESTMINSTER_BASELINE_ATTRS)
    if overrides:
        attrs.update(overrides)
    PERSONAS.append({
        'slug': slug,
        'number': _COUNTER[0],
        'name': name,
        'dates': dates,
        'role': role,
        'tagline': tagline,
        'bio': bio,
        'attrs': attrs,
        'works': works or [],
        'influences': influences or [],
    })


def get_persona_by_slug(slug):
    for p in PERSONAS:
        if p.get('slug') == slug:
            return p
    return None


# ----------------------------------------------------------------------
# Role glossary
#
# Many members of the Assembly — especially the county ministers named in
# the 1643 ordinance and the parliamentary lay assessors — left almost no
# personal record. Rather than invent biography, each persona page shows a
# factual note on the *institutional role* the member held, so that even a
# sparsely-documented figure is placed in the working structure of the
# Assembly. ``role_context`` matches a persona's ``role`` string (by
# substring, most-specific first) to one of these notes.
# ----------------------------------------------------------------------

ROLE_CONTEXTS = [
    (('lay assessor (commons)',), 'Lay Assessor — House of Commons',
     "Parliament seated lay assessors alongside the divines to represent its "
     "interest and keep it informed of the Assembly's progress. The ordinance "
     "of 1643 named thirty members of the House of Commons as assessors; they "
     "could take part in debate but were not among the voting divines, and "
     "their attendance was often occasional as the war and parliamentary "
     "business pressed on them."),
    (('lay assessor (lords)',), 'Lay Assessor — House of Lords',
     "Parliament seated lay assessors from both Houses to sit with the divines "
     "and represent its interest. Ten peers were named from the House of Lords "
     "as lay assessors; like the Commons assessors they had voice in the "
     "Assembly but were not voting members, and they attended as their other "
     "duties allowed."),
    (('first assessor', 'second assessor'), 'Assessor to the Prolocutor',
     "The two assessors were senior divines appointed to assist the Prolocutor "
     "and to take the chair in his absence — which, given William Twisse's "
     "infirmity, meant they did much of the real work of presiding. Cornelius "
     "Burgess and John White were the original assessors."),
    (('prolocutor',), 'Prolocutor',
     "The Prolocutor was the Assembly's presiding officer — chairman and "
     "moderator — who put the questions, kept order, and represented the body "
     "to Parliament. William Twisse held the office from the opening in July "
     "1643; on his death in 1646 Charles Herle was chosen to succeed him and "
     "presided through the completion of the Catechisms."),
    (('scribe',), 'Scribe',
     "The scribes kept the Assembly's official minutes and recorded its votes. "
     "Henry Roborough and Adoniram Byfield served throughout; the minutes in "
     "their hand are the principal surviving record of the debates that "
     "produced the Standards."),
    (('scottish commissioner',), 'Scottish Commissioner',
     "Under the Solemn League and Covenant (1643) the Church of Scotland sent "
     "commissioners — ministers and ruling elders — to sit with the Assembly. "
     "They had voice in debate but no formal vote, yet their influence on the "
     "Standards, especially on worship and presbyterian polity, was decisive. "
     "Alexander Henderson, Samuel Rutherford, George Gillespie, and Robert "
     "Baillie were the leading ministerial commissioners."),
    (('erastian',), 'Erastian party',
     "The Erastians held that the power of church censures — above all "
     "excommunication — belonged ultimately to the civil magistrate rather "
     "than to independent church courts. Thomas Coleman and John Lightfoot, "
     "with the lay civilian John Selden, were its chief voices; the question "
     "was among the most bitterly fought at the Assembly."),
    (('dissenting brother', 'independent'), 'Independent / Dissenting Brethren',
     "A small but articulate minority of Congregationalist divines — the "
     "'Dissenting Brethren' — who pressed for a gathered-church polity against "
     "the Presbyterian majority. Their Apologeticall Narration (1644) and "
     "their dissents in the Grand Debate over church government shaped the "
     "Confession's carefully worded chapters and anticipated the Savoy "
     "Declaration of 1658."),
    (('originally named', 'declined', 'expelled'),
     'Named in the ordinance',
     "The 1643 ordinance that summoned the Assembly named some 121 divines. A "
     "number — chiefly episcopalians and royalists who heeded the King's "
     "proclamation forbidding the Assembly — never took their seats or sat "
     "only briefly; a few were later expelled. They are listed here for "
     "completeness as part of the originally-summoned roster."),
    (('superadded',), 'Super-added divine',
     "Around twenty-one ministers were 'super-added' to the Assembly between "
     "1643 and its closing years, to replace those who never appeared or had "
     "died and to bring in particular gifts. They sat on the same footing as "
     "the divines named in the original ordinance."),
    (('english presbyterian minister',), 'English Presbyterian divine',
     "The great majority of the sitting members were English parish ministers "
     "of Presbyterian conviction. They formed the drafting core of the "
     "Assembly, manning its three standing committees and supplying most of "
     "the text of the Confession, the two Catechisms, and the Directory for "
     "Public Worship."),
]


def role_context(role):
    """Return ``{'label', 'text'}`` describing a persona's Assembly role, or
    ``None`` if the role string matches no known category."""
    if not role:
        return None
    low = role.lower()
    for matchers, label, text in ROLE_CONTEXTS:
        if any(m in low for m in matchers):
            return {'label': label, 'text': text}
    return None


# ======================================================================
# I.  PROLOCUTORS, ASSESSORS, SCRIBES
# ======================================================================

_p('william-twisse', 'William Twisse', '1577–1646',
   'Prolocutor (1643–1646)',
   "Westminster's first Prolocutor; the most learned supralapsarian of his generation.",
   "Trained at New College Oxford under John Rainolds, Twisse spent the 1620s and 1630s in pastoral and polemical labours at Newbury, defending Calvinist orthodoxy against Arminius, Vorstius, Jackson, and (in three vast Latin folios) the Jesuit Jacobus Acontius. As Prolocutor he opened the Assembly on 1 July 1643 with a sermon on John 14:18. He was infirm by then and presided more as figurehead than driver, leaving the chair's work to the Assessors; he died in July 1646 just as the Confession was being completed.",
   overrides={'god_decree_order_of_decrees': 'Supralapsarian'},
   works=['Vindiciae Gratiae, Potestatis ac Providentiae Dei (1632)',
          'The Riches of Gods Love unto the Vessells of Mercy (1653)'])

_p('charles-herle', 'Charles Herle', '1598–1659',
   'Prolocutor (1646–1652)',
   'Succeeded Twisse; mediating Lancashire Presbyterian, drafter of the Larger Catechism.',
   "Rector of Winwick, Lancashire — one of the richest livings in England — Herle was a Civil War parliamentary chaplain and one of the steadier moderating voices at the Assembly. He chaired the committee that produced the Larger Catechism's exposition of the Decalogue. Elected Prolocutor on Twisse's death in July 1646, he presided through the completion of both Catechisms and the close of the active Assembly. He retired to Winwick at the Restoration and died there.",
   works=['The Independency on Scriptures of the Independency of Churches (1643)',
          'Davids Reserve (1645)'])

_p('cornelius-burgess', 'Cornelius Burgess', '1589–1665',
   'First Assessor',
   'London Presbyterian senior; preached the opening sermon to Parliament that called the Assembly.',
   "Lecturer at St Magnus the Martyr and St Paul's, Burgess was the most prominent London Presbyterian preacher of the early 1640s. He preached the November 1640 sermon before the Commons that helped catalyse the calling of the Assembly. As First Assessor he carried much of the actual procedural work. After 1660 he refused to conform, was deprived of his benefices, ruined financially by the Restoration land settlement, and died in obscurity.",
   works=['The Necessity and Benefit of Washing the Heart (1628)',
          'Two Sermons (1641)'])

_p('john-white-dorchester', 'John White (of Dorchester)', '1575–1648',
   'Second Assessor',
   '"Patriarch of Dorchester"; New England Company organiser and senior moderator.',
   "Rector of Holy Trinity, Dorchester for over forty years, where his catechetical and disciplinary regime made the town a Puritan model and seeded the Massachusetts Bay migration through the Dorchester Company. At Westminster, the elderly White served as Second Assessor and was widely respected as a non-partisan elder. He died in July 1648 before the Assembly's later petering-out under the Independent ascendancy.",
   works=['The Way to the Tree of Life (1647)',
          'A Commentary upon the Three First Chapters of Genesis (1656)'])

_p('henry-roborough', 'Henry Roborough', 'd. 1650',
   'Scribe',
   'Co-scribe with Byfield; kept the early sessions of the Assembly minutes.',
   "Educated at Christ's College Cambridge. Rector of St Leonard Eastcheap from 1631, Roborough was named first of the three formal scribes by the founding ordinance of 12 June 1643 — the scribes were non-voting but recorded the proceedings, and Roborough's hand fills the earliest stretches of the surviving manuscript minutes. He held conservative Presbyterian sympathies and signed multiple Sion College manifestoes against the rising Independent and Erastian factions in the late 1640s. He died in 1650 — too soon to see the Restoration ejections that would have caught him for nonconformity. His own theological positions left little independent trace beyond his scribal labour.",
   works=[])

_p('adoniram-byfield', 'Adoniram Byfield', 'd. c. 1660',
   'Scribe',
   'Co-scribe with Roborough; principal preserver of the Westminster manuscript minutes.',
   "Son of Nicholas Byfield, the Cheshire Puritan whose Marrow of the Oracles of God (1620) had been a standard catechetical handbook, and brother of Richard Byfield of Long Ditton. Adoniram served as one of the Assembly's two formal scribes alongside Henry Roborough and (later) John Wallis, recording the manuscript minutes that survive as our chief source for the Assembly's debates and form the basis of the modern editions (Mitchell and Struthers 1874; Van Dixhoorn, Oxford 2012). He held the parish of Fulham briefly, was chaplain to Sir William Constable's regiment in the New Model Army, and after the Assembly ministered in Berkshire and Surrey as an active Presbyterian under the Cromwellian church settlement. Died around 1660; the precise date is uncertain.",
   works=[])

_p('john-wallis', 'John Wallis', '1616–1703',
   'Scribe',
   'Junior scribe; later Savilian Professor of Geometry at Oxford and founding fellow of the Royal Society.',
   "A 27-year-old Cambridge-trained minister when he was appointed an Assembly scribe, Wallis is now remembered chiefly as one of the founders of modern mathematics. He published the *Arithmetica Infinitorum* (1656), invented the infinity symbol ∞, contributed to the early calculus, and was Savilian Professor of Geometry at Oxford from 1649 to his death. He cracked royalist ciphers for Parliament during the Civil Wars and remained a churchman of moderate Reformed convictions.",
   works=['Arithmetica Infinitorum (1656)',
          'Truth Tried (1643)'])


# ======================================================================
# II. SCOTTISH COMMISSIONERS — MINISTERS
# ======================================================================

_p('alexander-henderson', 'Alexander Henderson', '1583–1646',
   'Scottish Commissioner (minister)',
   'Chief architect of the Solemn League and Covenant; senior Scottish theological statesman.',
   "Minister at Leuchars (Fife) and then Edinburgh, Henderson led the Covenanter cause from its decisive 1638 victory over Laud's Prayer Book onward. He drafted the National Covenant (1638) and the Solemn League and Covenant (1643), and as senior Scottish commissioner at Westminster pressed the case for jure-divino presbyterianism. Worn out by the negotiations and the Uxbridge treaty, he died in August 1646; his body was carried back to Greyfriars.",
   overrides={'god_decree_order_of_decrees': 'Supralapsarian',
              'god_decree_covenant_of_redemption': 'Explicit-Developed'},
   works=['The Government and Order of the Church of Scotland (1641)',
          'The Bishops Doom (1638)'])

_p('samuel-rutherford', 'Samuel Rutherford', 'c. 1600–1661',
   'Scottish Commissioner (minister)',
   'Author of *Lex Rex*; fierce presbyterian, supralapsarian, mystical letter-writer.',
   "Professor of Divinity at St Andrews from 1639, Rutherford was the Assembly's most prolific Scottish theological pen — *Lex, Rex* (1644) gave Reformed political resistance theory its enduring statement; *The Due Right of Presbyteries* (1644) and *The Divine Right of Church Government* (1646) argued the polity case. His pastoral *Letters* (printed 1664) became one of the most beloved devotional books of the Reformed tradition. At the Restoration he was charged with treason but died before trial.",
   overrides={'god_decree_order_of_decrees': 'Supralapsarian',
              'god_decree_covenant_of_redemption': 'Explicit-Developed'},
   works=['Lex, Rex (1644)',
          'The Due Right of Presbyteries (1644)',
          'The Trial and Triumph of Faith (1645)',
          'The Covenant of Life Opened (1655)',
          'Letters (1664)'])

_p('george-gillespie', 'George Gillespie', '1613–1648',
   'Scottish Commissioner (minister)',
   'Youngest divine at Westminster; demolished the Erastian case in *Aaron’s Rod Blossoming*.',
   "Only 30 when he arrived in London, Gillespie was the youngest commissioner and quickly emerged as the sharpest debater. His famous extempore reply to Selden on the keys (1645) became Westminster lore; *Aaron's Rod Blossoming* (1646) is the canonical Reformed refutation of Erastianism. He returned to Scotland exhausted, was elected Moderator of the General Assembly in 1648, and died of consumption later that year aged only 35.",
   overrides={'god_decree_order_of_decrees': 'Supralapsarian',
              'god_decree_covenant_of_redemption': 'Explicit-Developed'},
   works=['A Dispute against the English Popish Ceremonies (1637)',
          'Aaron’s Rod Blossoming (1646)',
          'A Treatise of Miscellany Questions (1649)'])

_p('robert-baillie', 'Robert Baillie', '1602–1662',
   'Scottish Commissioner (minister)',
   'Letter-writing chronicler of the Assembly; later Principal of Glasgow.',
   "Glasgow professor of divinity who served as Scottish commissioner from late 1643. His private *Letters and Journals* — printed by the Bannatyne Club (1841-42) — supply more inside detail of the Assembly's business than any other surviving source. Baillie pushed the presbyterian case but with a politic moderation that often made him the Scottish delegation's chief negotiator. He became Principal of Glasgow at the Restoration but died within months.",
   overrides={'god_decree_covenant_of_redemption': 'Explicit-Developed'},
   works=['Letters and Journals (posthum. 1775; def. ed. 1841–42)',
          'A Dissuasive from the Errours of the Time (1645)'])


# ======================================================================
# III. SCOTTISH COMMISSIONERS — RULING ELDERS
# ======================================================================

_p('john-maitland-lauderdale', 'John Maitland, 2nd Earl of Lauderdale', '1616–1682',
   'Scottish Commissioner (ruling elder)',
   'Youngest elder commissioner; later notorious Restoration politician.',
   "Maitland accompanied the Scottish ministerial commissioners to Westminster in his early twenties and supported the Solemn League. His later career — as Charles II's Secretary of State for Scotland and chief instrument of the Restoration's anti-Covenanter persecutions — would be hard to predict from his Assembly days. A man of considerable learning, fluent in Greek and Hebrew, but politically pliable.",
   overrides={'god_decree_covenant_of_redemption': 'Explicit-Developed'})

_p('john-campbell-loudoun', 'John Campbell, 1st Earl of Loudoun', '1598–1662',
   'Scottish Commissioner (ruling elder)',
   'Lord Chancellor of Scotland; senior Covenanter statesman.',
   "Chief of the Campbells of Loudoun and Lord Chancellor of Scotland from 1641. Loudoun was the senior political figure on the Scottish commission to Westminster — the parliamentary counterpart to Henderson on the ministerial side. He led the Scottish commissioners to Westminster and signed the Solemn League and Covenant. He sat at the Assembly only occasionally — official duties in Edinburgh and at the king's court (in Newcastle and at the Newport negotiations) kept him much abroad — but his weight as Lord Chancellor mattered to the Anglo-Scottish coordination. After the Engagement (1647-48) and Cromwell's defeat of the Scots at Dunbar (1650) and Worcester (1651), his political fortunes declined; he was ejected from the chancellorship after the Cromwellian conquest, and lived under house arrest until the Restoration. He died at Edinburgh in 1662.",
   overrides={'god_decree_covenant_of_redemption': 'Explicit-Developed'})

_p('john-kennedy-cassillis', 'John Kennedy, 6th Earl of Cassillis', 'c. 1595–1668',
   'Scottish Commissioner (ruling elder)',
   '"The Solemn Earl"; pious Ayrshire Covenanter.',
   "Of Glasgow University, then a long career as the chief of the Kennedys of Ayrshire and one of the first nobles to sign the National Covenant in 1638. Known to contemporaries as 'the Solemn Earl' for his gravity and Reformed piety. He served as Justice General of Scotland and was one of the elder commissioners at Westminster, sitting on the Scottish General Assembly's commission almost continuously through the 1640s. He remained loyal to the strict Covenanter party throughout the 1640s and 50s, joined the Engagement reluctantly, and after Worcester withdrew to his Culzean estates. He refused public office at the Restoration in 1660 and refused the Test Act later, but survived in private life — the Kennedys remained obstinately Presbyterian through the Killing Times. He died in 1668; buried at Maybole.",
   overrides={'god_decree_covenant_of_redemption': 'Explicit-Developed'})

_p('archibald-johnston-wariston', 'Archibald Johnston of Wariston', '1611–1663',
   'Scottish Commissioner (ruling elder)',
   'Co-author of the National Covenant and Solemn League; executed at the Restoration.',
   "Edinburgh advocate who co-authored the National Covenant of 1638 with Henderson and rose to be Lord Advocate and Clerk Register. At Westminster he was the Scottish delegation's chief layman. He served Cromwell as Lord Clerk Register during the Protectorate, was attainted at the Restoration, fled to Hamburg, was kidnapped by royalist agents in Rouen in 1663, and was hanged at Edinburgh in July of that year — one of the most striking Covenanter martyrdoms.",
   overrides={'god_decree_covenant_of_redemption': 'Explicit-Developed',
              'civil_last_things_magistrate_role': 'Custos-Utriusque-Tabulae (1646)'})


# ======================================================================
# IV. ENGLISH PRESBYTERIAN MINISTERS — DRAFTING CORE
# ======================================================================

_p('edmund-calamy-elder', 'Edmund Calamy the Elder', '1600–1666',
   'English Presbyterian minister',
   '"Smectymnuus"; leader of London Presbyterians; hypothetical universalist.',
   "Calamy of Aldermanbury was one of the five Smectymnuans (1641, the Presbyterian rebuttal of Bishop Hall) and the most influential London Presbyterian of the 1640s. His January 1646 speech for hypothetical universalism in the atonement debate is the canonical Assembly statement of the Davenant position; the Confession's language was drafted to accommodate it. He was ejected in 1662 and died four years later.",
   overrides={'god_decree_extent_of_atonement': 'Hypothetical-Universal'},
   works=['Smectymnuus (1641, with Marshall, Young, Newcomen, Spurstowe)',
          "Englands Looking-Glasse (1641)"])

_p('stephen-marshall', 'Stephen Marshall', 'c. 1594–1655',
   'English Presbyterian minister',
   '"Smectymnuus"; "preacher of the long Parliament"; mediating Presbyterian.',
   "Marshall of Finchingfield was the most frequently summoned preacher of the Long Parliament — perhaps the single most prominent pulpit voice of the early 1640s English revolution. He preached *Meroz Cursed* (1641) and was Smectymnuus co-author. At the Assembly he was a moderating Presbyterian, sympathetic to the Dissenting Brethren but solid on the polity question. He died in 1655 and was buried in Westminster Abbey; his body was disinterred and dumped in a pit at the Restoration.",
   overrides={'god_decree_extent_of_atonement': 'Hypothetical-Universal'},
   works=['Smectymnuus (1641)', 'Meroz Cursed (1641)',
          'A Defence of Infant Baptisme (1646)'])

_p('edward-reynolds', 'Edward Reynolds', '1599–1676',
   'English Presbyterian minister',
   'Chief drafter of the Shorter Catechism; later Bishop of Norwich.',
   "Reynolds chaired the committee that produced the Shorter Catechism's celebrated first answer — 'Man's chief end is to glorify God, and to enjoy him forever.' Of all the Assembly's English ministers he was the most willing to conform at the Restoration, accepting consecration as Bishop of Norwich in 1661 (the only Westminster divine to take a see). He held the diocese with mildness until his death in 1676.",
   works=['A Treatise of the Passions and Faculties of the Soule (1640)',
          'The Sinfulnesse of Sinne (1639)',
          'Three Treatises (1631)'])

_p('anthony-tuckney', 'Anthony Tuckney', '1599–1670',
   'English Presbyterian minister',
   'Master of Emmanuel and St John’s; principal drafter of the Larger and Shorter Catechisms.',
   "Cambridge-trained Lincolnshire minister, Tuckney succeeded Holdsworth as Master of Emmanuel (1645) and later of St John's (1653). At the Assembly he chaired the catechetical committee that produced both Catechisms and was the working theologian behind their precision and economy. His 1651 exchange with Benjamin Whichcote — the Tuckney/Whichcote correspondence — is one of the seventeenth century's most revealing documents on the relations of Reformed orthodoxy and emergent Cambridge Platonism.",
   works=['None Such Precepts (1647)',
          'Forty Sermons Upon Several Occasions (1676)'])

_p('richard-vines', 'Richard Vines', '1600–1656',
   'English Presbyterian minister',
   'Hypothetical universalist; Master of Pembroke Cambridge.',
   "Master of Pembroke College, Cambridge from 1644. Vines was one of the leading advocates of hypothetical universalism in the Assembly's atonement debates, arguing that Christ's death was sufficient for all and intended conditionally for all though efficacious only for the elect. He pressed the Davenant reading hard against Rutherford's strict particularism. Ejected at the Restoration's purge of Cambridge.",
   overrides={'god_decree_extent_of_atonement': 'Hypothetical-Universal'},
   works=['Calebs Integrity in Following the Lord Fully (1642)',
          'Gods Drawing and Mans Coming to Christ (1662)'])

_p('lazarus-seaman', 'Lazarus Seaman', '1607–1675',
   'English Presbyterian minister',
   'Master of Peterhouse Cambridge; hypothetical universalist; the first English book auction.',
   "Of Emmanuel College Cambridge, Seaman was made Master of Peterhouse in 1644 (replacing the ejected royalist John Cosin) and was one of the most learned Hebraists in the Assembly. At Westminster he was a steady advocate of hypothetical universalism in the atonement debates — one of the principal Calamy-Davenant bloc — and a strong voice for presbyterian polity. He preached the parliamentary fast sermon Solomons Choice (1644) and contributed substantially to the Confession's chapter on Christ the Mediator. Ejected from Peterhouse in 1660 and from his London parish in 1662. His library — sold at auction by William Cooper on 31 October 1676 — produced the first printed English book-auction catalogue, a small but consequential bibliographical first that established the format of every subsequent English book auction. He died in September 1675.",
   overrides={'god_decree_extent_of_atonement': 'Hypothetical-Universal'},
   works=['The Head of the Church (1647)',
          'Solomons Choice (1644)'])

_p('william-gouge', 'William Gouge', '1575–1653',
   'English Presbyterian minister',
   'Most senior at the Assembly; *Of Domesticall Duties*; respected patriarch.',
   "Gouge of Blackfriars was the patriarch of the Assembly — already in his late 60s when it convened, with forty-five years of London ministry behind him. His *Of Domesticall Duties* (1622) was the most widely used Puritan handbook of household ethics. He chaired multiple Assembly committees, including (with Tuckney) the committee on the Confession's chapter on Christ the Mediator. He died in December 1653.",
   works=['Of Domesticall Duties (1622)',
          'A Learned and Very Useful Commentary on the Whole Epistle to the Hebrews (1655)'])

_p('john-arrowsmith', 'John Arrowsmith', '1602–1659',
   'English Presbyterian minister',
   'Master of St John’s then Trinity Cambridge; Regius Professor of Divinity; hypothetical universalist.',
   "Cambridge man through and through — Fellow of St Catharine's, then Master of St John's College from 1644 (succeeding Beale, who had been ejected) and Master of Trinity from 1653 (succeeding Thomas Hill). He held the Regius Professorship of Divinity at Cambridge from 1651. At the Assembly Arrowsmith was a vigorous Reformed scholastic of moderate hypothetical-universalist sympathies, allied with Calamy, Vines, and Seaman in the January 1646 atonement debate. His Tactica Sacra (1657) — a tightly argued Latin treatise on the conflict between the believer and indwelling sin — and the posthumously edited Armilla Catechetica or A Chain of Principles (1659) are notable Cambridge-Latin distillations of Westminster doctrine; the latter was a standard catechetical text at Cambridge into the 1680s. He died at Trinity Lodge in February 1659.",
   overrides={'god_decree_extent_of_atonement': 'Hypothetical-Universal'},
   works=['Tactica Sacra (1657)',
          'Armilla Catechetica (1659)'])

_p('thomas-hill', 'Thomas Hill', 'd. 1653',
   'English Presbyterian minister',
   'Master of Emmanuel then Trinity Cambridge; preacher of the parliamentary fast sermons.',
   "Educated at Emmanuel College Cambridge under William Bedell, Hill was named to the Assembly in 1643. Briefly Master of Emmanuel from 1645 before Tuckney succeeded him, he moved to Trinity College Cambridge in 1645 (replacing Thomas Comber) and held the lodging there until his death. He preached at least seven of the parliamentary fast sermons (1642-1648) and was a frequent Assembly speaker on procedure and on the worship debates; Six Sermons (1649) is the principal published collection. He was an active member of the catechetical committee under Tuckney. Died at Trinity Lodge in December 1653.",
   works=['The Trade of Truth Advanced (1642)',
          'The Right Separation Incouraged (1645)',
          'Six Sermons (1649)'])

_p('herbert-palmer', 'Herbert Palmer', '1601–1647',
   'English Presbyterian minister',
   'Master of Queens’ Cambridge; chair of the catechism committee.',
   "Of an Anglo-Norman gentry family (descended from Sir Thomas Palmer of Wingham, Kent), Palmer trained at St John's Cambridge and was master of Queens' from 1644 (succeeding Edward Martin, who had been ejected). He was the Assembly's most disciplined catechist — his Memorials of Godliness and Christianity (1644) had been Parliament's recommended catechism before the Westminster work began, and An Endeavour of Making the Principles of Christian Religion Plaine and Easie (1640) was a model for the Q&A format the Catechisms would adopt. As first chair of the catechetical committee he drafted its initial framework for the Larger Catechism; some scholars assign him primary drafting credit for the Shorter Catechism's structure as well. He died young in August 1647 with the Larger Catechism still six months from completion; Tuckney succeeded him in the chair.",
   works=['Memorials of Godliness and Christianity (1644)',
          'An Endeavour of Making the Principles of Christian Religion Plaine and Easie (1640)'])

_p('obadiah-sedgwick', 'Obadiah Sedgwick', 'c. 1600–1658',
   'English Presbyterian minister',
   'London preacher; chaplain to Lord Vere; strong doctrinal Calvinist.',
   "Of Magdalen Hall Oxford under William Pemble, then chaplain to Sir Horace Vere on his Dutch campaigns (a formative experience of Reformed Netherlands devotional practice). Sedgwick was rector of Coggeshall in Essex (1633) and then St Mildred Bread Street in London. At the Assembly he was one of the steadiest doctrinal Presbyterians, less polemical than Calamy but with a more popular pulpit, and a steady drafter of the Assembly's papers on doctrine. His treatises — The Doubting Believer (1641), The Anatomy of Secret Sins (posthum. 1660), The Bowels of Tender Mercy Sealed in the Everlasting Covenant (1661), and The Riches of Grace (posthum. 1657) — circulated widely as Puritan devotional reading into the eighteenth century. Died in January 1658, four years before the Great Ejection.",
   works=['The Doubting Believer (1641)',
          'The Bowels of Tender Mercy Sealed in the Everlasting Covenant (1661)'])

_p('henry-wilkinson-elder', 'Henry Wilkinson the Elder', '1566–1647',
   'English Presbyterian minister',
   'Senior Oxford divine; Lady Margaret Professor; the elder of two Wilkinsons at the Assembly.',
   "Of Magdalen Hall Oxford and (later) Christ Church, the elder Wilkinson was a long-serving rector of Waddesdon in Buckinghamshire — one of the more substantial Buckinghamshire benefices. He held the Lady Margaret Professorship of Divinity at Oxford from 1646 until his death the following year. He was one of the Assembly's senior figures — over seventy-five at its opening — and rarely spoke, but his weight as an Oxford theologian was useful symbolic capital for the parliamentary cause in the religiously divided university. His nephew Henry Wilkinson the Younger (slot above) succeeded him in the chair. He died at Oxford in March 1647 aged 81.",
   works=['Three Decads of Sermons (1660)'])

_p('henry-wilkinson-younger', 'Henry Wilkinson the Younger', '1610–1675',
   'English Presbyterian minister',
   'Canon of Christ Church Oxford; Lady Margaret Professor 1648–1662.',
   "Of Magdalen Hall Oxford and (from 1640) Christ Church, the younger Wilkinson — known to contemporaries as 'Long Harry' to distinguish him from his uncle 'Dean Harry' the elder Henry Wilkinson — held a canonry at Christ Church from 1648 and the Lady Margaret Professorship of Divinity at Oxford (1648-62) in succession to his uncle. He was active in the parliamentary reorganisation of Oxford as one of the visitors. At the Assembly he was a more vocal contributor than his uncle, working on the Confession's chapters on the moral law and the Sabbath. Ejected in 1662 for nonconformity, he ministered as a Dissenter at Buckminster (Leicestershire) and (later) Clapham, until his death in 1675.",
   works=[])

_p('george-walker', 'George Walker', '1581–1651',
   'English Presbyterian minister',
   'St John Evangelist Watling Street; doctrinal controversialist against the antinomians.',
   "Of St John's Cambridge, then nearly forty years (1614-1651) at St John Evangelist Watling Street in London. Walker was one of the most pugnacious doctrinal controversialists of his generation — he tangled with the antinomians (Tobias Crisp, John Eaton) over the imputation of righteousness in the 1620s and 30s, with the Roman Catholic Anthony Champney over the marks of the true church, with Anthony Wotton and John Goodwin over justification, and with Archbishop Laud over Sabbatarianism. Laud imprisoned him briefly in 1635 for his manuscript The Doctrine of the Sabbath (eventually printed 1641). At the Assembly he was a strong Presbyterian and a careful drafter of the chapters on justification and the law, and one of Anthony Burgess's chief allies against the antinomian wing in the mid-1640s.",
   works=['Socinianisme in the Fundamentall Point of Justification Discovered (1641)',
          'The Doctrine of the Sabbath (1641)'])

_p('thomas-gataker', 'Thomas Gataker', '1574–1654',
   'English Presbyterian minister',
   'Hebraist and classicist; editor of Marcus Aurelius; critic of judicial astrology.',
   "Of St John's College Cambridge, then preacher at Lincoln's Inn (1601-1611) before becoming rector of Rotherhithe in 1611 — a London parish he held for forty-three years until his death. Gataker was one of the most learned divines of his generation in Europe: his Marci Antonini Imperatoris De Rebus Suis (1652), the great folio edition of Marcus Aurelius's Meditations with Latin translation and notes, was used in classical scholarship into the nineteenth century; Dissertatio de Stylo Novi Instrumenti (1648) defended the literary quality of NT Greek against the Latinizing critics. At the Assembly he contributed substantially to the Westminster Annotations on the Bible (1645-47) and was the principal drafter of the chapter on lawful oaths and vows (WCF XXII). His Vindication of the Annotations (1653) against William Lilly's astrological attacks was one of the era's sharpest critiques of judicial astrology. Died at Rotherhithe in July 1654.",
   works=['Marci Antonini Imperatoris De Rebus Suis (1652)',
          'Dissertatio de Stylo Novi Instrumenti (1648)',
          'Vindication of the Annotations (1653)'])

_p('francis-cheynell', 'Francis Cheynell', '1608–1665',
   'English Presbyterian minister',
   'Anti-Socinian polemicist; parliamentary visitor of Oxford; President of St John’s briefly.',
   "Of Merton College Oxford, then Petworth (Sussex) rectory and a chaplaincy in the parliamentary army. Cheynell was the Assembly's chief anti-Socinian polemicist — The Rise, Growth, and Danger of Socinianisme (1643) was the standard English Reformed response to the rising tide of Polish-Socinian and English anti-Trinitarian literature, and his attendance at the deathbed of William Chillingworth (1644) and refusal of Christian burial to him became one of the era's most notorious sectarian incidents. Sent as a parliamentary visitor to purge Oxford in 1648, he served briefly as Lady Margaret Professor and President of St John's College Oxford (1648-1650). His abrasive, doctrinaire style made him unpopular even with allies — Anthony Wood called him 'a busy, hot-headed man' — but his Trinitarian rigour shaped WCF II.3. Ejected at the Restoration, he died in 1665.",
   works=['The Rise, Growth, and Danger of Socinianisme (1643)',
          'Chillingworthi Novissima (1644)',
          'The Divine Trinunity of the Father, Son, and Holy Spirit (1650)'])

_p('daniel-featley', 'Daniel Featley', '1582–1645',
   'English Presbyterian minister (expelled)',
   'Moderate Calvinist Episcopalian; expelled in 1643 after his royalist correspondence was intercepted.',
   "Of Corpus Christi College Oxford, then chaplain to Archbishop Abbot at Lambeth (1617-33) and rector of Lambeth and Acton. Featley was a moderate conformist Calvinist of the older school — a determined anti-Catholic controversialist (Pelagius Redivivus, 1626) and an opponent of Laudian ceremonial. He was named to the Assembly but his correspondence with Archbishop Ussher in royalist Oxford was intercepted in October 1643 (he had been passing Assembly news to the royalist camp), and he was expelled and briefly imprisoned in Lord Petre's house. Wrote The Dippers Dipt (1645) against the early English Baptists from confinement. He died in April 1645 at Chelsea, the only Assembly member formally expelled.",
   overrides={'ecclesiology_worship_polity': 'Reformed-Episcopal'},
   works=['The Dippers Dipt (1645)',
          'Pelagius Redivivus (1626)'])

_p('john-ley', 'John Ley', '1583–1662',
   'English Presbyterian minister',
   'Subdean of Chester; Westminster Annotator; mediator between Presbyterians and conformists.',
   "Of Christ Church Oxford, then Great Budworth (Cheshire) for forty years (from 1616) and subdean of Chester Cathedral. Ley contributed to the Westminster Annotations on the Bible (1645-47), the major Reformed commentary on the whole canon to come out of the Assembly years, alongside Gataker, Reynolds, and others. A moderate Presbyterian widely consulted by his peers as a careful exegete, he had been a Reformed conformist before the Civil War — held the subdeanery at Chester before being made Provost in 1645. Patternes of Piety (1640) was a catechetical handbook, A Discourse of Disputations Chiefly Concerning Matters of Religion (1658) summed up his approach to controverted theology. Died in office at Solihull in 1662, three weeks after the Act of Uniformity could have ejected him.",
   works=['Patternes of Piety (1640)',
          'A Discourse of Disputations Chiefly Concerning Matters of Religion (1658)'])

_p('thomas-young', 'Thomas Young', '1587–1655',
   'English Presbyterian minister',
   '"Smectymnuus"; Milton’s boyhood tutor; Master of Jesus College Cambridge.',
   "Scottish-born and educated at St Andrews and then at Cambridge, Young served as private tutor to the young John Milton from about 1618 to 1622 — Milton's Latin poems Elegia Quarta and Ad Thomam Iunium are addressed to him with great affection, and Young's influence is one source of Milton's later anti-prelatical politics. After ministry to the English merchants at Hamburg, Young returned to England as vicar of Stowmarket in Suffolk (1628) and remained there for the rest of his life. The 'T.Y.' of Smectymnuus (1641, the famous Presbyterian rebuttal of Bishop Hall), he had also written Dies Dominica (1639), an early defence of strict Sabbath observance. Master of Jesus College Cambridge from 1644 until he refused the Engagement in 1650 and was deprived. Died at Stowmarket in 1655.",
   overrides={'god_decree_extent_of_atonement': 'Hypothetical-Universal'},
   works=['Smectymnuus (1641)',
          'Dies Dominica (1639)'])

_p('matthew-newcomen', 'Matthew Newcomen', 'c. 1610–1669',
   'English Presbyterian minister',
   '"Smectymnuus"; Calamy’s brother-in-law; exiled to Leiden in 1662.',
   "Of St John's Cambridge under William Bedell, then vicar of Dedham (Essex) from 1636 — the famous old centre of John Rogers and Henry Smith's preaching. The 'M.N.' of Smectymnuus (1641) and the youngest of the five Smectymnuans. Newcomen married Edmund Calamy the Elder's sister and was theologically inseparable from him on most Assembly questions, sharing the hypothetical-universalist position on the atonement. He preached parliamentary fast sermons and contributed steadily to the catechetical committee. Ejected at Dedham in 1662, he retired to Leiden as minister of the English Reformed congregation there and died of plague at Leiden in September 1669.",
   overrides={'god_decree_extent_of_atonement': 'Hypothetical-Universal'},
   works=['Smectymnuus (1641)',
          'The Craft and Cruelty of the Churches Adversaries (1643)'])

_p('william-spurstowe', 'William Spurstowe', 'c. 1605–1666',
   'English Presbyterian minister',
   '"Smectymnuus"; Master of Catharine Hall; ejected twice.',
   "Of Emmanuel Cambridge, then chaplain to Lord Brooke's regiment and Hackney rectory. Master of St Catharine's Hall, Cambridge from 1645 (replacing the ejected royalist Richard Sterne). The 'W.S.' of Smectymnuus (1641) and the most modest of the five Smectymnuans — Baillie called him 'a sweet-tempered, sober man.' He served on the Westminster catechism committee and contributed steadily through the main sessions, sharing the hypothetical-universalist position on the atonement with Calamy. Ejected from the Mastership in 1650 for refusing the Engagement Oath, and ejected again from his Hackney living in 1662 under the Act of Uniformity. Died in 1666.",
   overrides={'god_decree_extent_of_atonement': 'Hypothetical-Universal'},
   works=['Smectymnuus (1641)',
          'The Wells of Salvation Opened (1655)'])

_p('joshua-hoyle', 'Joshua Hoyle', '1588–1654',
   'English Presbyterian minister',
   'Regius Professor of Divinity at Oxford; refugee from the 1641 Irish Rebellion.',
   "Educated at Magdalen Hall Oxford, then Fellow of Trinity College Dublin under James Ussher, where he taught Hebrew and divinity for nearly two decades and was a close associate of Ussher's circle. He was forced to flee Dublin during the Irish Rebellion of October 1641 and made his way to England, where he was named to the Assembly. At Westminster he was a steady speaker on the Confession's chapters on the decree and on Scripture (where Ussher's earlier influence shaped his contributions). His Rejoynder to Mr Malones Reply Concerning Reall Presence (1641) was the standard Reformed answer to Jesuit controversialists in Britain. Made Regius Professor of Divinity at Oxford from 1648, he held the chair until his death at Oxford in December 1654.",
   works=['A Rejoynder to Mr Malones Reply Concerning Reall Presence (1641)'])

_p('anthony-burgess', 'Anthony Burgess', 'd. 1664',
   'English Presbyterian minister',
   '*Vindiciae Legis* (1646); the Assembly’s great writer on the third use of the law.',
   "Of St John's Cambridge, Anthony Burgess (distinct from the Assessor Cornelius Burgess) served as Fellow of Emmanuel Cambridge in the 1630s before becoming vicar of Sutton Coldfield in Warwickshire from 1635. Burgess was the Assembly's most thorough writer on the third use of the law against the antinomian wing — Vindiciae Legis: or, A Vindication of the Morall Law and the Covenants (1646) is the canonical Reformed response to Tobias Crisp and the strongest English defence of the law's continued normative use for the regenerate. His enormous True Doctrine of Justification Asserted and Vindicated (2 vols, 1648-54) defends imputed righteousness against both Roman and antinomian readings at length. Spiritual Refining (1652-54) is his pastoral magnum opus on sanctification. Ejected at Sutton Coldfield in 1662; died in 1664.",
   works=['Vindiciae Legis (1646)',
          'The True Doctrine of Justification (1648–54)',
          'Spiritual Refining (1652)'])

_p('christopher-love', 'Christopher Love', '1618–1651',
   'English Presbyterian minister',
   'Younger Presbyterian; executed by Parliament for royalist plot, 1651.',
   "Welsh-born, of New Inn Hall Oxford. Love was one of the most popular young Presbyterian preachers in London — chaplain to John Warner before St Lawrence Jewry, and from 1645 minister of St Anne Aldersgate. At Westminster he was one of the younger active ministers and a fierce preacher against the Independents and (after 1649) the Cromwellian government. In May 1651 he was arrested for the 'Love Plot' — a Presbyterian attempt to negotiate Charles II's restoration through London merchants, with funds routed to the exiled queen — and after a long trial before the High Court of Justice was beheaded on Tower Hill on 22 August 1651 aged thirty-three: the first English minister executed by an English government since Mary's reign. His scaffold speech was widely printed; The Whole Workes (1653) and twenty subsequent posthumous editions made him a martyr-figure for the Presbyterian cause.",
   works=['The Naturall Mans Case Stated (1652)',
          "Heavens Glory, Hells Terror (1653)"])

_p('simeon-ashe', 'Simeon Ashe', 'd. 1662',
   'English Presbyterian minister',
   'Chaplain to Lord Brooke then Manchester; senior London Presbyterian.',
   "Of Emmanuel College Cambridge, then chaplain to Lord Brooke (Robert Greville, killed at the siege of Lichfield in March 1643) and after Brooke's death to Edward Montagu, Earl of Manchester through the Eastern Association campaigns. Ashe was thus an eyewitness to Marston Moor (July 1644) and reported the battle to Parliament. A senior London Presbyterian, he served at St Augustine Watling Street and was a steady moderate at the Assembly — neither a great preacher nor a controversialist, but a constant attender. He died in the very week of the Act of Uniformity in 1662 — buried two days before he would have been ejected; Calamy described him as 'one of those whom God hid in the day of trouble.'",
   works=[])

_p('thomas-wilson-maidstone', 'Thomas Wilson (of Maidstone)', '1601–1653',
   'English Presbyterian minister',
   'Vicar of Maidstone; popular Kentish Presbyterian preacher.',
   "Of Christ's College Cambridge, then vicar of Maidstone in Kent from 1631 until his death — a substantial Kent ministry through the war. Wilson was one of the more popular Kentish Presbyterian preachers and an early voice in the Long Parliament's call for thoroughgoing reformation: his fast sermon Davids Zeale for Zion (preached April 1641) urged Parliament to root-and-branch reform of episcopacy. He attended the Assembly less than the London ministers but represented the active Kent Presbyterian classis at Westminster, contributing to the catechetical committee. He died in office at Maidstone in 1653, several years before the Great Ejection.",
   works=['Davids Zeale for Zion (1641)'])

_p('edmund-staunton', 'Edmund Staunton', '1600–1671',
   'English Presbyterian minister',
   'President of Corpus Christi Oxford; one of the parliamentary visitors of Oxford.',
   "Of Wadham then Corpus Christi College Oxford, Staunton was vicar of Kingston-upon-Thames from 1632 and one of the more rigorously Calvinist Surrey ministers. He served on the parliamentary visitation of Oxford (1647-48), one of the ministers tasked with sequestering royalist heads of house, and was rewarded with the Presidency of Corpus Christi College Oxford from 1648 — a conformist-turned-Presbyterian governor of one of the most learned Oxford colleges. He preached the fast sermon Phinehas' Zeale in Execution of Iudgement (1645) before the Long Parliament. Ejected from the Presidency in 1660, he spent his last decade in pastoral retirement at Bovingdon and Rickmansworth, where he died in 1671.",
   works=['Phinehas’ Zeale in Execution of Iudgement (1645)'])

_p('robert-harris', 'Robert Harris', '1581–1658',
   'English Presbyterian minister',
   'President of Trinity College Oxford; preacher in the Dod and Cleaver circle.',
   "Of Magdalen Hall Oxford under John Rainolds, then a long pre-war ministry at Hanwell and Banbury in the Oxfordshire-Northamptonshire circle led by John Dod and Robert Cleaver — the heartland of late-Jacobean and Caroline Puritan piety. Harris was one of the most-loved Calvinist preachers of his generation; The Way to True Happinesse (1632) and a multi-volume Workes (1635) circulated widely. Made President of Trinity College Oxford from 1648 by the parliamentary visitation. Trinity's royalist fellows later recorded that Harris was a notably kind governor — gentle in enforcement, even-handed in dispute. He was the gentlest of the Oxford visitors and an unforced presence in the middle of the Presbyterian bloc at the Assembly. Died at Trinity Lodge in December 1658.",
   works=['The Way to True Happinesse (1632)',
          'Workes (1635)'])

_p('john-conant', 'John Conant', '1608–1694',
   'English Presbyterian minister',
   'Rector of Exeter College Oxford; later conformist; possibly the last surviving Westminster member.',
   "Of Exeter College Oxford under John Prideaux, then Rector of Exeter College from 1649 (after Mansell's ejection) and Regius Professor of Divinity (1654-60). He was Vice-Chancellor of Oxford 1657-60 — one of the Cromwellian Vice-Chancellors who steered the university through the Protectorate years. Joined the Assembly's later sessions in 1647 after the Confession was finished. Ejected from the Rectorship and Regius Chair in 1660 and from Exeter parish in 1662, but after the Indulgence of 1670 he gradually conformed; consecrated archdeacon of Norwich in 1676 and prebendary of Worcester from 1681. A moderate Calvinist representative of the Restoration's reconciled Reformed mainstream. Died in March 1694, aged eighty-six — quite possibly the last surviving member of the Assembly.",
   works=['Sermons (posthum. 1693)'])

_p('henry-scudder', 'Henry Scudder', 'c. 1585–c. 1652',
   'English Presbyterian minister',
   '*The Christian’s Daily Walk*; experiential Puritan devotional classic.',
   "Of Christ's College Cambridge under William Perkins's heirs, then Drayton (Wiltshire) and afterwards Collingbourne Ducis. His The Christian's Daily Walk in Security and Peace (1627) was one of the most reprinted English devotional works of the seventeenth century — practical and case-of-conscience-oriented, framed around the believer's daily duties of self-examination, repentance, prayer, and watchfulness. Owen, Baxter, and (a century later) Edwards all recommended it; Baxter cited it in his Christian Directory and Doddridge edited a later edition. Scudder married Henry Whitfield's sister (Whitfield was the founder of Guilford in Connecticut) and was uncle-in-law to William Whitaker. His quiet weight at the Assembly was that of a pastoral writer rather than a controversialist. Died around 1652 in retirement.",
   works=['The Christian’s Daily Walk in Security and Peace (1627)'])

_p('daniel-cawdrey', 'Daniel Cawdrey', '1588–1664',
   'English Presbyterian minister',
   'The Assembly’s most persistent anti-Independent polemicist; long controversy with John Owen.',
   "Of Peterhouse Cambridge, then St Martin in the Fields (London) and finally Great Billing in Northamptonshire from 1644. Cawdrey was the Assembly's most persistent polemicist against the Independents, writing against Thomas Hooker, John Cotton, and (from 1657) John Owen through the 1650s. His most consequential exchange was with Owen over the nature of schism — Cawdrey's Independencie Further Proved to be a Schism (1657-58) drew Owen's famous Review of the True Nature of Schism (1657). With Herbert Palmer he co-authored Sabbatum Redivivum (1645), one of the major Reformed treatments of the Sabbath in the seventeenth century. Ejected at Great Billing in 1662, he died two years later.",
   works=['Sabbatum Redivivum (1645, with Herbert Palmer)',
          'A Review of Mr Hookers Survey (1651)',
          'Independencie Further Proved to be a Schism (1658)'])

_p('humphrey-chambers', 'Humphrey Chambers', '1599–1662',
   'English Presbyterian minister',
   'Pewsey (Wilts) rector; chaplain to General Skippon; contributor to the Sabbath chapter.',
   "Of University College Oxford, then Pewsey (Wiltshire) rectory and (later) Claverton. Chambers was chaplain to Philip Skippon, Major-General of the New Model — a connection that placed him near the army's pulpit in the late 1640s. A steady Assembly member and one of the contributors to the work on the Sabbath chapter (WCF XXI). His Animadversions on Mr Gataker his Vindication of the Annotations (1653) intervened in the post-Assembly disputes over the Westminster Annotations. Ejected at Pewsey in 1662 under the Act of Uniformity; died the same year.",
   works=['Animadversions on Mr Gataker his Vindication of the Annotations (1653)'])

_p('francis-taylor', 'Francis Taylor', '1589–1656',
   'English Presbyterian minister',
   'Hebraist; Master of Jesus College Cambridge; Westminster Annotator on Proverbs.',
   "Of Queens' College Cambridge, then Yalding (Kent) for forty years from the early 1620s. Taylor was the Assembly's specialist in rabbinical-Hebrew sources, contributing the annotations on Proverbs and parts of the historical books to the Westminster Annotations on the Bible (1645-47). He published Targum Prius et Posterius in Estheram (1655) — a critical edition of the two Targumim on Esther with Latin translation — and a Commentary on the First Three Chapters of the Proverbs (1655). Made Master of Jesus College Cambridge in 1652 after Thomas Young's deprivation for refusing the Engagement Oath. Died at Cambridge in 1656.",
   works=['Selfe-Satisfaction Examined (1646)',
          'Targum Prius et Posterius in Estheram (1655)',
          'A Commentary on the First Three Chapters of the Proverbs (1655)'])

_p('jeremiah-whitaker', 'Jeremiah Whitaker', '1599–1654',
   'English Presbyterian minister',
   'Stretton then Bermondsey; frequent committee chair at Westminster.',
   "Of Sidney Sussex Cambridge — the most Puritan of the Cambridge colleges — then schoolmaster at Oakham and from 1624 rector of Stretton in Rutland. From 1644 he was promoted to St Mary Magdalen Bermondsey in London. A hard-working committee chair at the Assembly — the manuscript minutes show him moderating sessions through long stretches — Whitaker was respected for his careful procedural sense and pastoral gravity. His pastoral preaching style was much admired; his fast sermons The Christians Hope Triumphing (1645) and Eirenopoios (1645) ran through several editions. Died in office at Bermondsey in June 1654.",
   works=['Eirenopoios (1645)',
          'The Christians Hope Triumphing (1645)'])

_p('francis-roberts', 'Francis Roberts', '1609–1675',
   'English Presbyterian minister',
   'Rector of Wrington; the great Westminster covenant theologian.',
   "Of Trinity College Oxford, then rector of Cheshunt and (from 1650) Wrington in Somerset, where he stayed until his death. Roberts was the younger generation's covenant theologian — his Mysterium et Medulla Bibliorum: The Mysterie and Marrow of the Bible, Viz. Gods Covenants with Man (1657) is one of the largest Reformed treatments of the covenant theology of the Old and New Testaments in any language, running to over 1,700 folio pages. It works out the Westminster covenant scheme into a systematic theology that influenced Cocceius and Witsius on the Continent and provided much of the structural backbone for later British covenant divinity (Boston, the Marrow men). He survived the Restoration in his parish, conformed in 1662, and died at Wrington in 1675.",
   works=['Mysterium et Medulla Bibliorum (1657)'])

_p('john-wincop', 'John Wincop', 'd. 1647',
   'English Presbyterian minister',
   'Rector of Ellesworth; chaplain to the Earl of Holland.',
   "Of Christ's College Cambridge, then Ellesworth in Cambridgeshire and chaplain to Henry Rich, 1st Earl of Holland (one of the wavering Court peers who returned to the king's side late in the war). Wincop served on the catechetical committee from its earliest sessions and was a quiet but steady contributor through the main sessions. He preached the parliamentary fast sermon Israels Preservation (1645). Died in October 1647 before the Catechisms' final approval.",
   works=['Israels Preservation (1645)'])

_p('andrew-perne', 'Andrew Perne', '1596–1654',
   'English Presbyterian minister',
   'Wilby (Northants); steady member of the catechism committee.',
   "Of Catharine Hall Cambridge, then Wilby in Northamptonshire — one of the more substantial Northamptonshire benefices, in a county thick with Puritan ministers. A working member of the catechism committee and the chapter committee on the Lord's Supper, Perne was a steady but unobtrusive Presbyterian voice in the East Midlands cohort. He preached the parliamentary fast sermon Gospell Courage (1643). Died at Wilby in 1654.",
   works=['Gospell Courage (1643)'])

_p('william-carter-elder', 'William Carter the Elder', 'd. c. 1658',
   'English Presbyterian minister',
   'London lecturer; senior moderate.',
   "Carter of St Lawrence Jewry was a moderate London Presbyterian, distinct from his Independent namesake (Carter of Yarmouth). He died around 1658.",
   works=[])

_p('thomas-bayley', 'Thomas Bayley', 'd. c. 1657',
   'English Presbyterian minister',
   'Manningtree rector; minor active member.',
   "Bayley was rector of Manningtree, Essex. A steady attender of the Assembly's sessions but left little independent record.",
   works=[])

_p('john-langley', 'John Langley', 'c. 1593–1657',
   'English Presbyterian minister',
   'Hampshire and Gloucestershire minister; High Master of St Paul’s School.',
   "Of Magdalen Hall Oxford, Langley served at West Tuderley in Hampshire and as High Master of St Paul's School in London (1640-57) — the most prestigious schoolmastership in seventeenth-century England. From St Paul's he prepared generations of younger Reformed-trained boys who went on to Cambridge and Oxford. A quietly diligent Assembly attender; his name survives chiefly in the Assembly's manuscript division-lists. Died at St Paul's School in 1657.",
   works=[])

_p('john-bond', 'John Bond', '1612–1676',
   'English Presbyterian minister',
   'Master of Trinity Hall Cambridge; preacher of parliamentary fast sermons.',
   "Of St Catharine's Hall Cambridge under Richard Sibbes, then preacher at Exeter and (from 1645) Master of Trinity Hall, Cambridge. Bond was a younger Presbyterian, made Master of the Savoy in London (1646) and Professor of Law at Gresham College (1649). He preached fast sermons before the Long Parliament (Salvation in a Mystery, 1644; A Sermon Preached in Exon, 1643) and contributed to the catechetical work. Ejected from Trinity Hall at the Restoration in 1660 and from the Savoy in 1662; died in 1676.",
   works=['A Sermon Preached in Exon (1643)',
          'Salvation in a Mystery (1644)'])

_p('john-greene', 'John Greene', 'd. 1644',
   'English Presbyterian minister',
   'Pencombe rector; died during the Assembly.',
   "Rector of Pencombe, Herefordshire; a quiet Assembly member who died during the Assembly's sittings in 1644.",
   works=[])

_p('william-bridges', 'William Bridges', '1600–1670',
   'English Presbyterian minister',
   'Senior London preacher (not to be confused with William Bridge, Independent).',
   "London preacher whose name is sometimes confused in the records with the Independent William Bridge. A moderate Presbyterian and friend of Calamy.",
   works=[])

_p('humphrey-hardwick', 'Humphrey Hardwick', 'd. c. 1660',
   'English Presbyterian minister',
   'Hadham rector; Assembly attender.',
   "Rector of Hadham, Hertfordshire. A steady but quiet Assembly member.",
   works=[])

_p('john-foxcroft', 'John Foxcroft', 'd. 1658',
   'English Presbyterian minister',
   'Gotham rector.',
   "Rector of Gotham, Nottinghamshire. A regular Assembly attender from 1643 and a member of one of the catechism subcommittees.",
   works=[])

_p('peter-smith', 'Peter Smith', 'd. c. 1653',
   'English Presbyterian minister',
   'Barkway rector.',
   "Rector of Barkway, Hertfordshire. A working Assembly member known chiefly through the manuscript minutes.",
   works=[])

_p('john-philips', 'John Philips', 'd. 1660',
   'English Presbyterian minister',
   'Wrentham rector.',
   "Rector of Wrentham, Suffolk. A steady Assembly attender.",
   works=[])

_p('john-arrowsmith-cambridge', 'John Arrowsmith of Cambridge', 'd. 1652',
   'English Presbyterian minister',
   'Distinct from John Arrowsmith the Master — minor member.',
   "A minor Assembly member from Cambridge, occasionally confused with John Arrowsmith of Trinity in the records.",
   works=[])

_p('thomas-temple', 'Thomas Temple', '1567–1661',
   'English Presbyterian minister',
   'Vicar of Battersea; one of the senior members; lived to 94.',
   "Of Lincoln College Oxford, then Battersea vicarage from 1634 — coming to it in his late sixties from a career in Buckinghamshire and Northamptonshire ministries. Temple was an elderly Presbyterian at the Assembly's opening — seventy-six in 1643, the second-oldest active member after William Gouge — and his contributions were minor but loyal. He was ejected at Battersea in 1660 and died the following year in retirement, aged ninety-four — likely the longest-lived active Assembly member.",
   works=[])

_p('john-strickland', 'John Strickland', 'c. 1601–1670',
   'English Presbyterian minister',
   'Salisbury preacher; preached parliamentary fast sermons.',
   "Of Queen's College Oxford, then Burton-on-Trent and (from 1638) New Sarum (Salisbury) where he was a senior cathedral lecturer through the war. Strickland preached fast sermons before the Long Parliament in 1644 and 1645 (Mercy Rejoycing Against Judgement, 1645) and was a steady Presbyterian voice in the catechetical committee. He was ejected at the Restoration from his Salisbury lectureship and again in 1662 under the Act of Uniformity. Died in 1670.",
   works=['Mercy Rejoycing Against Judgement (1645)'])

_p('william-price', 'William Price', 'c. 1597–1666',
   'English Presbyterian minister',
   'Welsh Presbyterian; English Reformed pastor in Amsterdam.',
   "Welsh-born and Oxford-trained, Price was minister of the English Reformed Church in Amsterdam from 1641 — the major Reformed exile congregation in the Netherlands — while also being named to the Westminster Assembly. His position straddled two ministries: he attended Assembly sessions during English visits but spent most of his time at the Begijnhofkerk in Amsterdam, which he held until his death in 1666. He was a steady moderate Presbyterian voice and one of the few Welsh-born Assembly members.",
   works=[])

_p('francis-woodcock', 'Francis Woodcock', 'd. 1651',
   'English Presbyterian minister',
   'St Olave Jewry and Christ Church Newgate; regular preacher of parliamentary fast sermons.',
   "Of Brasenose Oxford, then lecturer at St Christopher le Stocks and (from 1644) St Olave Jewry and Christ Church Newgate, London. Woodcock was a steady London Presbyterian voice in the catechetical committee and a regular preacher of parliamentary fast sermons in the mid-1640s — Christ's Warning-Piece (1644) and Lex Talionis (1646) were the best known of more than a dozen sermons preached before either House. A second-tier London Presbyterian active on multiple committees through the main sessions. Died in office around 1651.",
   works=['Christ’s Warning-Piece (1644)',
          'Lex Talionis (1646)'])

_p('thomas-case', 'Thomas Case', '1598–1682',
   'English Presbyterian minister',
   'Popular London preacher; Love plotter; ejected at the Restoration.',
   "Of Christ Church Oxford, then a long London ministry — first at St Mary Magdalen, Milk Street (from 1641) and then at St Giles in the Fields. Case was one of the most popular London Presbyterian preachers of the 1640s and 50s; his fast-day sermons before Parliament were widely reprinted. He preached the funeral sermon for Christopher Love in 1651 and was himself implicated in the Love plot — arrested, brought before the Council of State, and held in the Tower for eight months before being released without trial. Continued to preach until ejected in 1662 under the Act of Uniformity; thereafter held a private congregation in Hackney until his death in 1682, having lived through the entire Restoration period as a leading London Dissenter.",
   works=['Mount Pisgah (1670)',
          'Correction, Instruction (1652)'])

_p('thomas-thoroughgood', 'Thomas Thoroughgood', 'c. 1595–1669',
   'English Presbyterian minister',
   'Norfolk minister; *Iewes in America*, the Lost-Tribes thesis on Native American descent.',
   "Of Christ's College Cambridge, then rector of Great Massingham in Norfolk, where he spent his whole ministerial career. His Iewes in America: or, Probabilities that those Indians are Iudaical (1650, expanded second edition 1660) argued that the indigenous peoples of America descended from the Lost Tribes of Israel — a position with significant millennial-Israel resonance in Anglo-Reformed eschatology. The work was widely discussed by both English and New England theologians: John Eliot, the Apostle to the Indians, prefaced the second edition; Cotton Mather and Increase Mather both engaged it; and it shaped the Mathers' continuing expectation of Israel's restoration. Thoroughgood attended the Assembly intermittently, was ejected in 1662, and died in 1669.",
   works=['Iewes in America (1650)'])

_p('john-jackson', 'John Jackson', 'c. 1600–1648',
   'English Presbyterian minister',
   'Marsk rector.',
   "Vicar of Marske in Cleveland. A regular Assembly member who died in 1648.",
   works=[])

_p('peter-clarke', 'Peter Clarke', 'd. 1665',
   'English Presbyterian minister',
   'Carnaby rector.',
   "Rector of Carnaby, Yorkshire. Ejected in 1662, he conformed for a time after the Indulgence.",
   works=[])

_p('thomas-ford', 'Thomas Ford', '1598–1674',
   'English Presbyterian minister',
   'Exeter Cathedral; expositor of the Decalogue.',
   "Of Magdalen Hall Oxford, then Exeter Cathedral lecturer and (after the war) one of the assistant ministers at St Mary Aldermanbury in London under Calamy. Ford was a respected expositor of the Decalogue — his unpublished Exeter sermons survived in eighteenth-century editions — and a steady Presbyterian at the Assembly through the main sessions. Returned to Exeter in 1651 to serve at St Mary Major. Ejected in 1662 under the Act of Uniformity but continued to preach privately in the city. Died at Exeter in 1674.",
   works=[])

_p('william-rathband', 'William Rathband', 'd. 1641 (named posthumously?)',
   'English Presbyterian minister',
   'Named in early lists; replaced.',
   "Newcastle-area minister whose presence at the actual Assembly sessions was minimal; his name appears in the original 1643 ordinance but he died shortly after.",
   works=[])

_p('john-maynard-mayfield', 'John Maynard (of Mayfield)', '1600–1665',
   'English Presbyterian minister',
   'Sussex preacher; member of the committee on baptism.',
   "Of Magdalen Hall Oxford under William Pemble, then Mayfield in Sussex from 1623 — a forty-year ministry in one of the more substantial East Sussex livings. Distinct from the parliamentary lawyer John Maynard. A regular Assembly attender and a member of the committee on baptism, he preached the parliamentary fast sermon A Sermon Preached before the Honourable House of Commons (1646). Ejected from Mayfield in 1662 under the Act of Uniformity; died in 1665.",
   works=['The Beauty and Order of the Creation (1668)',
          'A Sermon Preached before the Honourable House of Commons (1646)'])

_p('john-de-la-march', 'John de la March', 'd. 1650s',
   'English Presbyterian minister',
   'Channel Islands minister; French-language preacher.',
   "Channel Islands French-language Reformed minister. Represented the Channel Islands churches at Westminster.",
   works=[])

_p('philip-delme', 'Philip Delmé', 'c. 1593–c. 1654',
   'English Presbyterian minister',
   'French Reformed Church of London; Huguenot pastor.',
   "Of Genevan and Leiden training, Delmé was pastor of the French Reformed (Huguenot) congregation at Threadneedle Street in London — the stranger church that had been authorised by Edward VI's 1550 charter and that linked English Reformed practice to the wider French Reformed world. His Assembly presence was sporadic but symbolically significant: the inclusion of a French Reformed pastor signalled the Assembly's continental Reformed sympathies and its commitment to the wider Protestant union of the Solemn League period. He voted with the Presbyterian mainstream. Died around 1654.",
   works=[])

_p('george-walker-bansted', 'George Walker (of Banstead)', 'd. c. 1657',
   'English Presbyterian minister',
   'Distinct from George Walker of St John the Evangelist; minor.',
   "A minor Surrey minister occasionally confused with the better-known London Walker.",
   works=[])

_p('john-gibbon', 'John Gibbon', 'd. c. 1660',
   'English Presbyterian minister',
   'Waltham rector; minor member.',
   "Rector of Waltham St Lawrence, Berkshire. A regular Assembly attender.",
   works=[])

_p('william-mew', 'William Mew', 'c. 1602–1669',
   'English Presbyterian minister',
   'Eastington (Gloucestershire); mechanical inventor noted by Aubrey.',
   "Of Magdalen Hall Oxford, then Eastington in Gloucestershire (succeeding Capel) and later Cromhall. Mew was a country Presbyterian whose Assembly contribution was steady but unobtrusive — but John Aubrey, who knew him in Gloucestershire, remembered him in Brief Lives as much for his ingenious mechanical inventions (a calculating organ, a 'perpetual-motion' mill, geometrical instruments) as for his ecclesiastical career. Mew was a small example of the Hartlib circle's broad reach — the Puritan polymath-minister of the parish workshop. Ejected in 1662; died in 1669.",
   works=[])

_p('richard-capel', 'Richard Capel', '1586–1656',
   'English Presbyterian minister',
   'Gloucestershire Puritan; *Tentations* (1633), the canonical Puritan handbook on temptation.',
   "Of St Alban Hall Oxford, then Eastington and Pitchcombe (Gloucestershire). Capel had been deprived of his Oxford fellowship for refusing the 1604 Subscription, then served as a Gloucestershire country minister for forty years. His Tentations: Their Nature, Danger, Cure (1633) was the standard Puritan treatment of the locus — a casuistical handbook on the nature, danger, and cure of spiritual temptation — and shaped Owen's later treatise. He attended the Westminster Assembly when his health permitted but was already in his late fifties when it opened. Died at Pitchcombe in 1656.",
   works=['Tentations: Their Nature, Danger, Cure (1633)'])


# ======================================================================
# V. THE DISSENTING BRETHREN & OTHER INDEPENDENTS
# ======================================================================

_p('thomas-goodwin', 'Thomas Goodwin', '1600–1680',
   'Independent / Dissenting Brother',
   'Chief Independent theologian; later President of Magdalen Oxford.',
   "Goodwin was the most learned of the Five Dissenting Brethren and the chief intellectual architect of Independent ecclesiology. President of Magdalen College Oxford under the Protectorate (1650-1660). His massive posthumous *Works* (12 vols, 1681-1704) is the great Independent dogmatic system — strongly supralapsarian, with a developed covenant of redemption and an experimental soteriology shaped by Sibbes. Ejected in 1660, he lived in retirement in London until 1680.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational',
              'god_decree_order_of_decrees': 'Supralapsarian',
              'god_decree_covenant_of_redemption': 'Explicit-Developed'},
   works=['An Apologeticall Narration (1644, with Nye, Burroughs, Bridge, Simpson)',
          'A Childe of Light Walking in Darknesse (1636)',
          'Of the Object and Acts of Justifying Faith (posthum. 1697)',
          'Works (12 vols, 1681–1704)'])

_p('philip-nye', 'Philip Nye', '1595–1672',
   'Independent / Dissenting Brother',
   'Politically the most astute Independent; chaplain to the Long Parliament.',
   "Of Brasenose Oxford, then St Michael Cornhill until forced into exile in Arnhem (1633-40) at the Dutch Reformed Independent congregation alongside Goodwin, Bridge, and Simpson. Returning to England in 1640, he became one of the inner circle of parliamentary chaplains and the political tactician of the Dissenting Brethren — quicker and politically sharper than Goodwin, the one who handled negotiations with Parliament and Cromwell. He drafted the 'Reasons against Presbyterian Government' that the Brethren laid before the Assembly and conducted most of the open-floor argument against jure-divino presbyterianism. With Stephen Marshall he tendered the Solemn League and Covenant to the Commons in September 1643. He chaired the Savoy Conference of 1658 that produced the Savoy Declaration — the Independent recension of Westminster. Ejected at the Restoration, he ministered to a private Independent congregation in London until his death in September 1672.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=['An Apologeticall Narration (1644)',
          'The Lawfulnesse of the Oath of Supremacy (1683, posthum.)'])

_p('jeremiah-burroughs', 'Jeremiah Burroughs', '1599–1646',
   'Independent / Dissenting Brother',
   '*The Rare Jewel of Christian Contentment*; pastoral Independent.',
   "Burroughs was the most pastoral and conciliatory of the Dissenting Brethren — Calamy said of him that 'if all Independents had been like Mr Burroughs, and all Presbyterians like Mr Marshall, the divisions of the Church might soon have been healed.' His posthumously published *Gospel-Worship* (1648) and *The Rare Jewel of Christian Contentment* (1648) are devotional classics. He died young in November 1646 after a fall from his horse.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=['An Apologeticall Narration (1644)',
          'Gospel-Worship (1648)',
          'The Rare Jewel of Christian Contentment (1648)',
          'Irenicum, to the Lovers of Truth and Peace (1646)'])

_p('william-bridge', 'William Bridge', '1600–1671',
   'Independent / Dissenting Brother',
   'Yarmouth Independent; *A Lifting Up for the Downcast*.',
   "Of Emmanuel Cambridge, then Colchester ministry until Laud's persecutions drove him into exile in Rotterdam (1636-1641) — where he was co-pastor with Sidrach Simpson at the English Reformed Independent congregation. He returned to England in 1641 and was settled at Great Yarmouth from 1643, where he led the East Anglian Independent cause for almost thirty years. A Lifting Up for the Downcast (1648) — a series of sermons preached to spiritually depressed believers in the dark years of the Civil War — is his pastoral classic and one of the most affecting Puritan devotional works of the seventeenth century. A signatory of the Apologeticall Narration (1644). Ejected from Yarmouth in 1662, he ministered to a private congregation there until his death in 1671.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=['An Apologeticall Narration (1644)',
          'A Lifting Up for the Downcast (1648)',
          'The Saints Hiding-Place (1646)'])

_p('sidrach-simpson', 'Sidrach Simpson', 'c. 1600–1655',
   'Independent / Dissenting Brother',
   'Master of Pembroke College Cambridge; sharpest Independent polemicist.',
   "Of Queens' College Cambridge, then St Mary Wolnoth in London until Laud's pressure drove him into exile in Rotterdam in 1638 (with Goodwin and Nye, where they formed the gathered Independent congregation that returned to England together in 1641). He served at St Mary Abchurch London, then (from 1650) Master of Pembroke College Cambridge. Of the Five Dissenting Brethren who signed the Apologeticall Narration, Simpson was the most polemical against the Presbyterian majority — his Reformation's Preservation (1643) had argued the gathered-church position in print before the Assembly was even called. Died at Pembroke Lodge in 1655.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=['An Apologeticall Narration (1644)',
          'Reformation’s Preservation (1643)'])

_p('william-greenhill', 'William Greenhill', '1591–1671',
   'Independent minister',
   'Stepney; expositor of Ezekiel; co-pastor with Jeremiah Burroughs.',
   "Of Magdalen College Oxford, then a vicarage at New Shoreham (Sussex) before moving to Stepney in 1641, where he was lecturer and (from 1644) co-pastor with Jeremiah Burroughs of one of the most important London Independent congregations. After Burroughs's death in 1646 he continued as pastor at Stepney. Greenhill attended the Assembly but was less prominent than the Five Dissenting Brethren in print; his five-volume Exposition of the Prophet Ezekiel (1645-1662) was the major Puritan commentary on Ezekiel, more than 2,000 pages in its final extent. He was tutor to King Charles I's younger children Henry and Elizabeth in the late 1640s after Northumberland was given their guardianship. Ejected at the Restoration in 1660 from his St Dunstan's Stepney lectureship, he continued at the gathered church until his death in 1671.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=['An Exposition of the Prophet Ezekiel (5 vols, 1645–1662)'])

_p('joseph-caryl', 'Joseph Caryl', '1602–1673',
   'Independent minister',
   'Twenty-four-year Exposition of Job (12 vols); senior Independent.',
   "Of Exeter College Oxford, then preacher at Lincoln's Inn (1631) and rector of St Magnus the Martyr at London Bridge from 1645. Caryl spent nearly twenty-four years preaching through the book of Job at St Magnus; the resulting An Exposition with Practicall Observations upon the Booke of Iob (12 quarto volumes, 1643-1666) is the longest sustained Puritan commentary on a single book of Scripture, perhaps 4 million words. He was a Westminster member with Independent sympathies and served as a parliamentary commissioner at the Uxbridge treaty (1645) and again at Newport (1648). Cromwell sent him with John Owen to Scotland as parliamentary chaplain in 1650-51. Ejected at the Restoration, he led a gathered Independent congregation in London which, after his death in 1673, was inherited by John Owen.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=['An Exposition with Practicall Observations upon the Booke of Iob (12 vols, 1643–1666)'])

_p('william-carter-yarmouth', 'William Carter (of Yarmouth)', 'd. 1658',
   'Independent minister',
   'Lambeth lecturer then Yarmouth Independent; distinct from Carter of St Lawrence Jewry.',
   "Lecturer at Lambeth and one of the Independents at the Westminster Assembly, distinct from the elder Presbyterian Carter of St Lawrence Jewry. Carter was not one of the five signatories of An Apologeticall Narration (Goodwin, Nye, Bridge, Burroughs, Simpson) but voted consistently with the Independent bloc on polity questions. After the Assembly he was settled with William Bridge at Great Yarmouth as co-pastor of the Independent gathered church there. Died in 1658.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=[])

_p('peter-sterry', 'Peter Sterry', '1613–1672',
   'Independent minister',
   'Platonist Independent; chaplain to Lord Brooke and to Cromwell.',
   "Of Emmanuel College Cambridge, the most Platonist of the Assembly's voices and a member of the same generation as Henry More and Ralph Cudworth. He was chaplain to Lord Brooke until Brooke's death at Lichfield in 1643, then to the Earl of Manchester, and finally one of Cromwell's chosen Whitehall chaplains through the Protectorate (1654-58). At Westminster his attendance was intermittent, but he signed Independent papers. Sterry's Independent ecclesiology was joined to a mystical-Platonist soteriology that distinguished him sharply from the sober Goodwin-Nye-Bridge wing — A Discourse of the Freedom of the Will (1675, posthum.) and The Rise, Race, and Royalty of the Kingdome of God in the Soul of Man (1683, posthum.) read closer to Cudworth and More than to Owen, and were thought by some contemporaries to verge on universalism. Died in retirement at Hackney in 1672.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=['The Spirits Conviction of Sinne (1645)',
          'A Discourse of the Freedom of the Will (1675, posthum.)'])

_p('john-phillip', 'John Phillip', 'd. 1660',
   'Independent minister',
   'Wrentham co-pastor with Bridge.',
   "Co-pastor with William Bridge at Wrentham, Suffolk. A working Assembly member of Independent sympathies.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=[])


# ======================================================================
# VI. THE ERASTIANS
# ======================================================================

_p('john-lightfoot', 'John Lightfoot', '1602–1675',
   'Erastian minister',
   'Master of Catharine Hall; great Christian Hebraist.',
   "Master of St Catharine's Hall, Cambridge (1650-1675) after Spurstowe. Lightfoot was the most learned Hebraist and rabbinic scholar of his generation in England — his *Horae Hebraicae et Talmudicae* (1658-1674) put rabbinic literature to work in NT exegesis on a scale not seen before. At the Assembly he was an Erastian on polity, arguing alongside Coleman and Selden that ultimate church authority belongs to the magistrate. His *Journal of the Westminster Assembly* (manuscript, printed 1824) is one of the best surviving accounts.",
   overrides={'ecclesiology_worship_polity': 'Erastian',
              'civil_last_things_magistrate_role': 'Erastian-Magistrate-Over-Church'},
   works=['Erubhin (1629)',
          'A Few and New Observations upon the Booke of Genesis (1642)',
          'Horae Hebraicae et Talmudicae (1658–1674)',
          'A Journal of the Westminster Assembly (manuscript)'])

_p('thomas-coleman', 'Thomas Coleman', '1598–1646',
   'Erastian minister',
   '"Rabbi Coleman"; Hebraist co-leader of the Erastian wing; died mid-debate.',
   "Of Magdalen Hall Oxford, then Lincolnshire ministries — Blyton, Lincoln, and finally St Peter Cornhill in London from 1645. Called 'Rabbi Coleman' by contemporaries for his Hebrew learning, Coleman was the principal ministerial Erastian at the Assembly alongside John Lightfoot, and the most direct opponent of Gillespie's jure-divino case. He preached the famous Erastian sermon before the House of Commons on 30 July 1645 (Hopes Deferred and Dashed, published as A Brotherly Examination Re-examined) advocating civil supremacy in ecclesiastical jurisdiction — drawing Gillespie's Aaron's Rod Blossoming (1646) in devastating reply. He died on 30 March 1646, mid-debate, two months before the Confession's final approval — leaving Lightfoot as the sole ministerial Erastian voice.",
   overrides={'ecclesiology_worship_polity': 'Erastian',
              'civil_last_things_magistrate_role': 'Erastian-Magistrate-Over-Church'},
   works=['A Brotherly Examination Re-examined (1645)'])


# ======================================================================
# VII. LAY ASSESSORS — COMMONS
# ======================================================================

_p('john-selden', 'John Selden', '1584–1654',
   'Lay Assessor (Commons)',
   'England’s greatest jurist; Erastian; *History of Tithes*.',
   "Selden was the most learned jurist in Europe, author of *History of Tithes* (1618, suppressed), *Mare Clausum* (1635), *De Synedriis* (1650-55), and the polymathic *Table-Talk* (posthum. 1689). At the Assembly he was the Erastians' chief voice and the divines' most formidable adversary — Whitelocke recorded his speech that 'perpetual succession of bishops, presbyters, and deacons' was no more in the Bible than 'perpetual succession of Lord Mayors of London.' His exchanges with Gillespie are Westminster legend.",
   overrides={'ecclesiology_worship_polity': 'Erastian',
              'civil_last_things_magistrate_role': 'Erastian-Magistrate-Over-Church'},
   works=['History of Tithes (1618)',
          'Mare Clausum (1635)',
          'De Synedriis (3 vols, 1650–1655)',
          'Table-Talk (posthum. 1689)'])

_p('bulstrode-whitelocke', 'Bulstrode Whitelocke', '1605–1675',
   'Lay Assessor (Commons)',
   'Memorialist; Commissioner of the Great Seal; ambassador to Sweden.',
   "Of St John's Oxford and the Middle Temple, Whitelocke was MP for Marlow and one of the most active parliamentary lay assessors at the Assembly. He served as Commissioner of the Great Seal from 1648 and on numerous embassies, including the famous mission to Queen Christina of Sweden (1653-54) recorded in his Journal of the Swedish Embassy. His Memorials of the English Affairs from the Beginning of the Reign of King Charles the First to King Charles the Second His Happy Restauration (1682) remains the indispensable lawyer's-eye chronicle of the period — the source for many famous quotations from the Assembly debates, including Selden's most cutting interventions. He sympathised with the Erastians on polity but on most other questions was a moderate. Refused to sit in judgement on the king. Withdrew from public life at the Restoration. Died in 1675.",
   overrides={'ecclesiology_worship_polity': 'Erastian'},
   works=['Memorials of the English Affairs (1682)',
          'Journal of the Swedish Embassy (1772)'])

_p('john-pym', 'John Pym', '1584–1643',
   'Lay Assessor (Commons)',
   '"King Pym"; the chief parliamentary architect of the Long Parliament’s drive against Charles I.',
   "Of Broadgates Hall Oxford (where Charles I would later try to take refuge) and the Middle Temple. Pym was the principal parliamentary tactician of the long Parliament's first three years — manager of Strafford's impeachment, drafter of the Grand Remonstrance (1641), one of the Five Members Charles I tried to arrest on 4 January 1642 in the act that triggered the king's flight from London. Contemporaries called him 'King Pym' for the closeness of his management of the Commons. He engineered the parliamentary ordinance that created the Westminster Assembly (June 1643), and he negotiated the Solemn League and Covenant with the Scots that brought their army into the war. He died of bowel cancer on 8 December 1643, five months after the Assembly opened — buried in Westminster Abbey; disinterred and dumped in a common pit at the Restoration.",
   works=['Speeches (collected later)'])

_p('henry-vane-younger', 'Sir Henry Vane the Younger', '1613–1662',
   'Lay Assessor (Commons)',
   'Governor of Massachusetts at 23; negotiator of the Solemn League; executed in 1662.',
   "Of Magdalen Hall Oxford. The younger Vane went to New England in 1635, was elected Governor of Massachusetts in May 1636 at age twenty-three, and immediately collided with John Winthrop over Anne Hutchinson and the Antinomian Crisis — Vane defending Hutchinson, Winthrop sentencing her. He returned to England in 1637 and rose rapidly: Treasurer of the Navy (1639), MP for Hull. With Henderson and Wariston he negotiated the Solemn League and Covenant in Edinburgh in 1643 — the alliance that brought Scotland into the war. He was one of the Independent managers in the Commons through the 1640s and a leading figure of the Commonwealth's foreign and naval policy. He opposed Cromwell's Protectorate from Republican principles (his Healing Question, 1656, was the most articulate Republican manifesto of the decade) and was imprisoned by Cromwell. At the Restoration he was excepted from indemnity, tried for high treason on the spurious charge of compassing the king's death, and beheaded on Tower Hill on 14 June 1662, despite Charles II's earlier promise of his life. His scaffold speech was suppressed by drums.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=['The Retired Mans Meditations (1655)',
          'A Healing Question (1656)'])

_p('oliver-st-john', 'Oliver St John', 'c. 1598–1673',
   'Lay Assessor (Commons)',
   'Solicitor General; Hampden’s counsel in the Ship Money case; Chief Justice under the Protectorate.',
   "Of Queens' Cambridge and Lincoln's Inn, St John was Cromwell's cousin by marriage and one of Pym's closest collaborators in the early Long Parliament. He had been Hampden's counsel in the Ship Money case of 1637-38, and his speech against Strafford in 1641 carried much of the procedural argument for the attainder. As Solicitor General (1641-1643) and Chief Justice of the Common Pleas under the Protectorate (1648-1660) he was the senior parliamentary lawyer of the era; a moderate Independent in church matters. Refused to sit in judgement on Charles I but did not protest publicly. At the Restoration he was barred from office; he fled to Augsburg and Basel, dying in exile in 1673.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'})

_p('nathaniel-fiennes', 'Nathaniel Fiennes', '1608–1669',
   'Lay Assessor (Commons)',
   'Son of Lord Saye and Sele; surrendered Bristol to Rupert in 1643.',
   "Second son of Viscount Saye and Sele; of New College Oxford and Lincoln's Inn. As Colonel and Governor of Bristol, Fiennes surrendered the city to Prince Rupert on 26 July 1643 after a brief siege — a controversial capitulation for which he was court-martialled and sentenced to death by the Earl of Essex, though the sentence was set aside on appeal. He sat as a lay assessor at the Assembly through the rest of the 1640s, sympathising with the Independents like his father, and served Cromwell as Lord Keeper of the Great Seal (1655-1659). He retired at the Restoration and died in 1669.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'})

_p('francis-rouse', 'Francis Rouse', '1579–1659',
   'Lay Assessor (Commons)',
   'Provost of Eton; metrical psalmist; Speaker of Barebones Parliament.',
   "Of Broadgates Hall Oxford and the Middle Temple, then a long parliamentary career and the Provostship of Eton (1644-1659). Rouse's Booke of Psalmes in English Meter (1643, revised by the Westminster Assembly 1646 and approved in Scotland 1650) became the basis of the Scottish Metrical Psalter — sung continuously in Reformed Scottish congregations to the present. He was Speaker of Barebones Parliament (1653) and a member of Cromwell's Other House. A devout moderate Independent, he wrote mystical-experimental devotional works (The Mysticall Marriage, 1631) before his political career. Died at Eton in January 1659.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=['The Booke of Psalmes in English Meter (1643)',
          'The Mysticall Marriage (1631)'])

_p('john-glyn', 'John Glyn', '1602–1666',
   'Lay Assessor (Commons)',
   'Recorder of London; prosecutor at Laud’s trial; later King’s Serjeant.',
   "Of Hart Hall Oxford and Lincoln's Inn, Glyn was Recorder of London from 1643 — the chief legal officer of the City — and MP for Westminster. He prosecuted Archbishop Laud's trial in 1644 and managed several Assembly-period impeachments. A moderate Presbyterian, he was briefly impeached by the army in 1647 alongside the 'Eleven Members.' He served Cromwell as a judge of the Upper Bench (1655), conformed at the Restoration, was knighted by Charles II, and made King's Serjeant. Died in 1666.",
   works=[])

_p('henry-vane-elder', 'Sir Henry Vane the Elder', '1589–1655',
   'Lay Assessor (Commons)',
   'Secretary of State to Charles I; broke with the king over Strafford.',
   "Of Brasenose Oxford and Gray's Inn, the elder Vane served Charles I as Cofferer of the Household and then Secretary of State (1640-41) until his quarrel with the king over the Earl of Strafford — Vane's evidence drawn from his notes of the Privy Council was decisive in Strafford's attainder. He broke with the king over religion, took the parliamentary side at the war's outbreak, and sat as a lay assessor at the Assembly. A more conservative figure than his more famous son, he was secluded at Pride's Purge and died in 1655.",
   works=[])

_p('walter-erle', 'Sir Walter Erle', '1586–1665',
   'Lay Assessor (Commons)',
   'Dorset MP; Lieutenant-General of the Ordnance; secluded at Pride’s Purge.',
   "Of New Inn Hall Oxford and the Middle Temple, Erle entered Parliament in 1614 and sat almost continuously until 1648 as an old-style Puritan gentry MP from Charborough in Dorset. He was Lieutenant-General of the Ordnance for Parliament during the Civil Wars and commanded the unsuccessful 1643 siege of Corfe Castle, repulsed by Lady Mary Bankes. A senior lay assessor at the Assembly and a moderate Presbyterian on church polity, he was secluded by Pride's Purge in December 1648 for refusing to support the regicide. He lived in retirement at Charborough until his death in 1665.",
   works=[])

_p('robert-harley', 'Sir Robert Harley', '1579–1656',
   'Lay Assessor (Commons)',
   'Master of the Mint; Westminster Abbey iconoclast; Brampton Bryan patron.',
   "Of Oriel Oxford and the Middle Temple, Harley was a long-serving MP for Radnorshire and (from 1641) Herefordshire and Master of the Mint from 1626. From his castle at Brampton Bryan — defended in his absence by his wife Brilliana through a fifteen-week royalist siege in 1643 — he sustained one of the most Puritan gentry households in the Welsh marches, sheltering and supporting Stanley Gower and other nonconforming ministers. As chairman of the parliamentary committee on the Abolition of Superstitious Monuments (1643), he superintended the iconoclasm at Westminster Abbey in 1644 — smashing altars, stained glass, and organs. He was secluded at Pride's Purge and died in 1656.",
   works=[])

_p('john-lisle', 'John Lisle', '1610–1664',
   'Lay Assessor (Commons)',
   'Regicide judge; assassinated in Lausanne by royalist agents.',
   "Of Magdalen Hall Oxford and the Middle Temple, Lisle was MP for Winchester and one of the parliamentary commissioners at the High Court of Justice that tried Charles I in January 1649 — he sat next to John Bradshaw and helped draft the king's sentence. He was Commissioner of the Great Seal under the Commonwealth (1649-1659). At the Restoration he was excepted from the Act of Indemnity, fled to Switzerland, and was shot dead by Irish royalist agents on the steps of the Reformed church at Lausanne on 11 August 1664.",
   works=[])

_p('edmund-prideaux', 'Edmund Prideaux', '1601–1659',
   'Lay Assessor (Commons)',
   'Attorney General to the Commonwealth; Postmaster of the Inland Letter Office.',
   "Of Cambridge then Inner Temple, Prideaux was a long-serving MP for Lyme Regis. As Postmaster of the Inland Letter Office from 1644 he reformed the English postal system, establishing the network of weekly cross-posts (London to Edinburgh, London to Dublin, London to Plymouth) that underlies the modern Royal Mail; the office became immensely lucrative. He was made Solicitor General in 1648 and Attorney General to the Commonwealth in 1649. A senior lay assessor at the Assembly, he died in August 1659, six months before the Restoration.",
   works=[])

_p('john-clotworthy', 'Sir John Clotworthy', 'd. 1665',
   'Lay Assessor (Commons)',
   'Ulster planter; anti-Strafford prosecutor; later Viscount Massereene.',
   "An Anglo-Irish Presbyterian planter in Ulster (the Antrim estates), Clotworthy was MP for Maldon and the parliamentary manager of the Strafford impeachment from the Irish side — his testimony on Strafford's Irish army was decisive. He served on the parliamentary committee for the propagation of the gospel in Ireland and as a senior lay assessor at the Assembly. Briefly imprisoned by the army in 1647 with the 'Eleven Members.' He survived the Interregnum, helped negotiate the Restoration, and was created Viscount Massereene in 1660. Died in 1665.",
   works=[])

_p('john-maynard-lawyer', 'John Maynard (the lawyer)', '1604–1690',
   'Lay Assessor (Commons)',
   'Serjeant-at-Law; long-lived legal eminence; prosecutor of Strafford and Laud.',
   "Of Exeter College Oxford and the Middle Temple, then Serjeant-at-Law and one of the longest-serving English lawyers of the century. Maynard the lawyer (distinct from John Maynard of Mayfield, the Sussex minister) was a lay assessor at the Assembly, prosecuted Strafford and Laud, and survived through Restoration and Glorious Revolution to die in 1690 aged eighty-seven. He was made King's Serjeant at the Restoration and continued to argue major cases into his ninth decade. His most famous remark — to William III on being told that his memory must be much decayed — was: 'Sir, I have forgot more than ever I knew.' Lord Macaulay called him 'the most learned lawyer of his age.'",
   works=[])

_p('walter-yonge', 'Walter Yonge', '1581–1649',
   'Lay Assessor (Commons)',
   'Devon diarist.',
   "Of the gentry family of Colyton in Devon, Yonge kept a remarkable manuscript diary from 1604 to 1645 — one of the most useful single sources for the religious and political history of Devon and of the Long Parliament's early years (the parliamentary section printed by the Camden Society, 1848). MP for Honiton, then Dartmouth; he served on numerous Commons committees through the early 1640s. A moderate Puritan lay assessor at the Assembly; his diary entries on Assembly business are uniquely informative for the gentry vantage. Died in 1649.",
   works=['Diary (1604–1628; 1642–1645)'])

_p('zouch-tate', 'Zouch Tate', '1606–1650',
   'Lay Assessor (Commons)',
   'Sponsor of the Self-Denying Ordinance; Northamptonshire Presbyterian MP.',
   "Of Christ Church Oxford and the Middle Temple, Tate was MP for Northampton and one of the parliamentary managers of the Solemn League and Covenant. He moved (with Sir Henry Vane the Younger seconding) the Self-Denying Ordinance of 9 December 1644 — which removed sitting MPs from military command and cleared the way for the New Model Army under Fairfax — and chaired the committee that drafted it. A steady Presbyterian lay assessor at the Assembly, he died in 1650.",
   works=[])

_p('john-rouse', 'John Rouse', 'd. c. 1660',
   'Lay Assessor (Commons)',
   'MP; distinct from Francis Rouse.',
   "A minor MP assessor often confused with Francis Rouse in older records.",
   works=[])


# ======================================================================
# VIII. LAY ASSESSORS — LORDS
# ======================================================================

_p('algernon-percy-northumberland', 'Algernon Percy, 10th Earl of Northumberland', '1602–1668',
   'Lay Assessor (Lords)',
   'Lord High Admiral; senior moderate peer; custodian of the royal children after Charles I’s execution.',
   "Of St John's Cambridge, the Percy heir succeeded his father in 1632 and was Lord High Admiral from 1638 until 1642, breaking with Charles I over the Bishops' Wars. A senior moderate parliamentary peer at the Assembly's opening, he was made Lord General of the Fleet by Parliament and given guardianship of the royal children (Henry, Henrietta, Elizabeth) after the regicide — Princess Elizabeth died in his care at Carisbrooke Castle in 1650. He opposed the king's execution and the Engagement Oath, withdrew from public life in 1649, and was restored to the Privy Council by Charles II at the Restoration. Died in 1668 at Petworth.",
   works=[])

_p('william-fiennes-saye-sele', 'William Fiennes, 1st Viscount Saye and Sele', '1582–1662',
   'Lay Assessor (Lords)',
   'Patriarch of the Independent peers; Providence Island and Saybrook colony patron.',
   "Of New College Oxford and the Middle Temple, Saye and Sele was the senior aristocratic patron of the Independent cause. He was head of the Providence Island Company (1630-1641), which sponsored Puritan colonising in the Caribbean, and (with Lord Brooke) co-patron of the Saybrook Colony in Connecticut (1635). His Broughton Castle in Oxfordshire was the meeting-place of the gentry circle that planned much of the Long Parliament's opposition to Charles I in the late 1630s — Hampden, Pym, St John, the elder Vane. He sympathised with Independent ecclesiology but stopped short of the regicide and retired from politics in 1649. Restored to the Privy Council at the Restoration. Father of Nathaniel Fiennes. Died in 1662.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=[])

_p('edward-montagu-manchester', 'Edward Montagu, 2nd Earl of Manchester', '1602–1671',
   'Lay Assessor (Lords)',
   'Commander of the Eastern Association; quarrelled with Cromwell at Newbury.',
   "Of Sidney Sussex Cambridge — the most Puritan of the Cambridge colleges. Manchester (then Viscount Mandeville) was one of the Five Members Charles I tried to arrest in January 1642. As Major-General of the Eastern Association army he won Marston Moor with Cromwell as his Lieutenant-General of Horse (July 1644), but his caution at the Second Battle of Newbury (October 1644) produced the famous quarrel with Cromwell — 'If we beat the King ninety and nine times yet he is King still…but if the King beat us once we shall be all hanged' — that triggered the Self-Denying Ordinance and the New Model. A moderate Presbyterian lay assessor at the Assembly, he withdrew at the regicide. Restored as Lord Chamberlain of the Household at the Restoration (1660). Died in 1671.",
   works=[])

_p('philip-herbert-pembroke', 'Philip Herbert, 4th Earl of Pembroke', '1584–1650',
   'Lay Assessor (Lords)',
   'Lord Chamberlain; patron of Shakespeare’s First Folio; Wilton House.',
   "Of New College Oxford, the Herbert heir succeeded his brother as 4th Earl of Pembroke and 1st Earl of Montgomery in 1630. Long-serving Lord Chamberlain (1626-1641), he had been the dedicatee — with his brother William — of Shakespeare's First Folio (1623). A moderate who took the parliamentary side at the war's outbreak, partly from personal animus against Strafford and Laud. His seat at Wilton was rebuilt during the war by Inigo Jones. He sat in the Lords until its abolition in 1649 and then accepted election to the Rump for Berkshire — a controversial step for a peer. Died in 1650.",
   works=[])

_p('william-cecil-salisbury', 'William Cecil, 2nd Earl of Salisbury', '1591–1668',
   'Lay Assessor (Lords)',
   'Grandson of Lord Burghley; senior moderate peer who served all regimes.',
   "Of St John's Cambridge, the grandson of William Cecil, Lord Burghley (Elizabeth I's chief minister). Captain of the Gentlemen Pensioners under Charles I (1612-1635) before breaking with the king. A senior moderate parliamentary peer at the Assembly, he sat in the Rump after the abolition of the Lords (1649), in Cromwell's Other House (1657), and was re-summoned to the Lords at the Restoration in 1660 — almost uniquely, he held a seat under every English regime between 1620 and 1668. Died at Hatfield House in 1668.",
   works=[])

_p('robert-greville-brooke', 'Robert Greville, 2nd Lord Brooke', '1607–1643',
   'Lay Assessor (Lords)',
   'Puritan peer; Saybrook patron; killed at the siege of Lichfield, 1643.',
   "Adopted heir of Fulke Greville (the courtier-poet, biographer of Sidney) and his successor in the barony. Brooke was the most intellectually serious of the Puritan peers — his The Nature of Truth (1640) is an early English engagement with anti-Aristotelian metaphysics and shows the influence of Hartlib's circle; A Discourse Opening the Nature of Episcopacie (1641) is one of the sharpest anti-episcopal polemics of the early Long Parliament. With Saye and Sele he was co-patron of the Saybrook Colony in Connecticut. Parliamentary commander in the Midlands, he was killed by a deaf-mute royalist sharpshooter from the spire of Lichfield Cathedral close on 2 March 1643 — four months before the Assembly opened, so his Assembly place was nominal. Independent in church sympathies.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=['The Nature of Truth (1640)',
          'A Discourse Opening the Nature of Episcopacie (1641)'])

_p('henry-grey-stamford', 'Henry Grey, 1st Earl of Stamford', '1599–1673',
   'Lay Assessor (Lords)',
   'West Country parliamentary commander; created earl 1628.',
   "Of Trinity College Cambridge; raised by Charles I to the earldom of Stamford in 1628. Parliamentary commander in the south-west during the early years of the war — he was defeated at Stratton in May 1643 by Sir Bevil Grenville's Cornish royalists and lost Exeter to Prince Maurice later that summer. Withdrew to private life after 1645. A moderate Presbyterian lay assessor at the Assembly; sat through the Long Parliament's reduced years and survived to the Restoration. Died in 1673.",
   works=[])

_p('philip-wharton', 'Philip Wharton, 4th Baron Wharton', '1613–1696',
   'Lay Assessor (Lords)',
   'Long-lived Independent patron; Wharton Bibles for Dissenting children.',
   "Of Exeter College Oxford, Wharton was thirty when the Assembly opened — the youngest of the peer assessors. He led a regiment at Edgehill (1642) and was a steady ally of Saye and Sele in the Independent interest. He withdrew at the regicide, refused office under the Protectorate, and was a leading manager of Restoration-era Dissent: a founder of the meetings that grew into the United Brethren and a constant patron of ejected ministers. By his will (1696) he endowed the 'Wharton Bibles' — Bibles distributed to dissenting children for two centuries afterwards. He lived through every English regime from James I to William III. Independent-leaning. Died in 1696, aged 83.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=[])

_p('edward-howard-escrick', 'Edward Howard, 1st Baron Howard of Escrick', 'd. 1675',
   'Lay Assessor (Lords)',
   'Moderate parliamentary peer.',
   "A minor parliamentary peer assessor. Survived to the Restoration.",
   works=[])

_p('dudley-north', 'Dudley North, 4th Baron North', '1602–1677',
   'Lay Assessor (Lords)',
   'Cambridgeshire peer; minor poet and essayist; father of Sir Dudley North the economist.',
   "Of St John's Cambridge and the Middle Temple, North succeeded his father (Dudley North the third Baron, courtier of James I) in 1666 — so during the Westminster years he sat as the younger Dudley North while his father held the title. He was a literary and antiquarian peer whose A Forest of Varieties (1645) collected occasional poems, essays, and translations, and Light in the Way to Paradise (1682) developed a moderate Reformed devotional theology. Father of Sir Dudley North, the merchant whose Discourses upon Trade (1691) is an early classic of laissez-faire economics. A quiet moderate lay assessor at the Assembly. Died in 1677.",
   works=['A Forest of Varieties (1645)',
          'Light in the Way to Paradise (1682)'])


# ======================================================================
# IX. ORIGINALLY NAMED BUT DECLINED OR ABSENT
# ======================================================================

_p('james-ussher', 'James Ussher', '1581–1656',
   'Originally named — declined (royalist)',
   'Archbishop of Armagh; loyalist who would not sit.',
   "The greatest scholar of the seventeenth-century British church — author of *Annales Veteris Testamenti* (1650) with its 4004 BC creation date, *De Romanae Ecclesiae Symbolo*, and the Irish Articles of 1615 that fed into the Westminster Confession. Ussher was named to the Assembly but refused to attend out of loyalty to Charles I, remaining in royalist Oxford. He was the most prominent absent figure the Assembly never had.",
   works=['Annales Veteris Testamenti (1650)',
          'A Body of Divinity (1645)',
          'The Reduction of Episcopacie (1656 posthum.)'])

_p('joseph-hall', 'Joseph Hall', '1574–1656',
   'Originally named — declined (royalist)',
   'Bishop of Exeter then Norwich; senior moderate-Calvinist Episcopalian.',
   "Of Emmanuel Cambridge under William Chaderton — one of the most Puritan of the early-Stuart Emmanuel cohort — Hall served as Dean of Worcester, then Bishop of Exeter (1627) and finally Norwich (1641). He was the senior moderate-Reformed bishop of his generation and a devotional writer of distinction whose Meditations and Vowes (1605), Heaven upon Earth (1606), and Contemplations on the Holy History (1612-15) anticipated the genre of structured devotional meditation that Bunyan and the later Puritans absorbed. His Episcopacie by Divine Right (1640) — written at Laud's request — was the immediate provocation for the Smectymnuan reply (1641). Named to the Assembly but loyal to episcopacy, he refused to sit. The Long Parliament impeached him in 1641 (he was briefly imprisoned in the Tower) and sequestered his episcopal estates in 1647; he lived his last years on the parish living at Higham. His Hard Measure (1647) chronicles the sequestration. Died in September 1656.",
   overrides={'ecclesiology_worship_polity': 'Reformed-Episcopal'},
   works=['Meditations and Vowes (1605)',
          'Episcopacie by Divine Right (1640)',
          'Hard Measure (1647)'])

_p('ralph-brownrig', 'Ralph Brownrig', '1592–1659',
   'Originally named — declined (royalist)',
   'Bishop of Exeter; Master of Catharine Hall; moderate Calvinist Episcopalian.',
   "Of Pembroke Cambridge, then Master of St Catharine's Hall Cambridge (1635-1645) and Bishop of Exeter from 1642. Brownrig was a Calvinist Episcopalian — closer to the Westminster doctrine on the decree and on justification than to Laudian sacramentalism — and a respected preacher, whose Sixty-five Sermons (posthum. 1661) circulated widely after his death. Named to the Westminster Assembly but he refused to sit because of its disestablishment of episcopacy. Ejected from the Mastership of Catharine Hall in 1645 and sequestered from his see in 1646, he lived in retirement at Bury St Edmunds and (later) the household of Sir Thomas Rich in London. Died in December 1659, a few months before the Restoration he had longed for.",
   overrides={'ecclesiology_worship_polity': 'Reformed-Episcopal'},
   works=['Sixty-five Sermons (posthum. 1661)'])

_p('thomas-westfield', 'Thomas Westfield', '1573–1644',
   'Originally named — declined (royalist)',
   'Bishop of Bristol; aged Calvinist Episcopalian; declined the Assembly.',
   "Of Jesus College Cambridge, then a long London ministry — vicar of Hornsey, archdeacon of St Albans, and finally Bishop of Bristol from 1642. Westfield was a Calvinist Episcopalian of the older Jacobean type, much closer doctrinally to the Westminster majority than to Laud's circle, but he refused the Assembly's summons out of episcopal loyalty. The royalists held Bristol from July 1643, and Westfield remained at his cathedral through the occupation. He died at Bristol in June 1644 — one of the older bishops whose physical survival into the Assembly years was brief.",
   overrides={'ecclesiology_worship_polity': 'Reformed-Episcopal'},
   works=['Sermons (posthum. 1646)'])

_p('robert-sanderson', 'Robert Sanderson', '1587–1663',
   'Originally named — declined (royalist)',
   'Regius Professor at Oxford; great Anglican casuist; later Bishop of Lincoln.',
   "Of Lincoln College Oxford and Regius Professor of Divinity (1642), Sanderson was the great moderate Anglican casuist of the seventeenth century — De Obligatione Conscientiae and De Iuramenti Promissorii Obligatione (both 1647, his Oxford lectures of 1646) are the Reformed Episcopalian counterpart to William Ames's Cases of Conscience and stand among the most rigorous treatments of conscience in any seventeenth-century language. Named to the Westminster Assembly but he refused to sit out of episcopal and royalist loyalty. Deprived of the Regius Chair in 1648 for refusing the Engagement Oath, he lived in retirement at Boothby Pagnell (Lincolnshire) until the Restoration brought him to the see of Lincoln (1660) for the last three years of his life. Izaak Walton wrote his Life (1678). Died in 1663.",
   overrides={'ecclesiology_worship_polity': 'Reformed-Episcopal'},
   works=['De Obligatione Conscientiae (1647)',
          'De Iuramenti Promissorii Obligatione (1647)'])

_p('henry-hammond', 'Henry Hammond', '1605–1660',
   'Originally named — declined (royalist)',
   'Chaplain to Charles I; "father of English biblical criticism"; chief Anglican polemicist against the Assembly.',
   "Of Magdalen College Oxford, then rector of Penshurst in Kent (1633), Canon of Christ Church Oxford, and royal chaplain to Charles I from 1645. Hammond was the most prolific royalist polemicist against the Assembly's work — A View of the New Directorie (1646) attacked the Directory for Public Worship, A View of Some Exceptions to the Annotations (1647) replied to the Westminster Annotations on the Bible, and Of Schisme (1653) defended episcopal continuity against both Presbyterian and Independent ecclesiology. With Edward Pococke he edited the most learned mid-century Anglican biblical commentary, A Paraphrase and Annotations upon All the Books of the New Testament (1653) — a work that earned him the later title 'father of English biblical criticism' for its sustained attention to the Greek text. His Practical Catechisme (1645) was the principal Anglican catechetical text of the period. He died in April 1660, a month before the Restoration he had longed for.",
   overrides={'ecclesiology_worship_polity': 'Reformed-Episcopal'},
   works=['A Practicall Catechisme (1645)',
          'A Paraphrase and Annotations upon all the Books of the New Testament (1653)'])

_p('thomas-fuller', 'Thomas Fuller', '1608–1661',
   'Originally named — minimal attendance (royalist sympathy)',
   'Church historian; "*Worthies of England*"; chaplain to Hopton’s army.',
   "Of Queens' Cambridge and (later) Sidney Sussex Cambridge, Fuller was the great church historian and biographer of the period. Named to the Assembly, he attended only the earliest sessions (summer 1643) before withdrawing to the royalist side. He served as chaplain to Sir Ralph Hopton's army through the western campaigns and accompanied the king to Exeter. His prolific output — The Holy and Profane State (1642), The Church-History of Britain (1655) which is the first substantial English narrative of the English church from Augustine of Canterbury, and the posthumous History of the Worthies of England (1662) which gathered county-by-county biographies of every notable figure — is the genial royalist counterpart to the more polemical histories of the Civil War years. He conformed at the Restoration but died of fever in August 1661, before he could receive promotion.",
   overrides={'ecclesiology_worship_polity': 'Reformed-Episcopal'},
   works=['The Holy and Profane State (1642)',
          'Church-History of Britain (1655)',
          'Worthies of England (1662)'])

_p('walter-balcanqual', 'Walter Balcanqual', 'c. 1586–1645',
   'Originally named — declined (royalist)',
   'Scottish-born Dean of Durham; British delegate to the Synod of Dort.',
   "Scottish-born and of Pembroke Cambridge, Balcanqual was one of the British delegates Charles I's father sent to the Synod of Dort in 1618-19 (the others being George Carleton, Joseph Hall, John Davenant, and Thomas Goad) — a context that taught him the Continental Reformed setting that the Westminster divines later inherited. Made Dean of Rochester (1624) and then Dean of Durham (1639). His Large Declaration concerning the Late Tumults in Scotland (1639), drafted for Charles I, was the king's official polemic against the Scottish Covenanters and made Balcanqual a hated figure in his native country. Named to the Westminster Assembly but he refused to sit out of episcopal and royalist loyalty. He died in flight at Chirk Castle in 1645, having fled both the parliamentary and the Covenanting forces.",
   overrides={'ecclesiology_worship_polity': 'Reformed-Episcopal'},
   works=['Large Declaration concerning the Late Tumults in Scotland (1639)'])


# ======================================================================
# X. ADDITIONAL MINISTERS — SUPERADDED, IRENICISTS, ARMY CHAPLAINS,
#    AND LESSER-DOCUMENTED COUNTY MEMBERS
# ======================================================================

_p('john-dury', 'John Dury', '1596–1680',
   'Scottish-born irenicist; superadded',
   'Apostle of Protestant Union; tireless ecumenical traveller.',
   "Scottish-born, educated in the Netherlands and at Leiden, Dury spent his career attempting the impossible: a Pan-Protestant doctrinal union. He travelled between Lutheran, Reformed, and Anglican synods for fifty years carrying letters, drafts, and a remarkable patience for hostile receptions. Attended Westminster in 1643-44 as a superadded divine before resuming his continental rounds. His vast correspondence with Comenius, Mersenne, Hartlib, and dozens of central European theologians anticipates the Enlightenment republic of letters. Died at Cassel in 1680.",
   works=['Consultatio Theologica Super Negotio Pacis Ecclesiasticae (1654)',
          'A Memoriall Concerning Peace Ecclesiasticall (1641)'])

_p('hugh-peters', 'Hugh Peters', '1598–1660',
   'Independent army chaplain; superadded',
   'Chaplain to the New Model Army; executed as a regicide.',
   "Trinity Cambridge, then a Massachusetts ministry at Salem (1635–41) where he replaced Roger Williams, then chaplain to the New Model. Peters was a flamboyant army preacher — Carlyle called him 'a man as full of fire as a fox-cub' — and a frequent presence near Cromwell. His Assembly attendance was sporadic, but he was named to the superaddition list. At the Restoration he was tried as a regicide and hanged, drawn, and quartered at Charing Cross on 16 October 1660 alongside John Cook.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=['Mr Peters Last Report of the English Wars (1646)',
          'Good Work for a Good Magistrate (1651)'])

_p('joshua-sprigg', 'Joshua Sprigg', '1618–1684',
   'Independent army chaplain',
   'Chaplain to Fairfax; historian of the New Model Army.',
   "Of New Inn Hall Oxford under John Goodwin's influence, Sprigg became chaplain to Sir Thomas Fairfax through the campaigns of 1645-47. His Anglia Rediviva: England's Recovery (1647) is the indispensable contemporary military history of the New Model's first year — Naseby, Langport, Bristol, the storming of Bridgwater — written from inside Fairfax's headquarters and dedicated to him. His sympathies tilted Independent after 1647 and he was named to the Assembly's superaddition list, though his attendance was limited. He held a Fellowship at All Souls Oxford under the parliamentary visitation (1650-58) and pleaded for Charles I's life at his trial. Retired to private life under the Protectorate and Restoration. Died at Crayford in Kent in 1684.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=['Anglia Rediviva: England’s Recovery (1647)'])

_p('george-newton-taunton', 'George Newton', '1602–1681',
   'English Presbyterian minister',
   'Long western Presbyterian ministry at Taunton; pastoral hero of the 1645 siege.',
   "Of Magdalen Hall Oxford, then Taunton (Somerset) from 1631 — a fifty-year ministry that spanned the entire generation of the Civil Wars. Newton's pastoral ministry through the brutal three-month royalist siege of Taunton (December 1644 — May 1645), in which the town was largely burnt and its inhabitants reduced to near-starvation under Sir Ralph Hopton's army, made him a local hero. He attended the Assembly intermittently — Somerset was far from London during war years — and his Assembly contributions are slight. Ejected in 1662 under the Act of Uniformity but continued to preach privately at his house in Taunton, where he died in 1681. He was succeeded in his gathered Dissenting congregation by Joseph Alleine.",
   works=['A Sermon Preached the 11. of May, 1652 (1653)'])

_p('thomas-valentine', 'Thomas Valentine', 'd. 1665',
   'English Presbyterian minister',
   'Chalfont St Giles (Bucks); minor Assembly attender.',
   "Of Christ's College Cambridge, then Chalfont St Giles in Buckinghamshire from 1631 — the parish where John Milton would later live in retirement at the Restoration. Valentine attended the Assembly intermittently through the mid-1640s and contributed to the catechetical committee in a minor capacity. He preached the parliamentary fast sermon Two Sermons (1647). Ejected from Chalfont St Giles in 1662 under the Act of Uniformity; died in 1665.",
   works=['Two Sermons (1647)'])

_p('richard-byfield', 'Richard Byfield', '1598–1664',
   'English Presbyterian minister',
   'Long Ditton (Surrey); brother of the scribe Adoniram Byfield.',
   "Of Queens' College Oxford, then Long Ditton in Surrey from 1627. Richard Byfield was the elder brother of Adoniram the scribe and the son of Nicholas Byfield of Stoke Newington (the Cheshire Puritan whose Marrow of the Oracles of God (1620) was a standard household catechetical handbook). A steady Surrey Presbyterian, Byfield attended the Westminster Assembly through its long main sessions and contributed to the catechetical committee in a minor capacity. He preached the parliamentary fast sermon Temple-Defilers Defiled (1645) against the radical sects. Ejected from Long Ditton in 1662 under the Act of Uniformity; died in 1664.",
   works=['Temple-Defilers Defiled (1645)',
          'The Power of the Christ of God (1641)'])

_p('benjamin-needler', 'Benjamin Needler', '1620–1682',
   'English Presbyterian minister',
   'St Margaret Moses; younger Presbyterian; ejected 1662.',
   "Of St John's College Oxford, then St Margaret Moses in London from 1645 — one of the younger ministers added to the Assembly's later sessions, joining when the catechetical work was already well advanced. His Expository Notes, with Practical Observations on Genesis (1655) collects his weekday lectures and is one of the few sustained Westminster-divine expositions of Genesis. He was an active member of the third London Presbyterian classis. Ejected from St Margaret Moses in 1662 under the Act of Uniformity, he ministered privately in Oxfordshire and London until his death in 1682.",
   works=['Expository Notes upon Genesis (1655)'])

_p('thomas-hodges-kensington', 'Thomas Hodges', 'd. 1672',
   'English Presbyterian minister',
   'Kensington and Christ Church Newgate; chaplain to Pembroke; later conformist.',
   "Of Magdalen Hall Oxford, then chaplain to Philip Herbert, 4th Earl of Pembroke (one of the senior lay assessors at the Assembly) and rector of Kensington from 1640. Hodges sat on the Assembly's middle bench, contributed to the catechetical work and the chapter on the moral law, and was a moderate Presbyterian closer to Reynolds than to Calamy on the broader settlement question. After the Restoration he conformed in 1662, succeeded Cranford at Christ Church Newgate, and was made Dean of Hereford. Died in 1672. His best-known sermon is Inaccessible Glory (1655), preached at the funeral of Lord Wharton's daughter.",
   works=['Inaccessible Glory (1655)'])

_p('arthur-jackson', 'Arthur Jackson', '1593–1666',
   'English Presbyterian minister',
   'St Faith’s London; commentator on Scripture.',
   "Trinity Cambridge, then St Michael Wood Street and St Faith's London. Jackson published Reformed commentaries on the Pentateuch (1643), the historical books, and the prophets — one of the major mid-century English Bible-commentary projects, intended as a Reformed counterweight to Hugo Grotius's Annotationes. He attended the Assembly through its main sessions, was ejected at St Faith's in 1662, and died in 1666.",
   works=['Annotations upon the Five Books, Immediately Following the Historicall Part of the Old Testament (1646)',
          'Annotations upon the Whole Book of Psalms (1658)'])

_p('thomas-bedford', 'Thomas Bedford', 'd. 1653',
   'English Presbyterian minister',
   'Plymouth and Newton St Cyres (Devon); sacramental theologian.',
   "An Oxford-trained Devon minister, settled at Plymouth and then at Newton St Cyres in Devon. Bedford published an important Westminster-period treatise on the sacraments — Vindiciae Gratiae Sacramentalis (1650) and the earlier A Treatise of the Sacraments (1638) — defending an Augustinian-Reformed reading of sacramental efficacy against both Roman ex opere operato and the bare-memorial Zwinglian alternative. His position aligns with the WCF XXVII–XXIX signs-and-seals language. He attended the Assembly through its later sessions in the late 1640s and died in 1653.",
   works=['Vindiciae Gratiae Sacramentalis (1650)',
          'A Treatise of the Sacraments (1638)'])

_p('calybute-downing', 'Calybute Downing', '1606–1644',
   'English Presbyterian minister',
   'Hackney rector; early political theologian of parliamentary resistance.',
   "Of Oriel College Oxford and Christ Church, then chaplain to Sir Charles Howard before becoming vicar of Hackney from 1637. Downing was the political theologian of the early Assembly: his 1640 Sermon Preached to the Renowned Company of the Artillery argued for the godly's right of resistance against tyrannical magistrates, anticipating Rutherford's Lex Rex by four years and producing a momentary parliamentary scandal (Downing was reported to the Lords for sedition). A Discourse of the State Ecclesiasticall of this Kingdome in Relation to the Civill (1633) had earlier argued for state regulation of the church on Erastian-sounding principles, though without Selden's later sharpness. At Westminster he was one of the more politically active early members, but he died young in September 1644 only a year into the Assembly.",
   works=['A Discourse of the State Ecclesiasticall of this Kingdome in Relation to the Civill (1633)',
          'A Sermon Preached to the Renowned Company of the Artillery (1641)'])

_p('edward-bowles', 'Edward Bowles', '1613–1662',
   'English Presbyterian minister',
   'York Minster preacher; northern Presbyterian negotiator with the army.',
   "Of St Catharine's Hall Cambridge, then chaplain to the Earl of Manchester through the Eastern Association campaigns of 1644-45 (Marston Moor; the second battle of Newbury). From 1645 he was settled as preacher at York Minster, where he became the principal Presbyterian voice in northern England. He was a key negotiator between the army and Parliament during the 1647 crisis and one of the parliamentary chaplains at the abortive Treaty of Newport with Charles I (1648). Strong Presbyterian, anti-Independent, but pragmatic enough that he was much used as a mediator. He died in August 1662, just before the Act of Uniformity could eject him — succeeded at the Minster by Edmund Hough.",
   works=['Manifest Truths (1646)',
          'The Mysterie of Iniquity Yet Working in the Kingdomes (1643)'])

_p('edward-corbet', 'Edward Corbet', 'd. 1658',
   'English Presbyterian minister',
   'Merton then Magdalen Oxford; parliamentary visitor.',
   "Of Merton College Oxford and (later) Magdalen College, then rector of Chartham (Kent) and Great Haseley (Oxon). Corbet served on the parliamentary visitation of Oxford (1647-48), one of the visitors who oversaw the ejection of royalist heads of house and the installation of Reformed replacements. He contributed steadily to the Westminster Assembly's later sessions in the catechetical phase. His fast sermon Gods Providence (1642) defended the parliamentary cause from Romans 13. He died in 1658.",
   works=['Gods Providence (1642)'])

_p('james-cranford', 'James Cranford', 'd. 1657',
   'English Presbyterian minister',
   'Christ Church Newgate; anti-Independent controversialist; censor of Reformed presses.',
   "Of Magdalen Hall Oxford, then rector of Brockhall in Northamptonshire and (from 1645) Christ Church Newgate in London. Cranford was one of the more vehement anti-Independent polemicists at the Assembly — Haereseo-Machia, or the Mischiefes which Heresies doe (1646) catalogued the dangers of toleration — and one of the editors who introduced the work of Continental Reformed authors (especially Voetius's polemics against the Remonstrants) to English readers. He served as licenser for the Sion College divines, controlling much of London's Reformed religious publishing in the late 1640s. Died in 1657, five years before the Great Ejection.",
   works=['Haereseo-Machia (1646)',
          'The Teares of Ireland (1642)'])

_p('stanley-gower', 'Stanley Gower', 'd. 1660',
   'English Presbyterian minister',
   'Brampton Bryan and Dorchester; Harley family chaplain through three sieges.',
   "Chaplain to Sir Robert Harley at Brampton Bryan in Herefordshire from the early 1630s, where the Harleys' Puritan household became one of the great rural centres of Reformed piety in the Welsh marches. Gower remained at Brampton Bryan through Lady Brilliana Harley's celebrated defence of the castle during the fifteen-week royalist siege of 1643 (Brilliana, ill from the strain, died shortly after raising the siege). After Brampton Bryan was overrun in 1644 he moved to London and then succeeded John White as rector of Holy Trinity Dorchester in 1648. A steady Presbyterian Assembly attender through the main sessions; he preached the parliamentary fast sermon Things Now-a-Doing (1644). Died at Dorchester in 1660.",
   works=['Things Now-a-Doing (1644)'])

_p('william-strong', 'William Strong', 'd. 1654',
   'Independent minister',
   'St Dunstan-in-the-East; preacher at Westminster Abbey.',
   "Of St Catharine's Hall Cambridge, then St Dunstan-in-the-East in London and (from 1650) preacher at Westminster Abbey itself — the Independent congregation gathered there during the Commonwealth had Strong as its principal voice. He attended the Assembly's later sessions as one of the younger Independents and was a member of John Owen's circle. His posthumously published A Discourse of the Two Covenants (1678) is a substantial federal-theology treatise that works out an Independent reading of the covenant of redemption alongside the covenants of works and grace; XXXI Select Sermons (1656) collected his Westminster Abbey preaching. Died in office at Westminster in 1654.",
   overrides={'ecclesiology_worship_polity': 'Independent-Congregational'},
   works=['XXXI Select Sermons (1656)',
          'A Discourse of the Two Covenants (1678)'])

_p('john-trapp', 'John Trapp', '1601–1669',
   'English Presbyterian minister',
   'Commentator on the whole Bible; the Puritan epigrammatist.',
   "Of Christ Church Oxford, then Weston-on-Avon (Warwickshire) and (later) Welford-on-Avon. Schoolmaster at Stratford-upon-Avon for some years, where local tradition makes him a kind of successor to Shakespeare's old grammar-school master. Trapp was the Assembly's most prolific Bible commentator — A Commentary or Exposition upon All the Books of the New and Old Testament (5 folio volumes, 1646-62) is famous for its concision and aphoristic style. C.H. Spurgeon called him 'rich, racy, and rare' and recommended that any preacher who could afford his commentaries should buy them. A quietly conformist Presbyterian at the Assembly. He survived the Restoration in his parish, conformed in 1662, and died at Weston in 1669.",
   works=['A Commentary or Exposition upon All the Books of the New and Old Testament (5 vols, 1646–62)',
          'Gods Love-Tokens (1637)'])

_p('thomas-cawton-elder', 'Thomas Cawton the Elder', '1605–1659',
   'English Presbyterian minister',
   'St Bartholomew-by-the-Exchange; exiled to Rotterdam after Love plot.',
   "Of Queens' College Cambridge, then a long London ministry — first at Wivenhoe (Essex) and then St Bartholomew-by-the-Exchange in London from 1644, succeeding Stephen Marshall there. A steady Presbyterian at the Assembly, he attended through the main sessions and was active in the London ministerial association. He was implicated in the 1651 Love plot — arrested with Case and Jenkin, briefly imprisoned in the Tower — and then fled to Rotterdam (1652) where he ministered to the English exile Reformed congregation. He died at Rotterdam in 1659. His son's biography The Life and Death of Mr Thomas Cawton (1662) is a small classic of seventeenth-century English religious life-writing.",
   works=['The Life and Death of Mr Thomas Cawton (1662, biography by his son)'])

_p('benjamin-pickering', 'Benjamin Pickering', 'fl. 1640s',
   'English Presbyterian minister',
   'Sussex country minister.',
   "A Sussex country minister, named to the Assembly and intermittently attending; biographical record thin. Voted with the Presbyterian mainstream on the polity question.",
   works=[])

_p('francis-whiddon', 'Francis Whiddon', 'fl. 1640s',
   'English Presbyterian minister',
   'Moretonhampstead (Devon) minister.',
   "A Devon country minister, intermittent attender at the Assembly, with thin biographical record. Voted with the Presbyterian mainstream.",
   works=[])

_p('henry-painter', 'Henry Painter', 'd. 1652',
   'English Presbyterian minister',
   'Exeter minister.',
   "An Exeter minister, intermittent attender at the Assembly. Died in 1652.",
   works=[])

_p('henry-hall-norwich', 'Henry Hall', 'fl. 1640s',
   'English Presbyterian minister',
   'Norwich Presbyterian member; distinct from Bishop Joseph Hall.',
   "A Norwich minister, attender at the Assembly, with thin biographical record. Distinct from the royalist Bishop Joseph Hall (slot above).",
   works=[])

_p('charles-herbert', 'Charles Herbert', 'fl. 1640s',
   'English Presbyterian minister',
   'Welsh-border minister.',
   "A Welsh-border minister, named to the Assembly; biographical record very thin.",
   works=[])

_p('sampson-saunders', 'Sampson Saunders', 'fl. 1640s',
   'English Presbyterian minister',
   'Western country minister.',
   "A western country minister, named to the Assembly, intermittent attender; left no published work of substance.",
   works=[])

_p('arthur-salway', 'Arthur Salway', 'd. 1656',
   'English Presbyterian minister',
   'Severn Stoke (Worcestershire) minister.',
   "A Worcestershire country minister, intermittent attender at the Assembly. Died in 1656.",
   works=[])

_p('john-foxley', 'John Foxley', 'fl. 1640s',
   'English Presbyterian minister',
   'Essex country minister.',
   "An Essex country minister, intermittent attender at the Assembly with no published output of substance.",
   works=[])

_p('jasper-hicks', 'Jasper Hicks', 'fl. 1640s',
   'English Presbyterian minister',
   'Cornish minister; minor contributor.',
   "A Cornish minister, named in the ordinance and attending sporadically.",
   works=[])

_p('richard-cleyton', 'Richard Cleyton', 'fl. 1640s',
   'English Presbyterian minister',
   'Hertfordshire minister.',
   "A Hertfordshire minister with thin biographical record; minor contributor at the Assembly.",
   works=[])

_p('john-downing', 'John Downing', 'fl. 1640s',
   'English Presbyterian minister',
   'Sussex minister.',
   "A Sussex country minister, named to the Assembly, attending intermittently.",
   works=[])

_p('john-harris-magdalen', 'John Harris', 'd. 1658',
   'English Presbyterian minister',
   'Magdalen Hall Oxford; distinct from Robert Harris of Trinity.',
   "Distinct from Robert Harris of Trinity (slot above), this John Harris was an Oxford-trained minister who voted with the Presbyterian mainstream. He died in 1658.",
   works=[])

_p('francis-coke', 'Francis Coke', 'fl. 1640s',
   'English Presbyterian minister',
   'Yoxall (Staffordshire) minister.',
   "A Staffordshire minister, named to the Assembly, attending intermittently.",
   works=[])

_p('john-arthur', 'John Arthur', 'fl. 1640s',
   'English Presbyterian minister',
   'Berkshire minister.',
   "A Berkshire minister, intermittent attender at the Assembly. Reportedly conformed after the Restoration.",
   works=[])

_p('henry-hutton', 'Henry Hutton', 'fl. 1640s',
   'English Presbyterian minister',
   'Northern circuit; minor contributor.',
   "A northern minister with thin biographical record; intermittent attender at the Assembly.",
   works=[])

_p('john-bath', 'John Bath', 'fl. 1640s',
   'English Presbyterian minister',
   'Western minister.',
   "A western country minister, intermittent attender at the Assembly, with thin biographical record.",
   works=[])

_p('humphrey-saunders', 'Humphrey Saunders', 'fl. 1640s',
   'English Presbyterian minister',
   'Western country minister.',
   "A western country minister, intermittent attender at the Assembly; left no published output of substance.",
   works=[])

_p('john-ward-ipswich', 'John Ward of Ipswich', 'fl. 1640s',
   'English Presbyterian minister',
   'East Anglian Presbyterian.',
   "A steady Ipswich Presbyterian, attended the Assembly intermittently. Voted with the Presbyterian mainstream.",
   works=[])

_p('john-cardell', 'John Cardell', 'fl. 1640s',
   'English Presbyterian minister',
   'St Anne Aldersgate; London Presbyterian.',
   "London minister named to the Assembly with thin biographical detail beyond his attendance and middle-bench voting.",
   works=[])


# ======================================================================
# XI. ADDITIONAL LAY ASSESSORS — COMMONS AND LORDS
# ======================================================================

_p('john-hampden', 'John Hampden', '1594–1643',
   'Lay Assessor (Commons) — d. June 1643',
   'Ship Money resister; mortally wounded at Chalgrove Field.',
   "Of Magdalen Oxford and the Inner Temple, then a long parliamentary career as MP for Buckinghamshire — the cousin (and close ally) of Oliver Cromwell. Hampden's refusal to pay the twenty shillings of Ship Money assessed on his Buckinghamshire estate in 1635 produced the great constitutional case of the personal-rule decade: the judgement was for the king (1638) but only narrowly, and the case became the touchstone of parliamentary resistance to royal prerogative taxation. He was one of the Five Members Charles I tried to arrest in January 1642. He was named a lay assessor at the Assembly's opening but had no chance to attend: he was mortally wounded by Prince Rupert's troops at Chalgrove Field on 18 June 1643 (he was hit in the shoulder, the ball ranging into his chest) and died at Thame on 24 June — a week before the Assembly first sat. His name remained on the rolls in absentia.",
   works=[])

_p('sir-arthur-haselrig', 'Sir Arthur Haselrig', 'c. 1601–1661',
   'Lay Assessor (Commons)',
   'One of the Five Members; raised the "Lobsters" regiment; republican leader; died in the Tower.',
   "Of Magdalen Oxford and Gray's Inn, then MP for Leicester and one of the Five Members Charles I tried to arrest on 4 January 1642 — the proximate cause of the king's flight from London. He was instrumental in the impeachments of Strafford (1640) and Laud (1644). Haselrig raised the regiment of 'Lobsters' (heavy cuirassiers in lobster-tail helmets) for Parliament and fought at Roundway Down. After the regicide he served on the Council of State (1649-1653) and as Governor of Newcastle. He broke with Cromwell over the Protectorate, leading the parliamentary opposition that toppled Richard Cromwell in 1659 — only to be outmanoeuvred by Monck the following year. At the Restoration he was imprisoned in the Tower and died there in January 1661, in conditions Charles II reportedly thought too lenient and Pepys thought too cruel.",
   works=[])

_p('sir-thomas-widdrington', 'Sir Thomas Widdrington', 'c. 1600–1664',
   'Lay Assessor (Commons)',
   'Speaker of the Commons (1656); legal historian; Recorder of York.',
   "Of Christ's College Cambridge and Gray's Inn, then a long legal-parliamentary career — Recorder of York and (briefly) Recorder of Berwick before becoming MP for Berwick in the Long Parliament. Widdrington was a Commissioner of the Great Seal under the Commonwealth (1648-49) and Speaker of the Cromwellian Second Protectorate Parliament (1656-57). A moderate Presbyterian lay assessor at the Assembly. Married to Frances Fairfax, the future Lord General Sir Thomas Fairfax's sister. His Analecta Eboracensia, an antiquarian history of York compiled in retirement, was finally published in 1897. He survived the Restoration in private life and died in 1664.",
   works=['Analecta Eboracensia (posthum. 1897)'])

_p('basil-feilding-denbigh', 'Basil Feilding, 2nd Earl of Denbigh', '1608–1675',
   'Lay Assessor (Lords)',
   'Parliamentary commander in the West Midlands; ambassador to Venice.',
   "Of Queens' Cambridge, Feilding served as ambassador to Venice (1634-39) before the war and brought a continental polish unusual among the Puritan peers. He took the parliamentary side on his father's death in battle on the royalist side (April 1643) and was made commander-in-chief of the parliamentary forces in the West Midlands (1643-44) — replaced by Major-General Browne after a series of indecisive engagements. A moderate lay assessor at the Assembly, he opposed the regicide, withdrew at Pride's Purge, and survived the Restoration in private life. Died in 1675.",
   works=[])

_p('francis-russell-bedford', 'Francis Russell, 4th Earl of Bedford', '1593–1641',
   'Lay Assessor (Lords) — d. May 1641',
   'Senior Puritan peer; would-be Lord Treasurer; died before the Assembly opened.',
   "Of Magdalen Oxford, then a long political career managing the fen drainage projects of the Bedford Level Company (the Great Level of the Fens, the project that drained much of East Anglia). Bedford was the senior Puritan peer and the political manager of the early Long Parliament — Charles I tried to detach him by offering him the Treasurership in early 1641, the so-called 'Bridge appointments' scheme, but the deal collapsed when Strafford's attainder hardened the parliamentary side. Bedford died of smallpox on 9 May 1641, just twelve days before Strafford's execution and two years before the Westminster Assembly first sat — but his name appears in early plans for the gathering.",
   works=[])

_p('robert-rich-warwick', 'Robert Rich, 2nd Earl of Warwick', '1587–1658',
   'Lay Assessor (Lords)',
   'Lord High Admiral of the Parliament’s fleet; senior New England patron.',
   "Of Emmanuel Cambridge, then a long Puritan political career as the senior maritime patron of New England colonisation. He held the Bermuda and Somers Islands Company patents and was a leading backer of the Providence Island Company, the Massachusetts Bay Company, and the early Rhode Island settlements; Roger Williams's 1644 charter for Providence Plantations was secured through his influence. As Lord High Admiral of the Parliament's fleet (1642) he held the navy for Parliament at the war's outbreak, depriving Charles of seaborne supply. A senior lay assessor at the Assembly. He opposed the regicide and was deprived of the Admiralty after 1649. Died in 1658.",
   works=[])

_p('john-crewe', 'John Crewe, 1st Baron Crewe', '1598–1679',
   'Lay Assessor (Commons)',
   'Long parliamentary career; Treaty of Newport commissioner; created peer at the Restoration.',
   "Of Gray's Inn, Crewe was MP for Northamptonshire and one of the long Parliament's most active committee chairs through the 1640s. A moderate Presbyterian, he served on the parliamentary commissioners at the Treaty of Newport with Charles I (September-November 1648) and was secluded at Pride's Purge for his vote to continue negotiations. He withdrew from politics during the Protectorate and returned for the Convention Parliament of 1660, helping to manage the Restoration; he was created Baron Crewe in April 1661. Died in 1679.",
   works=[])

_p('sir-richard-onslow', 'Sir Richard Onslow', '1601–1664',
   'Lay Assessor (Commons)',
   'Surrey parliamentary commander; moderate Presbyterian.',
   "Of Inner Temple, Onslow was MP for Surrey and Colonel of the Surrey trained bands, defending the southern home counties against royalist incursions through the war. A moderate Presbyterian lay assessor at the Assembly, he was briefly arrested by the army in 1647 and again in 1648. He sat in Cromwell's Other House but withdrew before the regicide. He survived the Restoration in private life at Clandon and died in 1664; the Onslow earldom is descended from him.",
   works=[])

_p('sir-john-wray', 'Sir John Wray', '1586–1655',
   'Lay Assessor (Commons)',
   'Lincolnshire baronet; long-standing patron of Puritan ministers.',
   "Of Magdalene Cambridge and Lincoln's Inn, Wray was a Lincolnshire baronet (created 1611) and long-serving knight of the shire (MP for Lincolnshire). A devoted Puritan patron, he sheltered nonconforming ministers on his Glentworth estates through the Laudian persecutions and supported the parliamentary cause early. A senior lay assessor at the Assembly through its main sessions and a moderate Presbyterian vote, he died in 1655.",
   works=[])

_p('sir-robert-pye', 'Sir Robert Pye', '1585–1662',
   'Lay Assessor (Commons)',
   'Auditor of the Receipt of the Exchequer; father-in-law to Hampden.',
   "Of Inner Temple, Pye was Auditor of the Receipt of the Exchequer from 1618 — one of the senior treasury offices — and long-serving MP for Bath and later Berkshire. He had been Buckingham's protégé before falling out with Charles I over Ship Money. His daughter Anne married John Hampden, and Pye's seat at Faringdon was Hampden's last refuge in 1643. A moderate lay assessor at the Assembly, he sat through the Long Parliament's reduced years and died in 1662.",
   works=[])

_p('john-glynne-2', 'John Glynne (alternate spelling)', '— see john-glyn',
   'Lay Assessor (Commons)',
   'Spelling variant placeholder for John Glyn.',
   "Spelling variant of John Glyn (Recorder of London); the active record is at the earlier slot.",
   works=[])


# ======================================================================
# XII. ADDITIONAL DECLINED OR ORIGINALLY-NAMED ROYALIST DIVINES
# ======================================================================

_p('george-morley', 'George Morley', '1598–1684',
   'Originally named — declined (royalist)',
   'Later Bishop of Winchester; senior Anglican manager of the Restoration settlement.',
   "Of Christ Church Oxford under Brian Duppa, Morley was royal chaplain to Charles I and a familiar of Sidney's circle at Great Tew (Lord Falkland's house, where Clarendon, Sheldon, Chillingworth, and Hammond met). Named to the Westminster Assembly but he refused to sit, remaining with the king's cause; he was deprived of his Christ Church canonry and went into exile in Antwerp, the Hague, and Breda as one of Charles II's most trusted exiled chaplains. He preached the sermon at Charles II's coronation at Scone in 1651 and was the senior chaplain to the king in Brussels through the late 1650s. At the Restoration he became Bishop of Worcester (1660) and then Winchester (1662-84), and was the senior Anglican manager — alongside Sheldon — of the Savoy Conference (1661) and the negotiations that produced the Act of Uniformity and the Great Ejection. Died in 1684, aged 86.",
   overrides={'ecclesiology_worship_polity': 'Reformed-Episcopal'},
   works=['A Modest Advertisement Concerning the Present Controversie about Church Government (1641)',
          'Several Treatises (1683)'])

_p('brian-walton', 'Brian Walton', '1600–1661',
   'Originally named — declined (royalist)',
   'Editor of the London Polyglot Bible (1657); later Bishop of Chester.',
   "Magdalen Cambridge, then St Martin Orgar in London until sequestered (1641) for refusing to read the Long Parliament's Protestation. Walton was named to the Assembly but declined out of episcopal loyalty. He spent the Interregnum editing the London Polyglot Bible (1657) — the most ambitious Bible-editing project of the seventeenth century — and was made Bishop of Chester at the Restoration. He died in 1661.",
   overrides={'ecclesiology_worship_polity': 'Reformed-Episcopal'},
   works=['Biblia Sacra Polyglotta (6 vols, 1654–57)',
          'A Treatise Concerning the Payment of Tythes (1641)'])

_p('john-cosin', 'John Cosin', '1594–1672',
   'Originally named — declined (royalist)',
   'Master of Peterhouse; later Bishop of Durham; the great high-church liturgist.',
   "Of Caius College Cambridge, then chaplain to Bishop Overall and (from 1635) Master of Peterhouse Cambridge — where his Laudian liturgical innovations (the marble altar, the candles, the eastward position) made Peterhouse a Puritan target. He was the most pronouncedly high-church of the figures named to the Westminster Assembly and refused to sit. A Collection of Private Devotions (1627) — compiled at the Queen's request and adapted from the older Book of Hours — had been one of the most contested Laudian devotional books. The Long Parliament deprived him of all his offices in 1641 and 1644; he went into exile in Paris as Anglican chaplain to the royalist exiles at the Louvre (1644-60). At the Restoration he returned to Durham as bishop (1660) and rebuilt its liturgical life with new altars, vestments, and choir music — the model for Restoration high-church practice. Died in 1672.",
   overrides={'ecclesiology_worship_polity': 'Reformed-Episcopal'},
   works=['A Collection of Private Devotions (1627)',
          'Historia Transubstantiationis Papalis (1675)'])

_p('john-williams-york', 'John Williams', '1582–1650',
   'Originally named — declined (royalist)',
   'Archbishop of York; Lord Keeper under James I; Laud’s great rival.',
   "Welsh-born, of St John's College Cambridge — where he was later one of the most generous benefactors, the second court is named for him — Williams was Lord Keeper of the Great Seal under James I (1621-25), the last clergyman to hold that office. Bishop of Lincoln from 1621 and finally Archbishop of York from 1641, he was Laud's great rival within the Caroline episcopate: where Laud pressed Arminian sacramentalism, Williams was a moderate Calvinist who defended communion tables in the body of the church against Laud's altar-policy (The Holy Table, Name and Thing, 1637). The Star Chamber imprisoned him in the Tower from 1637 to 1640 on Laud's instigation. Released by the Long Parliament, he was named to the Westminster Assembly but refused to sit out of episcopal loyalty. He retired to Conway Castle in north Wales and died there in March 1650.",
   overrides={'ecclesiology_worship_polity': 'Reformed-Episcopal'},
   works=['The Holy Table, Name and Thing (1637)'])

_p('christopher-cartwright', 'Christopher Cartwright', '1602–1658',
   'Originally named — minimal attendance',
   'York Hebraist and rabbinics scholar; minor royalist sympathies.',
   "Of Peterhouse Cambridge, then a Yorkshire ministry at All Saints North Street York. Cartwright was a learned Hebraist and rabbinics scholar of the same generation as Lightfoot and Selden, though without their public profile — Electa Thargumico-Rabbinica (1648) draws on Targumic and rabbinic sources for biblical exegesis, and Mellificium Hebraicum (posthum. 1660) is a substantial collection of Jewish learning. Named to the Assembly but he attended rarely; his sympathies were moderate-royalist and he opposed both the Erastians and the more aggressive Presbyterian wing. He continued at York through the Commonwealth and died there in 1658.",
   works=['Electa Thargumico-Rabbinica (1648)',
          'Doctrine of Faith Plainly Discovered (1649)',
          'Mellificium Hebraicum (posthum. 1660)'])

