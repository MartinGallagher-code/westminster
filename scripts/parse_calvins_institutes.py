"""
Parse Calvin's Institutes of the Christian Religion (Allen translation, 1813)
from Project Gutenberg plain text.

Downloads the text and extracts per-chapter content into data/calvins_institutes.json.

Structure:
  Book I  (chapters 1–18)   — Knowledge of God the Creator
  Book II (chapters 19–35)  — Knowledge of God the Redeemer
  Book III (chapters 36–60) — The Mode of Obtaining the Grace of Christ
  Book IV (chapters 61–80)  — The External Means of Grace

Vol 1 (PG #45001): Books I–II + Book III chapters 1–13
Vol 2 (PG #64392): Book III chapters 14–25 + Book IV chapters 1–20

Two different formatting styles are handled:
  Vol 1: 'Chapter I. Title Text\n\n' (inline title, mixed case)
  Vol 2: 'CHAPTER XIV.\nTITLE ON NEXT LINE\n\n' (centered all-caps)

Each chapter becomes one Question record; each book becomes one Topic record.
"""

import json
import re
import urllib.request
from pathlib import Path

GUTENBERG_URL_VOL1 = "https://www.gutenberg.org/cache/epub/45001/pg45001.txt"
GUTENBERG_URL_VOL2 = "https://www.gutenberg.org/cache/epub/64392/pg64392.txt"

BOOKS = [
    {
        "book": 1,
        "title": "Knowledge of God the Creator",
        "slug": "book-1-knowledge-of-god-the-creator",
        "chapter_start": 1,
        "chapter_end": 18,
        "description": (
            "The knowledge of God as Creator, including natural revelation, "
            "the corruption of human knowledge by idolatry, and Scripture as "
            "the true spectacles through which God is known."
        ),
    },
    {
        "book": 2,
        "title": "Knowledge of God the Redeemer",
        "slug": "book-2-knowledge-of-god-the-redeemer",
        "chapter_start": 19,
        "chapter_end": 35,
        "description": (
            "The fall of man, the law, the mediatorial work of Christ, "
            "and His threefold office as Prophet, Priest, and King."
        ),
    },
    {
        "book": 3,
        "title": "The Mode of Obtaining the Grace of Christ",
        "slug": "book-3-mode-of-obtaining-grace",
        "chapter_start": 36,
        "chapter_end": 60,
        "description": (
            "Faith, regeneration, justification by faith alone, Christian liberty, "
            "prayer, election and predestination, and the resurrection."
        ),
    },
    {
        "book": 4,
        "title": "The External Means of Grace",
        "slug": "book-4-external-means-of-grace",
        "chapter_start": 61,
        "chapter_end": 80,
        "description": (
            "The church, its government and ministry, the sacraments of baptism "
            "and the Lord's Supper, and the relation of the church to civil government."
        ),
    },
]

# Maps global chapter number → book number
CHAPTER_BOOK = {}
for b in BOOKS:
    for ch in range(b["chapter_start"], b["chapter_end"] + 1):
        CHAPTER_BOOK[ch] = b["book"]


def download_text(url, cache_path):
    """Download plain text from URL if not already cached."""
    if cache_path.exists():
        print(f"Using cached: {cache_path}")
        return cache_path.read_text(encoding="utf-8", errors="replace")
    print(f"Downloading {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    cache_path.write_bytes(data)
    print(f"Saved {cache_path.stat().st_size / 1024:.0f} KB to {cache_path}")
    return data.decode("utf-8", errors="replace")


def strip_pg(text):
    """Remove Project Gutenberg header and footer."""
    start = re.search(r"\*\*\* START OF .+?\*\*\*", text)
    if start:
        text = text[start.end():]
    end = re.search(r"\*\*\* END OF .+?\*\*\*", text)
    if end:
        text = text[:end.start()]
    return text


def roman_to_int(s):
    """Convert Roman numeral string to integer."""
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    result, prev = 0, 0
    for ch in reversed(s.upper()):
        val = values.get(ch, 0)
        result += val if val >= prev else -val
        prev = val
    return result


def parse_vol1_chapters(text):
    """
    Parse chapters from vol 1.
    Format: '\n\nChapter I. Title Text\n\n' (mixed case, title inline)
    Only look in the body section (after the Table of Contents).
    """
    # Find where body starts: first all-caps BOOK I header
    body_start = text.find("\nBOOK I.")
    if body_start == -1:
        print("ERROR: Could not find 'BOOK I.' in vol 1 body")
        return []
    body = text[body_start:]

    # Pattern: double newline, then 'Chapter [Roman]. Title text' possibly multi-line
    ch_pattern = re.compile(
        r"\n\n(Chapter\s+([IVXLC]+)\.\s+[^\n]+(?:\n[^\n]+)*?)\n\n",
        re.IGNORECASE,
    )

    matches = list(ch_pattern.finditer(body))
    chapters = []
    for i, m in enumerate(matches):
        roman = m.group(2).upper()
        local_num = roman_to_int(roman)
        # Clean up multi-line title
        title = re.sub(r"\s+", " ", m.group(1)).strip()
        title = re.sub(r"^Chapter\s+[IVXLC]+\.\s+", "", title, flags=re.IGNORECASE)

        body_start_pos = m.end()
        body_end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        raw_body = body[body_start_pos:body_end_pos]
        chapters.append((local_num, title, raw_body))

    return chapters


def parse_vol2_chapters(text):
    """
    Parse chapters from vol 2.
    Format: 3+ newlines + spaces + CHAPTER XIV. + newline + title (multi-line) + double-newline
    Title is in ALL CAPS and may wrap across multiple lines.
    """
    # Match the chapter header: 3+ newlines, spaces, CHAPTER [Roman]., newline, title block
    ch_pattern = re.compile(
        r"\n{3,}\s+(CHAPTER\s+([IVXLC]+)\.)\s*\n(.+?)(?:\n\s*\n)",
        re.DOTALL | re.IGNORECASE,
    )

    matches = list(ch_pattern.finditer(text))
    # Record the position right after each match's title block (= start of body)
    chapters = []
    for i, m in enumerate(matches):
        roman = m.group(2).upper()
        local_num = roman_to_int(roman)
        # Title may span multiple lines (all caps, centered) — collapse to single line
        title = re.sub(r"\s+", " ", m.group(3)).strip()
        # Convert ALL CAPS title to title case
        title = title.title()
        # Fix lowercase articles/prepositions mangled by .title()
        for word in ["Of", "The", "And", "Or", "In", "On", "To", "By", "For",
                     "With", "A", "An", "Not", "But"]:
            title = re.sub(r"\b" + word.title() + r"\b", word, title)

        body_start_pos = m.end()
        body_end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        raw_body = text[body_start_pos:body_end_pos]
        chapters.append((local_num, title, raw_body))

    return chapters


def clean_text(text):
    """Clean OCR/formatting artifacts from Gutenberg plain text."""
    # Remove Unicode soft hyphens and regular hyphenated line-breaks
    text = re.sub(r"(\w)[‐-]\s*\n\s*(\w)", r"\1\2", text)
    # Collapse multiple spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)
    # Remove bare page numbers on their own lines
    text = re.sub(r"^\s*\d{1,4}\s*$", "", text, flags=re.MULTILINE)
    # Collapse excessive blank lines
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text


def unwrap_paragraphs(text):
    """Unwrap soft line breaks within paragraphs, preserving paragraph breaks."""
    paragraphs = re.split(r"\n\s*\n", text)
    unwrapped = []
    for para in paragraphs:
        joined = re.sub(r"\s*\n\s*", " ", para).strip()
        if joined:
            unwrapped.append(joined)
    return "\n\n".join(unwrapped).strip()


def main():
    base_dir = Path(__file__).resolve().parent.parent
    cache_vol1 = Path("/tmp/institutes_vol1.txt")
    cache_vol2 = Path("/tmp/institutes_vol2.txt")
    output_path = base_dir / "data" / "calvins_institutes.json"

    vol1_raw = download_text(GUTENBERG_URL_VOL1, cache_vol1)
    vol2_raw = download_text(GUTENBERG_URL_VOL2, cache_vol2)

    vol1 = strip_pg(vol1_raw)
    vol2 = strip_pg(vol2_raw)

    # Parse chapters from each volume
    vol1_chapters = parse_vol1_chapters(vol1)
    vol2_chapters = parse_vol2_chapters(vol2)

    print(f"Vol 1: {len(vol1_chapters)} chapters (expected 48)")
    print(f"Vol 2: {len(vol2_chapters)} chapters (expected 32)")

    # Combine all chapters in sequence
    # Vol 1 global chapters: 1–48
    # Vol 2 global chapters: 49–80
    all_chapters = vol1_chapters + vol2_chapters

    # Build the data items
    data_items = []
    for global_idx, (local_num, title, raw_body) in enumerate(all_chapters):
        global_ch = global_idx + 1
        book_num = CHAPTER_BOOK.get(global_ch, 1)
        book_info = next(b for b in BOOKS if b["book"] == book_num)

        cleaned = clean_text(raw_body)
        body = unwrap_paragraphs(cleaned)

        data_items.append({
            "Number": global_ch,
            "Book": book_num,
            "BookTitle": book_info["title"],
            "Chapter": local_num,
            "ChapterTitle": title,
            "Text": body,
        })

    output = {
        "Metadata": {
            "Title": "Institutes of the Christian Religion",
            "Year": "1559",
            "Authors": ["John Calvin"],
            "Translator": "John Allen",
            "TranslationYear": "1813",
            "SourceUrl": GUTENBERG_URL_VOL1,
            "SourceAttribution": "Public Domain",
            "CreedFormat": "SystematicTheology",
        },
        "Data": data_items,
    }

    output_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nWrote {len(data_items)} chapters to {output_path}")
    total_chars = sum(len(d["Text"]) for d in data_items)
    print(f"Total text: {total_chars:,} characters")

    if len(data_items) != 80:
        print(f"WARNING: Expected 80 chapters but got {len(data_items)}")
        # Show chapter distribution by book
        from collections import Counter
        book_dist = Counter(d["Book"] for d in data_items)
        for bnum in sorted(book_dist):
            expected = next(b for b in BOOKS if b["book"] == bnum)
            expect_count = expected["chapter_end"] - expected["chapter_start"] + 1
            print(f"  Book {bnum}: {book_dist[bnum]} chapters (expected {expect_count})")
    else:
        print("All 80 chapters parsed successfully!")


if __name__ == "__main__":
    main()
