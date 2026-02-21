import re

import pdfplumber
from django.conf import settings
from django.core.management.base import BaseCommand

from catechism.models import Catechism, Commentary, CommentarySource, Question


class Command(BaseCommand):
    help = "Load John Wallis's 'A Brief and Easy Explanation of the Shorter Catechism' (1648) from PDF"

    def handle(self, *args, **options):
        catechism = Catechism.objects.get(slug='wsc')
        source, _ = CommentarySource.objects.update_or_create(
            slug="wallis",
            defaults={
                "name": "A Brief and Easy Explanation of the Shorter Catechism",
                "author": "John Wallis",
                "year": 1648,
                "description": (
                    "The first commentary ever written on the Shorter Catechism, "
                    "by a scribe of the Westminster Assembly. Uses a distinctive "
                    "yes/no sub-question format."
                ),
            },
        )

        pdf_path = settings.BASE_DIR / "data" / "wallis_wsc.pdf"
        if not pdf_path.exists():
            self.stderr.write(self.style.WARNING(
                f"Wallis PDF not found: {pdf_path}. Skipping."
            ))
            return

        full_text = self._extract_text(pdf_path)
        questions = self._parse_questions(full_text)

        if len(questions) != 107:
            self.stderr.write(self.style.WARNING(
                f"Expected 107 questions, found {len(questions)}."
            ))

        loaded = 0
        for num, body in sorted(questions.items()):
            try:
                question = Question.objects.get(catechism=catechism, number=num)
            except Question.DoesNotExist:
                self.stderr.write(self.style.WARNING(
                    f"Question {num} not found in database, skipping."
                ))
                continue

            Commentary.objects.update_or_create(
                question=question,
                source=source,
                defaults={"body": body},
            )
            loaded += 1

        self.stdout.write(self.style.SUCCESS(
            f"Loaded Wallis commentary for {loaded} questions"
        ))

    def _extract_text(self, pdf_path):
        """Extract all text from the PDF, concatenating pages."""
        full_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        return full_text

    def _parse_questions(self, full_text):
        """
        Split the extracted text by question number (Q1-Q107).

        Returns a dict mapping question number -> cleaned body text.
        """
        # Match both "Question 1." and "Q. 2." patterns
        pattern = re.compile(r"(?:Q\.|Question)\s+(\d+)\.")
        matches = list(pattern.finditer(full_text))

        # Deduplicate: keep only the first occurrence of each question number
        # (e.g. Q18 appears again in Appendix A as a memorisation example)
        seen = set()
        unique_matches = []
        for m in matches:
            num = int(m.group(1))
            if num not in seen:
                seen.add(num)
                unique_matches.append((num, m.start()))

        # Find the appendix boundary to cap Q107.
        # "Appendix A" appears twice: once in the TOC (early) and once at
        # the actual appendix (after Q107).  Use the last occurrence.
        appendix_pos = full_text.rfind("Appendix A")

        questions = {}
        for idx, (num, start) in enumerate(unique_matches):
            if idx + 1 < len(unique_matches):
                end = unique_matches[idx + 1][1]
            elif appendix_pos > start:
                end = appendix_pos
            else:
                end = len(full_text)

            raw = full_text[start:end]
            body = self._clean_text(raw)
            questions[num] = body

        return questions

    @staticmethod
    def _clean_text(text):
        """Clean extracted PDF text: remove footers, section headers, and footnotes."""
        lines = text.split("\n")
        cleaned = []

        for line in lines:
            # Remove page footer lines
            if re.match(
                r"^Easy Explanation of The Westminster Shorter Catechism \d+$",
                line,
            ):
                continue
            # Remove section headers like "Questions 11-20"
            if re.match(r"^Questions \d+[–\-]\d+$", line):
                continue
            cleaned.append(line)

        # Find the answer line (starts with "A. " or "Answer.")
        answer_start = None
        for i, line in enumerate(cleaned):
            if re.match(r"^A\.\s", line) or line.startswith("Answer."):
                answer_start = i
                break

        if answer_start is not None:
            # After the answer + proof-text lines, everything else is
            # footnotes that bled in from the PDF page layout.
            # Footnotes start with a bare number followed by text.
            # Proof-text lines contain scripture references (Book N:N).
            end_idx = len(cleaned)
            for j in range(answer_start + 1, len(cleaned)):
                line = cleaned[j].strip()
                if not line:
                    continue
                footnote_match = re.match(r"^(\d{1,2})\s+(.+)", line)
                if footnote_match:
                    after_num = footnote_match.group(2)
                    # Scripture books starting with a number (1 John, 2 Timothy, etc.)
                    is_scripture = bool(
                        re.match(r"^[A-Z][a-z]+\s+\d+[:\.]", after_num)
                    )
                    if not is_scripture:
                        end_idx = j
                        break
            cleaned = cleaned[:end_idx]

        # Remove inline footnotes that appear between sub-questions
        # e.g. "13 creature: any created thing, not necessarily an animal"
        final = []
        skip_continuation = False
        for line in cleaned:
            stripped = line.strip()
            # Detect inline footnote lines (number + lowercase word)
            if re.match(r"^\d{1,2}\s+[a-z]", stripped):
                skip_continuation = True
                continue
            if skip_continuation:
                # If this line continues the footnote text (doesn't match
                # a catechism pattern), skip it too
                if stripped and not re.match(
                    r"^(Is |Are |Or|And|Do |Did |Has |Had |Have |Was |Were |"
                    r"But |Can |May |Must |Should |Will |Does |Shall |That |"
                    r"Upon |With |Even |Not |After |A\.|Q\.|Question |Answer|"
                    r"Man|God|Sin|This|What|Such|Who|Each|Every|Also|Christ|"
                    r"Satan|These|Being|In |To |From |For |By |Our |The )",
                    stripped,
                ):
                    continue
                skip_continuation = False
            final.append(line)

        text = "\n".join(final)

        # Strip inline superscript footnote numbers attached to words
        # e.g. "covenant20 " -> "covenant ", "execute17 " -> "execute "
        # Only strip after letters/punctuation, never after digits (to
        # preserve scripture references like "73:25-28")
        text = re.sub(r'([a-zA-Z?.!,"\';])(\d{1,2})(?=[\s\n,;])', r"\1", text)

        # Collapse multiple blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Unwrap paragraphs: join lines within each paragraph so text reflows
        # to the browser width instead of preserving fixed column width.
        paragraphs = re.split(r"\n\s*\n", text)
        unwrapped = []
        for para in paragraphs:
            joined = re.sub(r"\s*\n\s*", " ", para).strip()
            if joined:
                unwrapped.append(joined)
        text = "\n\n".join(unwrapped)
        return text.strip()
