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

ROMAN_VALUES = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}


def fix_ocr_roman(s):
    """Fix common OCR substitutions in Roman numerals."""
    s = s.strip()
    # Remove spaces within the numeral (e.g. "I  Y" -> "IY")
    s = re.sub(r'\s+', '', s)
    s = s.upper()
    # OCR commonly confuses: V→Y, I→T at end, lowercase l→I
    s = s.replace('Y', 'V')  # Y is never valid in Roman numerals
    s = s.replace('T', 'I')  # T at end is usually I
    # Fix XVL -> XVI (L misread for I at end, but only if not after X)
    if s.endswith('L') and len(s) > 1 and s[-2] != 'X':
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
    # Remove page headers like "SECT. 4, 5.]  THE HOLY SCRIPTURE.  13"
    text = re.sub(r'^\s*SECT\..*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\s+CONFESSION\s+OF\s+FAITH\.\s*(\[CHAP\..*)?$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*CHAP\.\s+[IVXLC]+.*CONFESSION\s+OF\s+FAITH\.\s*\d*\s*$', '', text, flags=re.MULTILINE)
    # Remove bare page numbers
    text = re.sub(r'^\s*\d{1,3}\s*$', '', text, flags=re.MULTILINE)
    # Fix hyphenated line breaks
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
    # Collapse multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)
    # Collapse excessive blank lines
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
    help = "Load Robert Shaw's Exposition of the Westminster Confession of Faith"

    def handle(self, *args, **options):
        catechism = Catechism.objects.get(slug='wcf')

        source, _ = CommentarySource.objects.update_or_create(
            slug="shaw",
            defaults={
                "name": "An Exposition of the Confession of Faith",
                "author": "Robert Shaw",
                "year": 1845,
                "description": (
                    "A thorough exposition of the Westminster Confession "
                    "of Faith, treating each section with careful theological "
                    "explanation and practical application."
                ),
            },
        )

        filepath = settings.BASE_DIR / "data" / "shaw_wcf.txt"
        if not filepath.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {filepath}"))
            return

        full_text = filepath.read_text(encoding="utf-8", errors="replace")

        # Strip preamble - find first CHAPTER marker
        chapter_start = re.search(r'^CHAPTER\s+I\.\s*$', full_text, re.MULTILINE)
        if chapter_start:
            full_text = full_text[chapter_start.start():]

        # Find chapter boundaries
        chapter_pattern = re.compile(
            r'^CHAPTER\s+([IVXLCYT]+[.,]?)\s*$',
            re.MULTILINE
        )
        chapter_positions = []
        for m in chapter_pattern.finditer(full_text):
            roman = re.sub(r'[.,]', '', m.group(1))
            num = roman_to_int(roman)
            if 1 <= num <= 33:
                chapter_positions.append((m.start(), num))

        # Deduplicate chapter numbers (keep first occurrence)
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
                # Fallback: assign whole chapter exposition to all sections
                expo_match = re.search(r'EXPOSITION[.\'"]*\s*\n', chapter_text, re.IGNORECASE)
                if expo_match:
                    body = clean_text(chapter_text[expo_match.end():])
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
                            f"  Ch {ch_num}: assigned full chapter exposition to "
                            f"§{section_start}-{section_end}"
                        )
                continue

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
            f"Loaded Shaw commentary for {loaded} sections ({skipped} skipped)"
        ))

    def _parse_chapter_sections(self, chapter_text, ch_num, section_start):
        """
        Parse a chapter's text into section-level exposition blocks.

        Shaw's pattern:
        - Section I. — [WCF text]
        - [proof texts]
        - EXPOSITION.
        - [Shaw's commentary]

        Sometimes multiple sections share one EXPOSITION block.
        Returns dict of {global_section_number: exposition_text}.
        """
        # Find all section markers and exposition markers
        section_pattern = re.compile(
            r'^Section\s+([IVXLCYTl][IVXLCYTl\s]*[IVXLCYTl]|[IVXLCYTl])[.,]?\s*[-—]?\s*(?=[A-Z])',
            re.MULTILINE
        )
        expo_pattern = re.compile(
            r'^EXPOSITION[.\'",:]*\s*$',
            re.MULTILINE | re.IGNORECASE
        )

        # Build ordered list of markers
        markers = []
        for m in section_pattern.finditer(chapter_text):
            roman = m.group(1)
            local_num = roman_to_int(roman)
            markers.append(('section', m.start(), local_num))

        for m in expo_pattern.finditer(chapter_text):
            markers.append(('expo', m.start(), m.end()))

        markers.sort(key=lambda x: x[1])

        if not markers:
            return None

        # Walk through markers, collecting section numbers between expositions
        result = {}
        pending_sections = []

        # Build section position index for fallback
        section_positions = {}  # local_num -> (start_pos, marker_index)
        for j, marker in enumerate(markers):
            if marker[0] == 'section':
                section_positions[marker[2]] = (marker[1], j)

        for j, marker in enumerate(markers):
            if marker[0] == 'section':
                pending_sections.append(marker[2])  # local section number
            elif marker[0] == 'expo':
                if pending_sections:
                    # Find end of this exposition (next section marker or end of chapter)
                    expo_end_pos = len(chapter_text)
                    for k in range(j + 1, len(markers)):
                        if markers[k][0] == 'section':
                            expo_end_pos = markers[k][1]
                            break

                    expo_text = chapter_text[marker[2]:expo_end_pos]

                    # Assign to all pending sections
                    for local_num in pending_sections:
                        global_num = section_start + (local_num - 1)
                        result[global_num] = expo_text

                    pending_sections = []

        # Fallback: sections without a following EXPOSITION marker
        # Use the full text between this section and the next section/chapter
        for local_num in pending_sections:
            global_num = section_start + (local_num - 1)
            if global_num not in result:
                pos, midx = section_positions[local_num]
                # Find end: next section marker or chapter end
                end_pos = len(chapter_text)
                for k in range(midx + 1, len(markers)):
                    if markers[k][0] == 'section':
                        end_pos = markers[k][1]
                        break
                section_text = chapter_text[pos:end_pos]
                result[global_num] = section_text

        return result if result else None
