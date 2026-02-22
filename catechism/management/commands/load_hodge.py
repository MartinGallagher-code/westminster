import re

from django.conf import settings
from django.core.management.base import BaseCommand

from catechism.models import Catechism, Commentary, CommentarySource, Question


# Chapter number -> (first global section number, last global section number)
WCF_CHAPTER_SECTIONS = {
    1: (1, 10), 2: (11, 13), 3: (14, 21), 4: (22, 23), 5: (24, 30),
    6: (31, 36), 7: (37, 42), 8: (43, 50), 9: (51, 55), 10: (56, 59),
    11: (60, 65), 12: (66, 66), 13: (67, 69), 14: (70, 72), 15: (73, 78),
    16: (79, 85), 17: (86, 88), 18: (89, 92), 19: (93, 99), 20: (100, 103),
    21: (104, 111), 22: (112, 118), 23: (119, 122), 24: (123, 128),
    25: (129, 134), 26: (135, 137), 27: (138, 142), 28: (143, 149),
    29: (150, 157), 30: (158, 161), 31: (162, 166), 32: (167, 169),
    33: (170, 172),
}

# WCF chapter titles used to find the start of actual content (after intro chapters)
WCF_CHAPTER_TITLES = {
    1: "HOLY SCRIPTURE",
    2: "GOD AND",
    3: "ETERNAL DECREE",
    4: "CREATION",
    5: "PROVIDENCE",
}

ROMAN_VALUES = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}


def fix_ocr_roman(s):
    """Fix common OCR substitutions in Roman numerals."""
    s = s.strip()
    # Remove spaces within the numeral (e.g. "I  Y" -> "IY")
    s = re.sub(r'\s+', '', s)
    # Digit 1 → I
    s = s.replace('1', 'I')
    # Lowercase l → I (before uppercasing)
    s = s.replace('l', 'I')
    s = s.upper()
    s = s.replace('Y', 'V')
    s = s.replace('T', 'I')
    # Standalone L that's not after X is usually I (e.g. "Section L" = "Section I")
    if s == 'L':
        s = 'I'
    elif s.endswith('L') and len(s) > 1 and s[-2] != 'X':
        s = s[:-1] + 'I'
    return s


def roman_to_int(s):
    s = fix_ocr_roman(s)
    total = 0
    prev = 0
    for c in reversed(s):
        val = ROMAN_VALUES.get(c, 0)
        if val < prev:
            total -= val
        else:
            total += val
        prev = val
    return total


def clean_text(text):
    """Clean OCR text from Internet Archive DjVu extraction."""
    text = re.sub(r'_', '', text)
    # Remove page headers (e.g. "70", "GOD AND THE HOLY TRINITY.  71")
    text = re.sub(r'^\s*\d{1,3}\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\s+CONFESSION\s+OF\s+FAITH\.\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[A-Z][A-Z\s,]+\.\s+\d+\s*$', '', text, flags=re.MULTILINE)
    # Fix hyphenated line breaks
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
    # Collapse multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    # Unwrap paragraphs
    paragraphs = re.split(r'\n\s*\n', text)
    unwrapped = []
    for para in paragraphs:
        joined = re.sub(r'\s*\n\s*', ' ', para).strip()
        if joined:
            unwrapped.append(joined)
    return '\n\n'.join(unwrapped).strip()


class Command(BaseCommand):
    help = "Load A.A. Hodge's Commentary on the Westminster Confession of Faith"

    def handle(self, *args, **options):
        catechism = Catechism.objects.get(slug='wcf')

        source, _ = CommentarySource.objects.update_or_create(
            slug="hodge",
            defaults={
                "name": "A Commentary on the Confession of Faith",
                "author": "A.A. Hodge",
                "year": 1869,
                "description": (
                    "A systematic commentary on the Westminster Confession "
                    "with questions for theological students and Bible classes."
                ),
            },
        )

        filepath = settings.BASE_DIR / "data" / "hodge_wcf.txt"
        if not filepath.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {filepath}"))
            return

        full_text = filepath.read_text(encoding="utf-8", errors="replace")

        # Find start of actual WCF commentary (after intro chapters).
        # Look for "Confession of Faith" followed by "CHAPTER" and "HOLY SCRIPTURE"
        content_start = self._find_content_start(full_text)
        if content_start is None:
            self.stderr.write(self.style.ERROR("Could not find start of WCF commentary"))
            return

        full_text = full_text[content_start:]
        self.stdout.write(f"Content starts at offset {content_start}")

        # Find chapter boundaries (handle OCR: CHAPTEK, CHAPTEH, CHAPTEE, etc.)
        chapter_pattern = re.compile(
            r'^CHAPT[A-Za-z]{1,2}\s+([IVXLCYTl]+[.,]?)\s*$',
            re.MULTILINE
        )
        chapter_positions = []
        for m in chapter_pattern.finditer(full_text):
            roman = re.sub(r'[.,]', '', m.group(1))
            num = roman_to_int(roman)
            if 1 <= num <= 33:
                chapter_positions.append((m.start(), num))

        # Deduplicate - keep first occurrence of each chapter
        seen_chapters = set()
        unique_chapters = []
        for pos, num in chapter_positions:
            if num not in seen_chapters:
                seen_chapters.add(num)
                unique_chapters.append((pos, num))
        chapter_positions = unique_chapters

        self.stdout.write(f"Found {len(chapter_positions)} chapters")

        loaded = 0
        skipped = 0

        for i, (ch_start, ch_num) in enumerate(chapter_positions):
            if ch_num not in WCF_CHAPTER_SECTIONS:
                continue

            ch_end = chapter_positions[i + 1][0] if i + 1 < len(chapter_positions) else len(full_text)
            chapter_text = full_text[ch_start:ch_end]

            section_start, section_end = WCF_CHAPTER_SECTIONS[ch_num]
            result = self._parse_chapter_sections(chapter_text, ch_num, section_start)

            if not result:
                # Fallback: find commentary start and assign to all sections
                commentary_match = re.search(
                    r'(?:This|These)\s+(?:section|chapter)', chapter_text, re.IGNORECASE
                )
                body_start = commentary_match.start() if commentary_match else None

                # For single-section chapters without explicit markers,
                # look for the first paragraph break after initial WCF text
                if body_start is None and section_start == section_end:
                    para_match = re.search(r'\n\s*\n\s*[A-Z][a-z]', chapter_text[200:])
                    if para_match:
                        body_start = para_match.start() + 200

                if body_start is not None:
                    body = clean_text(chapter_text[body_start:])
                    if body and len(body) >= 50:
                        for sec_num in range(section_start, section_end + 1):
                            try:
                                q = Question.objects.get(catechism=catechism, number=sec_num)
                                Commentary.objects.update_or_create(
                                    question=q, source=source, defaults={"body": body}
                                )
                                loaded += 1
                            except Question.DoesNotExist:
                                skipped += 1
                        self.stdout.write(
                            f"  Ch {ch_num}: fallback - assigned to "
                            f"§{section_start}-{section_end}"
                        )
                continue

            # Fill gaps: if sections in the expected range are missing,
            # assign the nearest available section's commentary
            for sec_num in range(section_start, section_end + 1):
                if sec_num not in result:
                    # Find nearest section that has commentary
                    nearest = min(
                        result.keys(),
                        key=lambda k: abs(k - sec_num),
                        default=None,
                    )
                    if nearest is not None:
                        result[sec_num] = result[nearest]

            for global_section_num, body in result.items():
                body = clean_text(body)
                if not body or len(body) < 50:
                    skipped += 1
                    continue
                try:
                    q = Question.objects.get(catechism=catechism, number=global_section_num)
                    Commentary.objects.update_or_create(
                        question=q, source=source, defaults={"body": body}
                    )
                    loaded += 1
                except Question.DoesNotExist:
                    self.stderr.write(self.style.WARNING(
                        f"  §{global_section_num}: not found in database"
                    ))
                    skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"Loaded Hodge commentary for {loaded} sections ({skipped} skipped)"
        ))

    def _find_content_start(self, text):
        """Find where the actual WCF commentary begins (after intro chapters)."""
        # Look for "Confession of Faith" near a "CHAPTER" with "HOLY SCRIPTURE"
        # The actual content has: "Confession of Faith." then "CHAPTER  I,"
        # then "OF THE HOLY SCRIPTURE"
        pattern = re.compile(
            r'Confession\s+of\s+Faith\.\s*\n+\s*CHAPTER\s+I[.,]',
            re.IGNORECASE
        )
        matches = list(pattern.finditer(text))
        if matches:
            # Use the last match that's followed by "HOLY SCRIPTURE"
            for m in reversed(matches):
                after = text[m.start():m.start() + 500]
                if 'HOLY' in after and 'SCRIPTURE' in after:
                    return m.start()
            return matches[-1].start()
        return None

    def _parse_chapter_sections(self, chapter_text, ch_num, section_start):
        """
        Parse a chapter's text into section-level commentary blocks.

        Hodge's pattern:
        - Section I. — [WCF text]
        - [proof texts]
        - "This section teaches/affirms..." or "These sections teach..."
        - [Hodge's commentary]
        - Optional "Questions" section at the end

        Sometimes multiple sections share one commentary block.
        Returns dict of {global_section_number: commentary_text}.
        """
        # Handle OCR variants: "Section", "8ection", "ii^ECTiON"
        section_pattern = re.compile(
            r'(?:Section|8ection|ii\^ECTiON)\s+([IVXLCYTl1]+)\s*[.,]?\s*[-—]?'
        )
        # Commentary start patterns — match various Hodge intro styles:
        # "This section teaches...", "These Sections briefly state...",
        # "This Chapter teaches...", "These Sections proceed to..."
        commentary_pattern = re.compile(
            r'(?:This|These)\s+(?:section|chapter)[s]?\s+'
            r'(?:\w+\s+)?'  # optional adverb (e.g., "briefly")
            r'(?:teach|affirm|assert|declare|state|define|treat|proceed)',
            re.IGNORECASE
        )

        # Build markers list
        markers = []
        for m in section_pattern.finditer(chapter_text):
            local_num = roman_to_int(m.group(1))
            markers.append(('section', m.start(), local_num))

        for m in commentary_pattern.finditer(chapter_text):
            markers.append(('commentary', m.start(), m.start()))

        markers.sort(key=lambda x: x[1])

        if not markers:
            return None

        result = {}
        pending_sections = []

        for j, marker in enumerate(markers):
            if marker[0] == 'section':
                pending_sections.append(marker[2])
            elif marker[0] == 'commentary':
                if pending_sections:
                    # Find end of commentary: next section marker or end of chapter
                    commentary_end = len(chapter_text)
                    for k in range(j + 1, len(markers)):
                        if markers[k][0] == 'section':
                            commentary_end = markers[k][1]
                            break

                    commentary_text = chapter_text[marker[2]:commentary_end]

                    # Strip trailing "Questions" review section
                    q_match = re.search(
                        r'\n\s*(?:QUESTIONS|Questions)\s*\.?\s*\n',
                        commentary_text
                    )
                    if q_match:
                        commentary_text = commentary_text[:q_match.start()]

                    for local_num in pending_sections:
                        global_num = section_start + (local_num - 1)
                        result[global_num] = commentary_text

                    pending_sections = []

        # Handle remaining pending sections (no commentary marker followed them).
        # Assign text from last commentary marker to end of chapter.
        if pending_sections:
            # Find the last commentary marker position
            last_commentary_end = 0
            for marker in reversed(markers):
                if marker[0] == 'commentary':
                    last_commentary_end = marker[1]
                    break

            # Use text from the first pending section to end of chapter
            first_pending_pos = None
            for marker in markers:
                if marker[0] == 'section' and marker[2] == pending_sections[0]:
                    first_pending_pos = marker[1]
                    break

            if first_pending_pos is not None:
                commentary_text = chapter_text[first_pending_pos:]
                q_match = re.search(
                    r'\n\s*(?:QUESTIONS|Questions)\s*\.?\s*\n',
                    commentary_text
                )
                if q_match:
                    commentary_text = commentary_text[:q_match.start()]

                for local_num in pending_sections:
                    global_num = section_start + (local_num - 1)
                    result[global_num] = commentary_text

        return result if result else None
