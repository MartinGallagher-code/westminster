import re

from django.conf import settings
from django.core.management.base import BaseCommand

from catechism.models import Catechism, Commentary, CommentarySource, Question


class Command(BaseCommand):
    help = "Load Alexander Whyte's commentary on the Shorter Catechism (1882)"

    def handle(self, *args, **options):
        catechism = Catechism.objects.get(slug='wsc')
        source, _ = CommentarySource.objects.update_or_create(
            slug="whyte",
            defaults={
                "name": "A Commentary on the Shorter Catechism",
                "author": "Alexander Whyte",
                "year": 1882,
                "description": (
                    "A rich and practical commentary drawing on the best Reformed "
                    "divines, with questions for study at the end of each section."
                ),
            },
        )

        filepath = settings.BASE_DIR / "data" / "whyte_commentary.txt"
        if not filepath.exists():
            self.stderr.write(self.style.WARNING(
                f"Whyte commentary file not found: {filepath}. Skipping."
            ))
            return

        text = filepath.read_text(encoding="utf-8")
        lines = text.split("\n")

        # Locate the start line of each question (Q1-Q107).
        boundaries = self._find_question_boundaries(lines)
        if len(boundaries) != 107:
            self.stderr.write(self.style.WARNING(
                f"Expected 107 question boundaries, found {len(boundaries)}."
            ))

        # Extract the body text for each question.
        loaded = 0
        for idx, (qnum, start_line) in enumerate(boundaries):
            # End line is the start of the next question, or end of file.
            if idx + 1 < len(boundaries):
                end_line = boundaries[idx + 1][1]
            else:
                end_line = len(lines)

            raw_body = "\n".join(lines[start_line:end_line])
            body = self._clean_text(raw_body)

            if not body:
                self.stderr.write(self.style.WARNING(
                    f"Empty body for Q{qnum}, skipping."
                ))
                continue

            try:
                question = Question.objects.get(catechism=catechism, number=qnum)
            except Question.DoesNotExist:
                self.stderr.write(self.style.WARNING(
                    f"Question {qnum} not found in database, skipping."
                ))
                continue

            Commentary.objects.update_or_create(
                question=question,
                source=source,
                defaults={"body": body},
            )
            loaded += 1

        self.stdout.write(self.style.SUCCESS(
            f"Loaded Whyte commentary for {loaded} questions"
        ))

    def _find_question_boundaries(self, lines):
        """Return a sorted list of (question_number, line_index) tuples."""
        boundaries = []

        # Q1 has a unique header: "QUESTION  i."
        for i, line in enumerate(lines):
            if re.match(r"^QUESTION\s+i\.", line):
                boundaries.append((1, i))
                break

        # Q2-Q107: lines starting with "Q." or "Q-" followed by a number.
        for i, line in enumerate(lines):
            m = re.match(r"^Q[\.\-]\s+(.+?)[\.\-]\s+\w", line)
            if not m:
                continue
            raw_num = m.group(1).strip().replace(" ", "")
            num = self._parse_question_number(raw_num)
            if num is not None and 2 <= num <= 107:
                boundaries.append((num, i))

        boundaries.sort(key=lambda x: x[1])
        return boundaries

    @staticmethod
    def _parse_question_number(raw):
        """Parse a question number from OCR text, handling artifacts."""
        # Pure digits (most common case)
        if raw.isdigit():
            return int(raw)
        # OCR sometimes renders numbers with lowercase letters:
        # "ioo" = 100, "ioi" = 101
        ocr_map = {"ioo": 100, "ioi": 101}
        if raw in ocr_map:
            return ocr_map[raw]
        return None

    @staticmethod
    def _clean_text(text):
        """Clean up common OCR artifacts in the body text."""
        # Collapse multiple spaces into one (OCR spacing artifact)
        text = re.sub(r"  +", " ", text)
        # Fix broken words at line ends: word- \n continued -> word-continued
        # (hyphenated line breaks from OCR)
        text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
        # Collapse multiple blank lines into at most two newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text
