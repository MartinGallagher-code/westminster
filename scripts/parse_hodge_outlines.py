"""
Parse A.A. Hodge's Outlines of Theology (1879 revised edition)
from Internet Archive DjVu OCR text.

Downloads the text and extracts per-chapter content into data/hodge_outlines.json.

Structure:
  43 chapters covering the full range of Reformed systematic theology.
  Chapters are organized into thematic parts (Topics).
  Each chapter becomes one Question record; each part becomes one Topic record.

Note: The OCR scan is missing chapters XV, XXI, and XXXVII — these pages
were not captured in the Internet Archive scan. The output contains 40 chapters
with their correct numbers (1–14, 16–20, 22–36, 38–43).
"""

import json
import re
import urllib.request
from pathlib import Path

IA_URL = "https://archive.org/download/outlinesoftheolo1879hodg/outlinesoftheolo1879hodg_djvu.txt"

# 43 chapters with their correct titles (from the table of contents)
# Index = chapter_number - 1
CHAPTER_TITLES = [
    "Christian Theology: Its Several Branches and Their Relation to Other Departments of Human Knowledge",
    "The Origin of the Idea of God and Proof of His Existence",
    "The Sources of Theology",
    "The Inspiration of the Bible",
    "The Scriptures of the Old and New Testaments the Only Rule of Faith and Judge of Controversies",
    "A Comparison of Systems",
    "Creeds and Confessions",
    "The Attributes of God",
    "The Holy Trinity",
    "The Decrees of God in General",
    "Predestination",
    "The Creation of the World",
    "Angels",
    "Providence",
    "The Moral Constitution of the Soul, Will, Conscience, Liberty, Etc.",
    "Creation and Original State of Man",
    "The Covenant of Works",
    "The Nature of Sin and the Sin of Adam",
    "Original Sin",
    "Inability",
    "The Imputation of Adam's First Sin to His Posterity",
    "The Covenant of Grace",
    "The Person of Christ",
    "The Mediatorial Office of Christ",
    "The Atonement: Its Nature, Necessity, Perfection, and Extent",
    "The Intercession of Christ",
    "The Mediatorial Kingship of Christ",
    "Effectual Calling",
    "Regeneration",
    "Faith",
    "Union of Believers with Christ",
    "Repentance, and the Romish Doctrine of Penance",
    "Justification",
    "Adoption, and the Order of Grace in the Application of Redemption",
    "Sanctification",
    "Perseverance of the Saints",
    "Death, and the State of the Soul after Death",
    "The Resurrection",
    "The Second Advent and General Judgment",
    "Heaven and Hell",
    "The Sacraments",
    "Baptism",
    "The Lord's Supper",
]

PARTS = [
    {
        "part": 1,
        "title": "Prolegomena",
        "slug": "part-1-prolegomena",
        "chapter_start": 1,
        "chapter_end": 7,
        "description": (
            "The nature and branches of Christian theology, proof of God's existence, "
            "the sources and inspiration of Scripture, and the role of creeds and confessions."
        ),
    },
    {
        "part": 2,
        "title": "Theology Proper",
        "slug": "part-2-theology-proper",
        "chapter_start": 8,
        "chapter_end": 11,
        "description": "The attributes of God, the Holy Trinity, and the divine decrees including predestination.",
    },
    {
        "part": 3,
        "title": "Creation and Providence",
        "slug": "part-3-creation-and-providence",
        "chapter_start": 12,
        "chapter_end": 14,
        "description": "The creation of the world, angels, and the doctrine of divine providence.",
    },
    {
        "part": 4,
        "title": "Anthropology and Hamartiology",
        "slug": "part-4-anthropology-and-hamartiology",
        "chapter_start": 15,
        "chapter_end": 21,
        "description": (
            "The moral constitution of man, his original state, the covenant of works, "
            "the nature of sin, original sin, inability, and the imputation of Adam's sin."
        ),
    },
    {
        "part": 5,
        "title": "Christology",
        "slug": "part-5-christology",
        "chapter_start": 22,
        "chapter_end": 27,
        "description": (
            "The covenant of grace, the person of Christ, His mediatorial office, "
            "the atonement, His intercession, and His mediatorial kingship."
        ),
    },
    {
        "part": 6,
        "title": "Soteriology",
        "slug": "part-6-soteriology",
        "chapter_start": 28,
        "chapter_end": 36,
        "description": (
            "Effectual calling, regeneration, faith, union with Christ, repentance, "
            "justification, adoption, sanctification, and perseverance of the saints."
        ),
    },
    {
        "part": 7,
        "title": "Eschatology",
        "slug": "part-7-eschatology",
        "chapter_start": 37,
        "chapter_end": 40,
        "description": "Death and the state of the soul, the resurrection, the second advent and judgment, and heaven and hell.",
    },
    {
        "part": 8,
        "title": "Ecclesiology and the Sacraments",
        "slug": "part-8-ecclesiology-and-sacraments",
        "chapter_start": 41,
        "chapter_end": 43,
        "description": "The nature of the sacraments, baptism, and the Lord's Supper.",
    },
]


def roman_to_int(s):
    """Convert Roman numeral string to integer."""
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    result, prev = 0, 0
    for ch in reversed(s.upper()):
        val = values.get(ch, 0)
        result += val if val >= prev else -val
        prev = val
    return result


def download_text(url, cache_path):
    """Download plain text from URL if not already cached."""
    if cache_path.exists():
        print(f"Using cached: {cache_path}")
        return cache_path.read_text(encoding="utf-8", errors="replace")
    print(f"Downloading {url} ...")
    with urllib.request.urlopen(url) as resp:
        data = resp.read()
    cache_path.write_bytes(data)
    print(f"Saved {cache_path.stat().st_size / 1024:.0f} KB to {cache_path}")
    return data.decode("utf-8", errors="replace")


def find_body_start(text):
    """
    Skip the table of contents. The body starts immediately after
    the last 'OUTLINES OF THEOLOGY.' heading (which precedes CHAPTER I in the body).
    """
    body_marker = re.search(
        r"OUTLINES\s+OF\s+THEOLOGY\.\s*\n",
        text,
        re.IGNORECASE,
    )
    if body_marker:
        return body_marker.end()
    return 0


def parse_chapters(body_text):
    """
    Split body text into (chapter_num, raw_text) pairs.

    Chapter markers in the DjVu OCR look like:
      "CHAPTER    I. \\n\\n" or "\\n\\n\\nCHAPTER   XIV. \\n\\n"

    We parse the chapter's Roman numeral to get the correct chapter number,
    since some chapters (XV, XXI, XXXVII) are absent from this scan.

    Operates on space-normalized text only (does NOT strip all-caps lines,
    which would destroy the chapter headers).
    """
    # Normalize multiple spaces (DjVu artifact) without removing any lines
    body_norm = re.sub(r"[ \t]{2,}", " ", body_text)

    # Chapter pattern: optional leading newlines + "CHAPTER [roman]." + newline
    # First chapter is at position 0 (no leading newlines)
    chapter_pattern = re.compile(
        r"(?:^|\n{2,})\s*(CHAPTER\s+([IVXLC]+)\.)\s*\n",
        re.MULTILINE,
    )

    matches = list(chapter_pattern.finditer(body_norm))
    print(f"Found {len(matches)} chapter markers in body")

    chapters = []
    for i, match in enumerate(matches):
        roman = match.group(2).upper()
        chapter_num = roman_to_int(roman)
        text_start = match.end()
        text_end = matches[i + 1].start() if i + 1 < len(matches) else len(body_norm)
        raw = body_norm[text_start:text_end]
        chapters.append((chapter_num, raw))

    return chapters


def clean_text(text):
    """Normalize OCR artifacts from DjVu chapter content."""
    # Rejoin hyphenated line breaks (e.g. "re-\nlation" → "relation")
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
    # Remove bare page numbers (a line with only digits)
    text = re.sub(r"^\s*\d{1,4}\s*$", "", text, flags=re.MULTILINE)
    # Remove running headers (all-caps lines like "OUTLINES OF THEOLOGY." or "PREDESTINATION.")
    text = re.sub(r"^\s*[A-Z][A-Z ,.';&:-]{5,}\s*$", "", text, flags=re.MULTILINE)
    # Collapse excess blank lines
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text


def unwrap_paragraphs(text):
    """Unwrap soft-wrapped lines within paragraphs."""
    paragraphs = re.split(r"\n\s*\n", text)
    unwrapped = []
    for para in paragraphs:
        joined = re.sub(r"\s*\n\s*", " ", para).strip()
        if joined:
            unwrapped.append(joined)
    return "\n\n".join(unwrapped).strip()


def main():
    base_dir = Path(__file__).resolve().parent.parent
    cache_path = Path("/tmp/hodge_outlines_raw.txt")
    output_path = base_dir / "data" / "hodge_outlines.json"

    raw = download_text(IA_URL, cache_path)

    body_start = find_body_start(raw)
    print(f"Body starts at character {body_start}")
    body = raw[body_start:]

    # Parse chapters from space-normalized text (before cleaning, which would
    # remove the all-caps CHAPTER headers)
    chapters = parse_chapters(body)

    if not chapters:
        print("ERROR: No chapters found. Inspect /tmp/hodge_outlines_raw.txt.")
        return

    print(f"Parsed {len(chapters)} chapters")

    # Build part lookup by chapter number
    part_by_chapter = {}
    for p in PARTS:
        for ch in range(p["chapter_start"], p["chapter_end"] + 1):
            part_by_chapter[ch] = p

    data_items = []
    for chapter_num, raw_text in chapters:
        part_info = part_by_chapter.get(chapter_num, PARTS[-1])

        cleaned = clean_text(raw_text)
        body_text = unwrap_paragraphs(cleaned)
        title = (
            CHAPTER_TITLES[chapter_num - 1]
            if chapter_num <= len(CHAPTER_TITLES)
            else f"Chapter {chapter_num}"
        )

        data_items.append(
            {
                "Number": chapter_num,
                "Part": part_info["part"],
                "PartTitle": part_info["title"],
                "ChapterTitle": title,
                "Text": body_text,
            }
        )

    output = {
        "Metadata": {
            "Title": "Outlines of Theology",
            "Year": "1879",
            "Authors": ["A.A. Hodge"],
            "SourceUrl": IA_URL,
            "SourceAttribution": "Public Domain (Internet Archive)",
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

    missing = [n for n in range(1, 44) if n not in {d["Number"] for d in data_items}]
    if missing:
        print(f"Missing chapters (absent from OCR scan): {missing}")


if __name__ == "__main__":
    main()
