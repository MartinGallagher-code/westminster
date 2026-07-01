"""Map each WCF chapter and each catechism question to the ontology loci.

Each WCF chapter is tagged with one or two locus keys; each LC and SC
question is similarly tagged. The mapping is a manual editorial
assignment based on the chapter/question's primary doctrinal subject.

Usage:

    from .locus_mapping import (
        wcf_chapter_loci, catechism_question_loci,
        wcf_chapters_for_locus, catechism_questions_for_locus,
    )

    wcf_chapter_loci(3)          # → ['god_decree']
    catechism_question_loci('wsc', 1)  # → ['scripture']

    wcf_chapters_for_locus('soteriology')
    # → [9, 10, 11, 12, 14, 15, 17, 18]
"""


# ======================================================================
# WCF chapters → locus keys
#
# Each chapter is assigned one primary locus (and occasionally a
# secondary). The mapping follows the Confession's own internal
# structure as described in data.py's module docstring.
# ======================================================================

WCF_CHAPTER_LOCI = {
    1:  ['scripture'],
    2:  ['god_decree'],
    3:  ['god_decree'],
    4:  ['god_decree'],
    5:  ['god_decree'],
    6:  ['covenant', 'soteriology'],
    7:  ['covenant'],
    8:  ['christology'],
    9:  ['soteriology'],
    10: ['soteriology'],
    11: ['soteriology'],
    12: ['soteriology'],
    13: ['law_sanctification'],
    14: ['soteriology'],
    15: ['soteriology', 'law_sanctification'],
    16: ['law_sanctification'],
    17: ['soteriology'],
    18: ['soteriology'],
    19: ['law_sanctification'],
    20: ['law_sanctification'],
    21: ['ecclesiology_worship'],
    22: ['civil_last_things'],
    23: ['civil_last_things'],
    24: ['civil_last_things'],
    25: ['ecclesiology_worship'],
    26: ['ecclesiology_worship'],
    27: ['ecclesiology_worship'],
    28: ['ecclesiology_worship', 'covenant'],
    29: ['ecclesiology_worship'],
    30: ['ecclesiology_worship'],
    31: ['ecclesiology_worship'],
    32: ['civil_last_things'],
    33: ['civil_last_things'],
}


# ======================================================================
# Westminster Shorter Catechism questions → locus keys
#
# The SC follows a three-part structure:
#   Q1-3:    Prolegomena / Scripture
#   Q4-11:   God, decree, creation, providence
#   Q12-19:  Fall, covenant, Christ the Mediator
#   Q20-28:  Application of redemption (calling, justification,
#            adoption, sanctification)
#   Q29-38:  Benefits in this life and at death / the last things
#   Q39-81:  The moral law (Decalogue exposition)
#   Q82-87:  Faith, repentance, means of grace
#   Q88-107: Prayer, sacraments, the Lord's Prayer
# ======================================================================

WSC_QUESTION_LOCI = {}

# Q1-3: Scripture / prolegomena
for _q in range(1, 4):
    WSC_QUESTION_LOCI[_q] = ['scripture']

# Q4-6: God and Trinity
for _q in range(4, 7):
    WSC_QUESTION_LOCI[_q] = ['god_decree']

# Q7-11: Decree, creation, providence
for _q in range(7, 12):
    WSC_QUESTION_LOCI[_q] = ['god_decree']

# Q12: The fall
WSC_QUESTION_LOCI[12] = ['covenant']

# Q13-16: Sin
for _q in range(13, 17):
    WSC_QUESTION_LOCI[_q] = ['covenant']

# Q17-19: Covenant of grace
for _q in range(17, 20):
    WSC_QUESTION_LOCI[_q] = ['covenant']

# Q20-22: Christ the Mediator
for _q in range(20, 23):
    WSC_QUESTION_LOCI[_q] = ['christology']

# Q23-26: Prophet, priest, king
for _q in range(23, 27):
    WSC_QUESTION_LOCI[_q] = ['christology']

# Q27-28: Humiliation and exaltation
for _q in range(27, 29):
    WSC_QUESTION_LOCI[_q] = ['christology']

# Q29-32: Application of redemption
for _q in range(29, 33):
    WSC_QUESTION_LOCI[_q] = ['soteriology']

# Q33-36: Justification, adoption, sanctification
for _q in range(33, 37):
    WSC_QUESTION_LOCI[_q] = ['soteriology']

# Q37-38: Benefits at death, resurrection
for _q in range(37, 39):
    WSC_QUESTION_LOCI[_q] = ['civil_last_things']

# Q39-81: The moral law (Decalogue exposition)
for _q in range(39, 82):
    WSC_QUESTION_LOCI[_q] = ['law_sanctification']

# Q82-84: Faith, repentance
for _q in range(82, 85):
    WSC_QUESTION_LOCI[_q] = ['soteriology']

# Q85-87: Means of grace (Word, sacraments, prayer)
for _q in range(85, 88):
    WSC_QUESTION_LOCI[_q] = ['ecclesiology_worship']

# Q88-90: Outward means / Word / sacraments
for _q in range(88, 91):
    WSC_QUESTION_LOCI[_q] = ['ecclesiology_worship']

# Q91-93: Sacraments, baptism, Lord's Supper
for _q in range(91, 94):
    WSC_QUESTION_LOCI[_q] = ['ecclesiology_worship']

# Q94-97: Baptism and Lord's Supper
for _q in range(94, 98):
    WSC_QUESTION_LOCI[_q] = ['ecclesiology_worship']

# Q98-107: Prayer and the Lord's Prayer
for _q in range(98, 108):
    WSC_QUESTION_LOCI[_q] = ['ecclesiology_worship']


# ======================================================================
# Westminster Larger Catechism questions → locus keys
#
# The LC follows a similar structure to the SC but at much greater
# length, especially on the Decalogue (Q91-148) and the Lord's Prayer
# (Q178-196).
# ======================================================================

WLC_QUESTION_LOCI = {}

# Q1-5: Prolegomena / Scripture
for _q in range(1, 6):
    WLC_QUESTION_LOCI[_q] = ['scripture']

# Q6-11: God, Trinity, decree
for _q in range(6, 12):
    WLC_QUESTION_LOCI[_q] = ['god_decree']

# Q12-14: Decree, creation
for _q in range(12, 15):
    WLC_QUESTION_LOCI[_q] = ['god_decree']

# Q15-17: Providence, fall
for _q in range(15, 18):
    WLC_QUESTION_LOCI[_q] = ['god_decree']

# Q18-20: Fall, sin
for _q in range(18, 21):
    WLC_QUESTION_LOCI[_q] = ['covenant']

# Q21-29: Sin and its misery
for _q in range(21, 30):
    WLC_QUESTION_LOCI[_q] = ['covenant']

# Q30-35: Covenant of grace
for _q in range(30, 36):
    WLC_QUESTION_LOCI[_q] = ['covenant']

# Q36-42: Christ the Mediator
for _q in range(36, 43):
    WLC_QUESTION_LOCI[_q] = ['christology']

# Q43-50: Humiliation (including Q50: the descent)
for _q in range(43, 51):
    WLC_QUESTION_LOCI[_q] = ['christology']

# Q51-56: Exaltation
for _q in range(51, 57):
    WLC_QUESTION_LOCI[_q] = ['christology']

# Q57-60: Benefits of union with Christ
for _q in range(57, 61):
    WLC_QUESTION_LOCI[_q] = ['soteriology']

# Q61-65: Justification
for _q in range(61, 66):
    WLC_QUESTION_LOCI[_q] = ['soteriology']

# Q66-69: Adoption, sanctification
for _q in range(66, 70):
    WLC_QUESTION_LOCI[_q] = ['soteriology']

# Q70-73: Justification (continued)
for _q in range(70, 74):
    WLC_QUESTION_LOCI[_q] = ['soteriology']

# Q74-78: Faith, repentance
for _q in range(74, 79):
    WLC_QUESTION_LOCI[_q] = ['soteriology']

# Q79-81: Perseverance, assurance
for _q in range(79, 82):
    WLC_QUESTION_LOCI[_q] = ['soteriology']

# Q82-85: Communion in glory / death / resurrection
for _q in range(82, 86):
    WLC_QUESTION_LOCI[_q] = ['civil_last_things']

# Q86-90: What is duty / the moral law
for _q in range(86, 91):
    WLC_QUESTION_LOCI[_q] = ['law_sanctification']

# Q91-148: The Ten Commandments exposition (the LC's longest section)
for _q in range(91, 149):
    WLC_QUESTION_LOCI[_q] = ['law_sanctification']

# Q149-152: Sin, aggravations of sin
for _q in range(149, 153):
    WLC_QUESTION_LOCI[_q] = ['law_sanctification']

# Q153-160: Means of grace, Word, sacraments
for _q in range(153, 161):
    WLC_QUESTION_LOCI[_q] = ['ecclesiology_worship']

# Q161-167: Baptism
for _q in range(161, 168):
    WLC_QUESTION_LOCI[_q] = ['ecclesiology_worship']

# Q168-177: Lord's Supper
for _q in range(168, 178):
    WLC_QUESTION_LOCI[_q] = ['ecclesiology_worship']

# Q178-196: Prayer and the Lord's Prayer
for _q in range(178, 197):
    WLC_QUESTION_LOCI[_q] = ['ecclesiology_worship']


# ======================================================================
# Lookup functions
# ======================================================================

def wcf_chapter_loci(chapter_number):
    """Return the locus key(s) for a WCF chapter."""
    return WCF_CHAPTER_LOCI.get(chapter_number, [])


def catechism_question_loci(catechism_slug, question_number):
    """Return the locus key(s) for a catechism question."""
    if catechism_slug == 'wsc':
        return WSC_QUESTION_LOCI.get(question_number, [])
    if catechism_slug == 'wlc':
        return WLC_QUESTION_LOCI.get(question_number, [])
    return []


# ======================================================================
# DPW sections → locus keys
# ======================================================================

DPW_SECTION_LOCI = {
    1:  ['ecclesiology_worship'],      # Assembling of the Congregation
    2:  ['scripture'],                  # Public Reading of Holy Scriptures
    3:  ['ecclesiology_worship'],      # Public Prayer before the Sermon
    4:  ['ecclesiology_worship'],      # Preaching of the Word
    5:  ['ecclesiology_worship'],      # Prayer after the Sermon
    6:  ['ecclesiology_worship'],      # Administration of Baptism
    7:  ['ecclesiology_worship'],      # Lord's Supper
    8:  ['law_sanctification'],        # Sanctification of the Lord's Day
    9:  ['civil_last_things'],         # Solemnization of Marriage
    10: ['ecclesiology_worship'],      # Visitation of the Sick
    11: ['civil_last_things'],         # Burial of the Dead
    12: ['ecclesiology_worship'],      # Public Solemn Fasting
    13: ['ecclesiology_worship'],      # Days of Public Thanksgiving
    14: ['ecclesiology_worship'],      # Singing of Psalms
    15: ['ecclesiology_worship'],      # Appendix: Days and Places
}

# ======================================================================
# FPCG sections → locus keys
# ======================================================================

FPCG_SECTION_LOCI = {
    1:  ['ecclesiology_worship'],      # Preface
    2:  ['ecclesiology_worship'],      # Of the Church
    3:  ['ecclesiology_worship'],      # Of the Officers of the Church
    4:  ['ecclesiology_worship'],      # Pastors
    5:  ['ecclesiology_worship'],      # Teacher or Doctor
    6:  ['ecclesiology_worship'],      # Other Church-Governors (Elders)
    7:  ['ecclesiology_worship'],      # Deacons
    8:  ['ecclesiology_worship'],      # Of Particular Congregations
    9:  ['ecclesiology_worship'],      # Officers of a particular Congregation
    10: ['ecclesiology_worship'],      # Ordinances in a particular Congregation
    11: ['ecclesiology_worship'],      # Church-Government and Assemblies
    12: ['ecclesiology_worship'],      # Power in common of all Assemblies
    13: ['ecclesiology_worship'],      # Congregational Assemblies
    14: ['ecclesiology_worship'],      # Classical Assemblies
    15: ['ecclesiology_worship'],      # Synodical Assemblies
    16: ['ecclesiology_worship'],      # Of Ordination of Ministers
    17: ['ecclesiology_worship'],      # Doctrine of Ordination
    18: ['ecclesiology_worship'],      # Power of Ordination
    19: ['ecclesiology_worship'],      # Directory for Ordination
}

# ======================================================================
# SSK sections → locus keys
# ======================================================================

SSK_SECTION_LOCI = {
    1:  ['covenant'],                  # Head I: woeful condition / covenant of works
    2:  ['christology', 'covenant'],   # Head II: remedy in Christ / covenant of grace
    3:  ['ecclesiology_worship'],      # Head III: outward means
    4:  ['soteriology'],               # Head IV: blessings conveyed
    5:  ['law_sanctification'],        # Practical Use: convincing by the law
    6:  ['soteriology'],               # Practical Use: convincing by the gospel
    7:  ['soteriology'],               # Warrants: God's hearty invitation
    8:  ['soteriology'],               # Warrants: God's earnest request
    9:  ['soteriology'],               # Warrants: God's command
    10: ['soteriology'],               # Warrants: assurance of life
    11: ['law_sanctification'],        # Evidences: obligation to moral law
    12: ['law_sanctification'],        # Evidences: practise godliness
    13: ['soteriology'],               # Evidences: obedience through faith
    14: ['soteriology'],               # Evidences: communion with Christ
}


def directory_section_loci(work_slug, section_number):
    """Return the locus key(s) for a DPW/FPCG/SSK section."""
    if work_slug == 'dpw':
        return DPW_SECTION_LOCI.get(section_number, [])
    if work_slug == 'fpcg':
        return FPCG_SECTION_LOCI.get(section_number, [])
    if work_slug == 'ssk':
        return SSK_SECTION_LOCI.get(section_number, [])
    return []


def directory_sections_for_locus(work_slug, locus_key):
    """Return the section numbers that fall under a given locus."""
    if work_slug == 'dpw':
        mapping = DPW_SECTION_LOCI
    elif work_slug == 'fpcg':
        mapping = FPCG_SECTION_LOCI
    elif work_slug == 'ssk':
        mapping = SSK_SECTION_LOCI
    else:
        return []
    return sorted(s for s, loci in mapping.items() if locus_key in loci)


def wcf_chapters_for_locus(locus_key):
    """Return the WCF chapter numbers that fall under a given locus."""
    return sorted(ch for ch, loci in WCF_CHAPTER_LOCI.items()
                  if locus_key in loci)


def catechism_questions_for_locus(catechism_slug, locus_key):
    """Return the question numbers that fall under a given locus."""
    if catechism_slug == 'wsc':
        mapping = WSC_QUESTION_LOCI
    elif catechism_slug == 'wlc':
        mapping = WLC_QUESTION_LOCI
    else:
        return []
    return sorted(q for q, loci in mapping.items() if locus_key in loci)
