import re
from collections import defaultdict

from django.conf import settings
from django.core.management.base import BaseCommand

from catechism.models import Catechism, Commentary, CommentarySource, Question


# Roman numeral conversion
ROMAN_VALUES = {
    'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000
}


def roman_to_int(s):
    """Convert a Roman numeral string to an integer."""
    s = s.strip().upper()
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
    """Clean up Gutenberg text formatting."""
    # Remove Project Gutenberg header/footer markers
    text = re.sub(r'_', '', text)  # Remove italic markers
    text = re.sub(r'\[Footnote \d+:.*?\]', '', text, flags=re.DOTALL)
    # Normalize whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)
    # Unwrap paragraphs: join lines within each paragraph so text reflows
    # to the browser width instead of preserving fixed column width.
    paragraphs = re.split(r'\n\s*\n', text)
    unwrapped = []
    for para in paragraphs:
        joined = re.sub(r'\s*\n\s*', ' ', para).strip()
        if joined:
            unwrapped.append(joined)
    text = '\n\n'.join(unwrapped)
    return text.strip()


class Command(BaseCommand):
    help = "Load Thomas Ridgley's Body of Divinity commentary on the WLC"

    def handle(self, *args, **options):
        catechism = Catechism.objects.get(slug='wlc')

        source, _ = CommentarySource.objects.update_or_create(
            slug="ridgley",
            defaults={
                "name": "A Body of Divinity",
                "author": "Thomas Ridgley",
                "year": 1731,
                "description": (
                    "A comprehensive exposition of the Westminster Larger "
                    "Catechism, originally delivered as lectures. Revised "
                    "and annotated by John M. Wilson (1855)."
                ),
            },
        )

        # Read all volumes
        full_text = ""
        for vol in range(1, 5):
            filepath = settings.BASE_DIR / "data" / f"ridgley_vol{vol}.txt"
            if not filepath.exists():
                self.stderr.write(self.style.WARNING(
                    f"Volume {vol} not found: {filepath}. Skipping."
                ))
                continue
            text = filepath.read_text(encoding="utf-8")
            # Strip Gutenberg header/footer
            text = self._strip_gutenberg(text)
            full_text += text + "\n\n"
            self.stdout.write(f"Read volume {vol}: {len(text)} chars")

        if not full_text:
            self.stderr.write(self.style.ERROR("No text found."))
            return

        # Find question boundaries
        boundaries = self._find_question_boundaries(full_text)
        self.stdout.write(f"Found {len(boundaries)} question boundaries")

        # Extract text for each question
        question_texts = self._extract_question_texts(full_text, boundaries)
        self.stdout.write(
            f"Extracted commentary for {len(question_texts)} questions"
        )

        # Save to database
        loaded = 0
        for num in sorted(question_texts.keys()):
            text = clean_text(question_texts[num])
            if not text or len(text) < 50:
                continue

            try:
                question = Question.objects.get(catechism=catechism, number=num)
            except Question.DoesNotExist:
                self.stderr.write(self.style.WARNING(
                    f"  Q{num}: not found in database, skipping"
                ))
                continue

            Commentary.objects.update_or_create(
                question=question,
                source=source,
                defaults={"body": text},
            )
            loaded += 1

        self.stdout.write(self.style.SUCCESS(
            f"Loaded Ridgley commentary for {loaded} questions"
        ))

    def _strip_gutenberg(self, text):
        """Remove Project Gutenberg header and footer."""
        # Find start of actual content
        start_markers = [
            "*** START OF THE PROJECT GUTENBERG EBOOK",
            "*** START OF THIS PROJECT GUTENBERG EBOOK",
        ]
        for marker in start_markers:
            pos = text.find(marker)
            if pos >= 0:
                # Skip past the marker line
                newline = text.find('\n', pos)
                if newline >= 0:
                    text = text[newline + 1:]
                break

        # Find end of actual content
        end_markers = [
            "*** END OF THE PROJECT GUTENBERG EBOOK",
            "*** END OF THIS PROJECT GUTENBERG EBOOK",
            "End of the Project Gutenberg EBook",
            "End of Project Gutenberg",
        ]
        for marker in end_markers:
            pos = text.find(marker)
            if pos >= 0:
                text = text[:pos]
                break

        return text.strip()

    def _find_question_boundaries(self, full_text):
        """
        Find all question header positions.

        Headers look like:
            Quest. I.
            QUEST. I. _What is the chief and highest end of man?_
        or grouped:
            Quest. IX., X., XI.
        """
        boundaries = []  # list of (position, [question_numbers])

        # Match the centered "Quest. ..." header line (appears before the
        # full QUEST. line with the question text)
        pattern = re.compile(
            r'^\s*Quest\.\s+'
            r'([IVXLCDM]+(?:\.,?\s*[IVXLCDM]+)*)'
            r'\.\s*$',
            re.MULTILINE | re.IGNORECASE
        )

        for m in pattern.finditer(full_text):
            roman_str = m.group(1)
            # Parse potentially grouped question numbers
            # e.g., "IX., X., XI." or "XII., XIII."
            parts = re.split(r'[.,]\s*', roman_str)
            nums = []
            for part in parts:
                part = part.strip()
                if part and re.match(r'^[IVXLCDM]+$', part, re.IGNORECASE):
                    num = roman_to_int(part)
                    if 1 <= num <= 196:
                        nums.append(num)

            if nums:
                boundaries.append((m.start(), nums))

        # Sort by position
        boundaries.sort(key=lambda x: x[0])

        # Deduplicate: keep only the first occurrence of each question set
        seen = set()
        unique = []
        for pos, nums in boundaries:
            key = tuple(nums)
            if key not in seen:
                seen.add(key)
                unique.append((pos, nums))

        return unique

    def _extract_question_texts(self, full_text, boundaries):
        """Extract text between question boundaries."""
        question_texts = defaultdict(str)

        for i, (pos, nums) in enumerate(boundaries):
            # End at the next boundary or end of text
            if i + 1 < len(boundaries):
                end_pos = boundaries[i + 1][0]
            else:
                end_pos = len(full_text)

            section_text = full_text[pos:end_pos]

            # Assign to each question in the group
            for num in nums:
                if question_texts[num]:
                    question_texts[num] += "\n\n" + section_text
                else:
                    question_texts[num] = section_text

        return dict(question_texts)
