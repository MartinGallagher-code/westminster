import json
import re
import time
from html.parser import HTMLParser
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.management.base import BaseCommand


CCEL_BASE = "https://www.ccel.org/ccel/watson/divinity.{}.html"

# Mapping: (CCEL page section, list of WSC question numbers, chapter title)
PAGE_MAP = [
    ("v.i", [1], "Man's Chief End"),
    ("v.ii", [2], "The Scriptures"),
    ("vi.i", [4], "The Being of God"),
    ("vi.ii", [4], "The Knowledge of God"),
    ("vi.iii", [4], "The Eternity of God"),
    ("vi.iv", [4], "The Unchangeableness of God"),
    ("vi.v", [4], "The Wisdom of God"),
    ("vi.vi", [4], "The Power of God"),
    ("vi.vii", [4], "The Holiness of God"),
    ("vi.viii", [4], "The Justice of God"),
    ("vi.ix", [4], "The Mercy of God"),
    ("vi.x", [4], "The Truth of God"),
    ("vi.xi", [5], "The Unity of God"),
    ("vi.xii", [6], "The Trinity"),
    ("vi.xiii", [9, 10], "The Creation"),
    ("vi.xiv", [11], "The Providence of God"),
    ("vii.i", [12], "The Covenant of Works"),
    ("vii.ii", [13], "Adam's Sin"),
    ("vii.iii", [16, 17, 18], "Original Sin"),
    ("vii.iv", [19], "Man's Misery by the Fall"),
    ("viii.i", [20], "The Covenant of Grace"),
    ("viii.ii", [21], "Christ the Mediator of the Covenant"),
    ("viii.iii", [24], "Christ's Prophetic Office"),
    ("viii.iv", [25], "Christ's Priestly Office"),
    ("viii.v", [26], "Christ's Kingly Office"),
    ("viii.vi", [27], "Christ's Humiliation in His Incarnation"),
    ("viii.vii", [28], "Christ's Exaltation"),
    ("viii.viii", [29], "Christ the Redeemer"),
    ("ix.i", [30], "Faith"),
    ("ix.ii", [31], "Effectual Calling"),
    ("ix.iii", [33], "Justification"),
    ("ix.iv", [34], "Adoption"),
    ("ix.v", [35], "Sanctification"),
    ("ix.vi", [36], "Assurance"),
    ("ix.vii", [36], "Peace"),
    ("ix.viii", [36], "Joy"),
    ("ix.ix", [36], "Growth in Grace"),
    ("ix.x", [36], "Perseverance"),
    ("x.i", [37], "The Death of the Righteous"),
    ("x.ii", [37], "A Believer's Privilege at Death"),
    ("x.iii", [38], "The Resurrection"),
]


class HTMLTextExtractor(HTMLParser):
    """Extract text from the book-content div of a CCEL page."""

    def __init__(self):
        super().__init__()
        self.in_book_content = False
        self.depth = 0
        self.skip_tag = None
        self.skip_depth = 0
        self.paragraphs = []
        self.current = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")

        if tag == "div" and "book-content" in cls:
            self.in_book_content = True
            self.depth = 1
            return

        if not self.in_book_content:
            return

        if tag == "div":
            self.depth += 1

        if tag == "table" and "book_navbar" in cls:
            self.skip_tag = "table"
            self.skip_depth = 1
            return
        if tag == "script":
            self.skip_tag = "script"
            self.skip_depth = 1
            return

        if self.skip_tag:
            if tag == self.skip_tag:
                self.skip_depth += 1
            return

        if tag in ("h3", "h4", "h5"):
            self.current.append("\n\n### ")
        elif tag == "p":
            self.current.append("\n\n")
        elif tag == "br":
            self.current.append("\n")

    def handle_endtag(self, tag):
        if not self.in_book_content:
            return

        if self.skip_tag:
            if tag == self.skip_tag:
                self.skip_depth -= 1
                if self.skip_depth <= 0:
                    self.skip_tag = None
            return

        if tag == "div":
            self.depth -= 1
            if self.depth <= 0:
                self.in_book_content = False

    def handle_data(self, data):
        if self.in_book_content and not self.skip_tag:
            self.current.append(data)

    def get_text(self):
        raw = "".join(self.current)
        lines = raw.split("\n")
        cleaned = []
        for line in lines:
            line = " ".join(line.split())
            cleaned.append(line)
        text = "\n".join(cleaned)
        text = re.sub(r"\n{3,}", "\n\n", text)
        paragraphs = re.split(r"\n\s*\n", text)
        unwrapped = []
        for para in paragraphs:
            joined = re.sub(r"\s*\n\s*", " ", para).strip()
            if joined:
                unwrapped.append(joined)
        text = "\n\n".join(unwrapped)
        return text.strip()


def fetch_page(section, delay=0.3):
    """Fetch a CCEL page and extract its text content."""
    url = CCEL_BASE.format(section)
    req = Request(url, headers={"User-Agent": "WestminsterCatechismApp/1.0"})
    try:
        with urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except URLError as e:
        return None, str(e)

    parser = HTMLTextExtractor()
    parser.feed(html)
    text = parser.get_text()

    time.sleep(delay)
    return text, None


class Command(BaseCommand):
    help = "Fetch Watson's Body of Divinity from CCEL and save to data/watson_commentary.json"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delay",
            type=float,
            default=0.3,
            help="Delay between HTTP requests in seconds (default: 0.3)",
        )

    def handle(self, *args, **options):
        delay = options["delay"]

        question_texts = {}  # {question_number: body_text}

        total = len(PAGE_MAP)
        failures = 0

        for i, (section, q_numbers, title) in enumerate(PAGE_MAP, 1):
            self.stdout.write(f"  [{i}/{total}] Fetching: {title} ({section})...")
            text, error = fetch_page(section, delay)

            if error:
                self.stderr.write(self.style.WARNING(f"    FAILED: {error}"))
                failures += 1
                continue

            if not text:
                self.stderr.write(self.style.WARNING("    EMPTY page"))
                failures += 1
                continue

            self.stdout.write(f"    Got {len(text)} chars")

            for qnum in q_numbers:
                if qnum not in question_texts:
                    question_texts[qnum] = []
                question_texts[qnum].append((title, text))

        # Build final JSON structure
        result = {}
        for qnum, chapters in sorted(question_texts.items()):
            if len(chapters) == 1:
                body = chapters[0][1]
            else:
                parts = []
                for title, text in chapters:
                    parts.append(f"--- {title} ---\n\n{text}")
                body = "\n\n\n".join(parts)
            result[str(qnum)] = body

        output_path = settings.BASE_DIR / "data" / "watson_commentary.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(
            f"Saved Watson commentary for {len(result)} questions to {output_path} "
            f"({failures} page failures)"
        ))
