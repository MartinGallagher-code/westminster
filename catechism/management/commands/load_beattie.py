import re
from collections import defaultdict

import pdfplumber
from django.conf import settings
from django.core.management.base import BaseCommand

from catechism.models import Commentary, CommentarySource, Question


class Command(BaseCommand):
    help = "Load Francis R. Beattie's 'The Presbyterian Standards' as WSC commentary"

    def handle(self, *args, **options):
        source, _ = CommentarySource.objects.update_or_create(
            slug="beattie",
            defaults={
                "name": "The Presbyterian Standards",
                "author": "Francis R. Beattie",
                "year": 1896,
                "description": (
                    "An exposition of the Westminster Confession of Faith "
                    "and Catechisms, organized around the Shorter Catechism "
                    "questions."
                ),
            },
        )

        pdf_path = settings.BASE_DIR / "data" / "beattie_presbyterian_standards.pdf"
        if not pdf_path.exists():
            self.stderr.write(
                self.style.WARNING(f"PDF not found: {pdf_path}. Skipping.")
            )
            return

        self.stdout.write("Extracting text from PDF...")
        full_text = self._extract_text(pdf_path)

        self.stdout.write("Parsing chapters by Shorter Catechism question ranges...")
        question_texts = self._parse_chapters(full_text)

        loaded = 0
        for num in sorted(question_texts):
            try:
                question = Question.objects.get(number=num)
            except Question.DoesNotExist:
                self.stderr.write(
                    self.style.WARNING(
                        f"Question {num} not found in database, skipping."
                    )
                )
                continue

            body = question_texts[num].strip()
            if not body:
                continue

            Commentary.objects.update_or_create(
                question=question,
                source=source,
                defaults={"body": body},
            )
            loaded += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded Beattie commentary for {loaded} questions"
            )
        )

    def _extract_text(self, pdf_path):
        """Extract all text from the PDF, joining pages."""
        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n".join(pages)

    def _parse_chapters(self, full_text):
        """
        Find chapter headers, extract text between them, and map each
        Shorter Catechism question number to its chapter text.

        Beattie organises his exposition by doctrinal topics.  Each chapter
        header references a range of Shorter Catechism questions, e.g.:

            SHORTER CATECHISM, 4--6; LARGER CATECHISM, 6--11; ...

        Some chapters cover only the Confession / Larger Catechism and use
        dashes instead of question numbers (e.g. ``SHORTER CATECHISM, ----``).
        Those chapters serve as boundary markers but produce no SC entries.

        When a question appears in more than one chapter the texts are
        concatenated with a horizontal-rule separator.
        """
        # ---- 1. Locate every chapter header ----
        # Matches both numbered headers and ---- placeholders.
        all_headers_re = re.compile(
            r"(SHORTER CATECHISM[,;]?\s*"
            r"[\d\-\u2013\u2014]+(?:\s*(?:AND|,)\s*[\d\-\u2013\u2014]+)*)"
            r"\s*;\s*LARGER CATECHISM",
            re.IGNORECASE,
        )
        all_matches = list(all_headers_re.finditer(full_text))
        if not all_matches:
            self.stderr.write(
                self.style.WARNING("No chapter headers found in PDF text.")
            )
            return {}

        self.stdout.write(f"  Found {len(all_matches)} chapter headers")

        # ---- 2. Build chapter boundaries ----
        # Each boundary is (start_of_header, end_of_header_block).
        # The chapter body runs from end_of_header_block to start_of_NEXT_header_title.
        boundaries = []
        for match in all_matches:
            boundaries.append(match.start())

        # ---- 3. Extract chapter text for each SC-bearing header ----
        sc_number_re = re.compile(
            r"SHORTER CATECHISM[,;]?\s*"
            r"([\d]+(?:\s*[-\u2013\u2014]+\s*[\d]+)?"
            r"(?:\s*(?:AND|,)\s*[\d]+(?:\s*[-\u2013\u2014]+\s*[\d]+)?)*)",
            re.IGNORECASE,
        )

        question_texts = defaultdict(list)

        for idx, match in enumerate(all_matches):
            # Check whether this header carries SC question numbers
            sc_match = sc_number_re.match(match.group(0))
            if not sc_match:
                continue  # ---- placeholder, skip

            q_numbers = self._parse_question_range(sc_match.group(1))
            if not q_numbers:
                continue

            # --- Derive the chapter title (short lines above the header) ---
            pre_start = max(0, match.start() - 300)
            pre_text = full_text[pre_start : match.start()]
            title_lines = [
                ln.strip()
                for ln in pre_text.split("\n")
                if ln.strip() and len(ln.strip()) < 120
            ]
            chapter_title = " ".join(title_lines[-3:]) if title_lines else ""

            # --- Chapter body starts after the header block ---
            chapter_start = match.end()
            # Skip past the rest of the header (LARGER CATECHISM ...; CONFESSION ...)
            header_tail_re = re.compile(
                r"[\s;,]*([\d\-\u2013\u2014,\s]*(?:AND\s*)?[\d\-\u2013\u2014,\s]*"
                r"[;.]?\s*(?:CONFESS[I1]ON OF FAITH[^.\n]*\.?\s*)?)",
                re.IGNORECASE,
            )
            ht = header_tail_re.match(full_text[chapter_start:])
            if ht:
                chapter_start += ht.end()

            # --- Chapter body ends at the title area of the next chapter ---
            if idx + 1 < len(all_matches):
                next_header_start = all_matches[idx + 1].start()
                # Walk backwards from the next header to skip its title lines
                pre_next = full_text[
                    max(0, next_header_start - 300) : next_header_start
                ]
                pre_next_lines = pre_next.split("\n")
                trim = 0
                for ln in reversed(pre_next_lines):
                    stripped = ln.strip()
                    if stripped and len(stripped) < 120:
                        trim += len(ln) + 1
                    else:
                        break
                chapter_end = next_header_start - trim
            else:
                chapter_end = len(full_text)

            chapter_body = full_text[chapter_start:chapter_end].strip()

            for q_num in q_numbers:
                if 1 <= q_num <= 107:
                    if chapter_title.strip():
                        section = f"## {chapter_title.strip()}\n\n{chapter_body}"
                    else:
                        section = chapter_body
                    question_texts[q_num].append(section)

        # ---- 4. Merge multiple chapters for the same question ----
        merged = {}
        for q_num, parts in question_texts.items():
            merged[q_num] = "\n\n---\n\n".join(parts)

        return merged

    @staticmethod
    def _parse_question_range(range_str):
        """
        Parse a range string like ``39-42 AND 82-83`` into a list of ints.
        Handles regular dashes, en-dashes, and em-dashes.
        """
        numbers = []
        parts = re.split(r"\s+AND\s+|,", range_str, flags=re.IGNORECASE)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            range_match = re.match(
                r"(\d+)\s*[-\u2013\u2014]+\s*(\d+)", part
            )
            if range_match:
                lo = int(range_match.group(1))
                hi = int(range_match.group(2))
                numbers.extend(range(lo, hi + 1))
            else:
                digits = re.findall(r"\d+", part)
                numbers.extend(int(d) for d in digits)
        return numbers
