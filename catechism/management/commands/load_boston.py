import re

from django.conf import settings
from django.core.management.base import BaseCommand

from catechism.models import Catechism, Commentary, CommentarySource, Question


# Mapping of section search strings to WSC question number(s).
# Each tuple is (search_string, [question_numbers]).
# Sections with an empty list are supplementary sermons to skip.
SECTION_MAP = [
    # Q1: What is the chief end of man?
    ("OF MAN'S CHIEF END AND HAPPINESS", [1]),
    # Q2: What rule hath God given to direct us...
    ("THE DIVINE AUTHORITY OF THE", [2]),
    ("THE UTILITY OF THE SCRIPTURES AS A", [2]),
    # Q3: What do the Scriptures principally teach?
    ("THE SCOPE OF THE SCRIPTURES", [3]),
    # Supplementary sermon on Scripture study (appended to Q3)
    ("THE SCRIPTURES THE BOOK OF THE LORD", [3]),
    # Q4: What is God?
    ("OF GOD AND HIS PERFECTIONS", [4]),
    # Q5: Are there more Gods than one?
    ("OF THE UNITY OF GOD", [5]),
    # Q6: How many persons are there in the Godhead?
    ("OF THE HOLY TRINITY", [6]),
    # Q7: What are the decrees of God?
    ("OF THE DECREES OF GOD", [7]),
    # Q8: How doth God execute his decrees?
    # Q9: What is the work of creation?
    ("OF THE WORK OF CREATION", [8, 9]),
    # Q10: How did God create man?
    ("OF THE CREATION OF MAN", [10]),
    # Q11: What are God's works of providence?
    ("OF THE PROVIDENCE OF GOD", [11]),
    # Supplementary sermon on providence (appended to Q11)
    ("THE WISE OBSERVATION OF PROVIDENCES", [11]),
    # Q12: What special act of providence...
    ("OF THE COVENANT OF WORKS", [12]),
    # Q13: Did our first parents continue...
    ("OF THE FALL OF OUR FIRST PARENTS", [13]),
    # Q14: What is sin?
    ("OF SIN IN GENERAL", [14]),
    # Q15: What was the sin whereby our first parents fell...
    ("OF THE FIRST SIN IN PARTICULAR", [15]),
    # Q16: Did all mankind fall in Adam's first transgression?
    ("OF OUR FALL IN ADAM", [16]),
    # Q17-Q18: Into what estate did the fall bring mankind? / Sinfulness
    ("OF THE SINFULNESS OF MAN", [17, 18]),
    # Q19: What is the misery of that estate...
    ("OF THE MISERY OF MAN", [19]),
    # Q20: Did God leave all mankind to perish...
    ("OF ELECTION TO EVERLASTING LIFE", [20]),
    # Q20 continued: Covenant of grace
    ("OF THE COVENANT OF GRACE", [20]),
    # Q21: Who is the Redeemer of God's elect?
    ("OF CHRIST THE ONLY REDEEMER", [21]),
    # Q22: How did Christ become man?
    ("OF CHRIST'S INCARNATION", [22]),
    # Q23: What offices doth Christ execute as our Redeemer?
    ("OF CHRIST'S OFFICES IN GENERAL", [23]),
    # Q24: How doth Christ execute the office of a prophet?
    ("OF CHRIST'S PROPHETICAL OFFICE", [24]),
    # Q25: How doth Christ execute the office of a priest?
    ("OF CHRIST'S PRIESTLY OFFICE", [25]),
    # Q25 continued: Intercession
    ("OF CHRIST'S INTERCESSION", [25]),
    # Q26: How doth Christ execute the office of a king?
    ("OF CHRIST'S KINGLY OFFICE", [26]),
    # Q27: Wherein did Christ's humiliation consist?
    ("OF CHRIST'S HUMILIATION", [27]),
    # Q28: Wherein consisteth Christ's exaltation?
    ("OF CHRIST'S EXALTATION", [28]),
    # Q29: How are we made partakers of the redemption...
    ("OF THE APPLICATION OF REDEMPTION", [29]),
    # Q30: How doth the Spirit apply...
    ("OF UNION WITH CHRIST", [30]),
    # Q31: What is effectual calling?
    ("OF EFFECTUAL CALLING", [31]),
    # Q32: What benefits do they that are effectually called partake of...
    ("OF THE BENEFITS OF EFFECTUAL", [32]),
    # Q33: What is justification? (runs up to ADOPTION sub-header)
    ("OF JUSTIFICATION", [33]),
    # Note: Q34 (adoption) handled specially below via ADOPTION sub-header
    # Supplementary sermon on adoption (appended to Q34)
    ("THE DIVINE CALL TO LEAVE THE DEVIL", [34]),
    # Q35: What is sanctification?
    ("OF SANCTIFICATION", [35]),
    # Supplementary on sanctification (appended to Q35)
    ("UNION WITH CHRIST THE ONLY WAY", [35]),
    # Q36: What are the benefits which in this life do accompany or flow from...
    ("OF THE BENEFITS FLOWING FROM", [36]),
    # Q36 sub-sections (these are subsections within the Q36 text, not separate top-level headers)
    # They'll be found between BENEFITS FLOWING and the next major section
    # Q37: What benefits do believers receive from Christ at death?
    ("OF THE BENEFITS WHICH BELIEVERS RECEIVE AT DEATH", [37]),
    # Q38: What benefits do believers receive from Christ at the resurrection?
    ("OF BENEFITS AT THE RESURRECTION", [38]),
    # Q39: What is the duty which God requireth of man?
    ("OF THE DUTY WHICH GOD REQUIRETH", [39]),
    # Q40: What did God at first reveal to man for the rule of his obedience?
    ("THE MORAL LAW, THE RULE OF MAN", [40]),
    # Q41: Where is the moral law summarily comprehended?
    ("THE MORAL LAW SUMMARILY COMPREHENDED", [41]),
    # Q42: What is the sum of the ten commandments?
    ("LOVE TO GOD AND OUR NEIGHBOUR", [42]),
    # Q43: What is the preface to the ten commandments?
    ("THE PREFACE TO THE TEN COMMANDMENTS", [43]),
    # Q44-Q46: First commandment (required, forbidden, "before me")
    ("OF THE FIRST COMMANDMENT", [44, 45, 46]),
    # Q47-Q48: Second commandment
    ("OF THE SECOND COMMANDMENT", [47, 48]),
    # Supplementary sermon (skip)
    ("PRAYER AGAINST THE ANTICH", []),
    # Q49-Q52: Third commandment
    ("OF THE THIRD COMMANDMENT", [49, 50, 51, 52]),
    # Q53-Q56: Fourth commandment (Sabbath)
    ("OF THE FOURTH COMMANDMENT", [53, 54, 55, 56]),
    # Q57-Q66: Fifth commandment (duties of various relations)
    ("OF THE FIFTH COMMANDMENT", [57, 58, 59, 60, 61, 62, 63, 64, 65, 66]),
    # Supplementary on ruling elders (appended to Q64)
    ("THE DUTY OF RULING ELDERS", [64]),
    # Q67-Q69: Sixth commandment
    ("OF THE SIXTH COMMANDMENT", [67, 68, 69]),
    # Q70-Q72: Seventh commandment
    ("OF THE SEVENTH COMMANDMENT", [70, 71, 72]),
    # Q73-Q75: Eighth commandment
    ("OF THE EIGHTH COMMANDMENT", [73, 74, 75]),
    # Q76-Q78: Ninth commandment
    ("OF THE NINTH COMMANDMENT", [76, 77, 78]),
    # Q79-Q81: Tenth commandment
    ("OF THE TENTH COMMANDMENT", [79, 80, 81]),
    # Q82: Is any man able perfectly to keep the commandments of God?
    ("OF MAN'S INABILITY TO KEEP", [82]),
    # Q83: Are all transgressions equally heinous?
    ("OF SIN IN ITS AGGRAVATIONS", [83]),
    # Q84: What doth every sin deserve?
    ("OF THE DESERT OF SIN", [84]),
    # Q85: What doth God require of us, that we may escape his wrath...
    ("OF THE MEANS OF SALVATION IN", [85]),
    # Q86: What is faith in Jesus Christ?
    ("OF FAITH IN JESUS CHRIST", [86]),
    # Q87: What is repentance unto life?
    ("OF REPENTANCE UNTO LIFE", [87]),
    # Q88: What are the outward means...
    ("OF CHRIST'S ORDINANCES IN", [88]),
    # Q89: How is the word made effectual to salvation?
    ("HOW THE WORD IS MADE EFFECTUAL", [89]),
    # Q90: How is the word to be read and heard?
    ("HOW THE WORD IS TO BE READ", [90]),
    # Supplementary sermons on ordinances (appended to Q90)
    ("THE DUTY OF ATTENDING", [90]),
    ("A CAVEAT AGAINST RECEIVING", [90]),
    ("THE DANGER OF NOT COMPLYING", [90]),
    # Q91: How do the sacraments become effectual means of salvation?
    ("HOW THE SACRAMENTS BECOME", [91]),
    # Q92: What is a sacrament?
    ("THE NATURE OF THE SACRAMENTS", [92]),
    # Q93-Q95: Sacraments of NT, baptism, to whom administered
    ("THE NUMBER OF THE SACRAMENTS", [93, 94, 95]),
    # Q96: What is the Lord's supper?
    ("OF THE LORD'S SUPPER", [96]),
    # Q97: What is required to the worthy receiving...
    ("OF THE WORTHY RECEIVING", [97]),
    # Supplementary on self-examination (appended to Q97)
    ("THE NECESSITY OF SELF", [97]),
    # Supplementary on unworthy communicating (appended to Q97)
    ("THE DANGER OF UNWORTHY", [97]),
    # Q98: What is prayer?
    ("THE NATURE OF PRAYER", [98]),
    # Supplementary on secret prayer (appended to Q98)
    ("A DISCOURSE ON SECRET PRAYER", [98]),
    # Q99: What rule hath God given for our direction in prayer?
    ("OF THE RULE OF DIRECTION IN PRAYER", [99]),
    # Q100: What doth the preface of the Lord's prayer teach us?
    ("THE PREFACE OF THE LORD'S PRAYER", [100]),
    # Q101: What do we pray for in the first petition?
    ("THE FIRST PETITION", [101]),
    # Q102: What do we pray for in the second petition?
    ("THE SECOND PETITION", [102]),
    # Q103: What do we pray for in the third petition?
    ("THE THIRD PETITION", [103]),
    # Q104: What do we pray for in the fourth petition?
    ("THE FOURTH PETITION", [104]),
    # Q105: What do we pray for in the fifth petition?
    ("THE FIFTH PETITION", [105]),
    # Q106: What do we pray for in the sixth petition?
    ("THE SIXTH PETITION", [106]),
    # Q107: What doth the conclusion of the Lord's prayer teach us?
    ("THE CONCLUSION OF THE LORD'S PRAYER", [107]),
]

# Sections at the end that are not part of the catechism exposition
END_MARKERS = [
    "A DISCOURSE ON THE EXPERIMENTAL KNOWLEDGE",
    "THE RIGHT IMPROVEMENT OF A TIME",
]


def clean_text(text):
    """Clean up extracted PDF text."""
    # Normalize whitespace within lines
    text = re.sub(r'[ \t]+', ' ', text)

    # Remove page break artifacts
    text = text.replace('\x0c', '\n')

    # Collapse 4+ blank lines into 2
    text = re.sub(r'\n{4,}', '\n\n\n', text)

    # Strip each line
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)

    # Remove lines that are only page numbers
    text = re.sub(r'\n\d{1,4}\n', '\n', text)

    return text.strip()


class Command(BaseCommand):
    help = "Load Thomas Boston's Exposition of the WSC from PDF"

    def handle(self, *args, **options):
        catechism = Catechism.objects.get(slug='wsc')
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            self.stderr.write(self.style.ERROR(
                "PyPDF2 is required. Install it with: pip3 install PyPDF2"
            ))
            return

        source, _ = CommentarySource.objects.update_or_create(
            slug="boston",
            defaults={
                "name": "An Exposition of the Assembly's Shorter Catechism",
                "author": "Thomas Boston",
                "year": 1773,
                "description": (
                    "A comprehensive exposition originally delivered as sermons, "
                    "covering all 107 questions with thorough doctrinal and "
                    "practical applications."
                ),
            },
        )

        pdf_path = settings.BASE_DIR / "data" / "boston_wsc.pdf"
        if not pdf_path.exists():
            self.stderr.write(self.style.ERROR(
                f"PDF not found: {pdf_path}"
            ))
            return

        self.stdout.write(f"Reading PDF: {pdf_path}")
        reader = PdfReader(str(pdf_path))
        full_text = ""
        for page in reader.pages:
            text = page.extract_text() or ""
            full_text += text + "\n"

        self.stdout.write(
            f"Extracted {len(full_text)} characters from "
            f"{len(reader.pages)} pages"
        )

        # Determine where body text starts (after table of contents).
        # The TOC contains the same headers as the body. We find the body
        # start by locating the first section header followed by a Bible
        # verse citation (the TOC has headers back-to-back without verses).
        body_start = self._find_body_start(full_text)
        self.stdout.write(f"Body text starts at position {body_start}")

        # Find all section positions in the body text
        sections = self._find_sections(full_text, body_start)

        if not sections:
            self.stderr.write(self.style.ERROR("No sections found in PDF text."))
            return

        self.stdout.write(f"Found {len(sections)} mapped sections")

        # Extract text for each question
        question_texts = self._extract_question_texts(full_text, sections)

        # Handle Q33/Q34 split: ADOPTION is a sub-header within the
        # JUSTIFICATION section
        self._split_justification_adoption(full_text, question_texts)

        # Load into database
        loaded = 0
        for num in sorted(question_texts.keys()):
            text = clean_text(question_texts[num])
            if not text:
                self.stderr.write(self.style.WARNING(
                    f"  Q{num}: empty text, skipping"
                ))
                continue

            try:
                question = Question.objects.get(catechism=catechism, number=num)
            except Question.DoesNotExist:
                self.stderr.write(self.style.WARNING(
                    f"  Q{num}: Question not found in database, skipping"
                ))
                continue

            Commentary.objects.update_or_create(
                question=question,
                source=source,
                defaults={"body": text},
            )
            loaded += 1
            self.stdout.write(f"  Q{num}: loaded ({len(text)} chars)")

        self.stdout.write(self.style.SUCCESS(
            f"Loaded Boston commentary for {loaded} questions"
        ))

    def _find_body_start(self, full_text):
        """
        Find where the body text begins (after the table of contents).

        The first body section is "OF MAN'S CHIEF END AND HAPPINESS"
        followed by a Bible verse citation. In the TOC, headers appear
        back-to-back without verse citations.
        """
        first_header = "OF MAN'S CHIEF END AND HAPPINESS"
        pos = full_text.find(first_header)
        if pos < 0:
            # Try with curly apostrophe
            first_header_alt = "OF MAN\u2019S CHIEF END AND HAPPINESS"
            pos = full_text.find(first_header_alt)

        if pos < 0:
            return 0

        # Find the second occurrence (body text, not TOC)
        second = full_text.find("OF MAN", pos + len(first_header))
        # Verify it's the same header by checking nearby text
        while second >= 0:
            snippet = full_text[second:second + 200]
            if "CHIEF END" in snippet and "COR" in snippet:
                return second
            second = full_text.find("OF MAN", second + 10)

        # Fallback: look for the pattern of header + Bible verse
        return pos

    def _find_sections(self, full_text, body_start):
        """Find positions of all mapped sections in the body text."""
        sections = []  # list of (position, question_numbers, label)

        for search_str, q_nums in SECTION_MAP:
            # Search only in body text (after TOC)
            found_pos = self._search_in_body(
                full_text, search_str, body_start
            )
            if found_pos >= 0:
                sections.append((found_pos, q_nums, search_str))
            else:
                if q_nums:
                    self.stderr.write(self.style.WARNING(
                        f"  Section not found: '{search_str}' "
                        f"(Q{q_nums})"
                    ))

        # Add end marker to bound the last catechism section
        for end_str in END_MARKERS:
            pos = full_text.find(end_str, body_start)
            if pos >= 0:
                sections.append((pos, [], "END"))
                break

        # Sort by position
        sections.sort(key=lambda x: x[0])

        return sections

    def _search_in_body(self, full_text, search_str, body_start):
        """
        Search for a section header in the body text.

        Handles multi-line headers (line breaks within the header text)
        and apostrophe variants.
        """
        # Build variants with different apostrophes
        variants = [search_str]
        if "\u2019" in search_str:
            variants.append(search_str.replace("\u2019", "'"))
        if "'" in search_str:
            variants.append(search_str.replace("'", "\u2019"))

        for variant in variants:
            # Direct search
            pos = full_text.find(variant, body_start)
            if pos >= 0:
                return pos

            # Try with flexible whitespace (headers may span multiple lines)
            words = variant.split()
            if len(words) >= 3:
                pattern = r'\s+'.join(re.escape(w) for w in words)
                m = re.search(pattern, full_text[body_start:])
                if m:
                    return body_start + m.start()

        return -1

    def _extract_question_texts(self, full_text, sections):
        """Extract text between section boundaries and assign to questions."""
        question_texts = {}  # {question_number: text}

        for i, (pos, q_nums, label) in enumerate(sections):
            if not q_nums:
                continue

            # Find end of this section (start of next section)
            if i + 1 < len(sections):
                end_pos = sections[i + 1][0]
            else:
                end_pos = len(full_text)

            section_text = full_text[pos:end_pos]

            # Assign to each mapped question
            for q_num in q_nums:
                if q_num in question_texts:
                    question_texts[q_num] += "\n\n" + section_text
                else:
                    question_texts[q_num] = section_text

        return question_texts

    def _split_justification_adoption(self, full_text, question_texts):
        """
        Split Q33 (Justification) and Q34 (Adoption).

        In Boston's text, ADOPTION is a sub-header within the larger
        OF JUSTIFICATION section.
        """
        if 33 not in question_texts:
            return

        q33_text = question_texts[33]

        # The ADOPTION sub-header appears on its own line, typically
        # preceded by a blank line and followed by a Bible reference.
        adoption_match = re.search(
            r'\n\s*\n\s*ADOPTION\s*\n',
            q33_text,
        )

        if adoption_match:
            split_pos = adoption_match.start()
            adoption_text = q33_text[split_pos:]
            justification_text = q33_text[:split_pos]
            question_texts[33] = justification_text

            # Q34 may already have text from DIVINE CALL section
            if 34 in question_texts:
                question_texts[34] = adoption_text + "\n\n" + question_texts[34]
            else:
                question_texts[34] = adoption_text

            self.stdout.write("  Split Q33/Q34 at ADOPTION sub-header")
        else:
            self.stderr.write(self.style.WARNING(
                "  Could not find ADOPTION sub-header within Q33 text. "
                "Q34 may be incomplete."
            ))
