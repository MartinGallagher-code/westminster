#!/usr/bin/env python3
"""Rebuild ``data/pca_bco/pca_bco.json`` from the PCA's published BCO PDF.

Usage::

    python scripts/parse_pca_bco.py path/to/BCO_2026.pdf \\
        --url https://www.pcaac.org/wp-content/uploads/2026/07/BCO_2026.pdf

The PDF itself is not committed: the Stated Clerk's notice restricts
redistributing it. Download the current edition from https://www.pcaac.org/bco/
(``python manage.py check_bco_update`` reports its URL) and point this script
at it. The script writes ``pca_bco.json`` and ``version.json`` next to each
other in ``data/pca_bco/``.

What the extraction has to undo
-------------------------------
pdfplumber hands back one string per printed line. Read naively, that text
carries the book's typesetting rather than its content:

* every page opens with a running header ("12-5 THE BOOK OF CHURCH ORDER");
* each heading is followed by a 6pt bookmark label repeating it;
* lines amended at the latest Assembly carry a bullet glyph from the Private
  Use Area in the margin;
* paragraphs and lettered sub-clauses are only distinguishable by indentation
  and by where a justified line stops short.

Pages alternate between a 36pt and a 54pt left margin, with a 342pt measure.
Within a section, a line starts a new paragraph when the line before it
stops short of the right margin, when it is indented a full first-line indent
beyond the line before it, or when it opens with a list marker while stepping
back out of a hanging indent. Paragraphs are separated by a blank line, which
is what ``format_confession_sections`` renders as separate ``<p>`` elements.
"""

import argparse
import datetime
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pdfplumber

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "pca_bco"

MEASURE = 342.0          # text width on every page
SHORT_LINE_SLACK = 18.0  # a line ending this far short of the margin ends a paragraph
FIRST_LINE_INDENT = 27.0  # more than a hanging indent (18pt), less than a first-line indent (36pt)

# "56-6 Then the minister..." is printed without its period.
SECTION_RE = re.compile(r"^(\d{1,2})-(\d{1,2})(?:\.\s*|\s+(?=[A-Z(]))")
# Unnumbered divisions inside a chapter ("A. Mission Churches", "Election").
DIVISION_RE = re.compile(r"^(?:[A-Z]\. )?[A-Z][A-Za-z ,]+$")
CHAPTER_RE = re.compile(r"^CHAPTER (\d{1,2})$")
PREFACE_HEAD_RE = re.compile(r"^(I|II|III)\. ([A-Z][A-Z ]+)$")
LIST_MARKER_RE = re.compile(r"^(\(?[a-z]{1,2}\)|[a-z]\.|\(?\d{1,2}\)|\d{1,2}\.|\(?[ivx]{1,4}\)|[ivx]{1,4}\.)\s")
PUA_RE = re.compile("[-]")

PREFACE_TITLES = {
    "I": "The King and Head of the Church",
    "II": "Preliminary Principles",
    "III": "The Constitution Defined",
}
INTRODUCTION_TITLES = {
    "Part III": "Preface to the Directory for Worship",
}
PARTS = [
    ("Part I", "Form of Government"),
    ("Part II", "The Rules of Discipline"),
    ("Part III", "The Directory for the Worship of God"),
]


class Line:
    __slots__ = ("text", "x0", "x1", "top", "size", "bold", "all_bold", "italic",
                 "page", "margin", "markers")

    def __init__(self, raw, page_number, margin):
        chars = [c for c in raw["chars"] if c["text"].strip() and not PUA_RE.match(c["text"])]
        sizes = Counter(round(c["size"], 1) for c in chars)
        self.size = sizes.most_common(1)[0][0] if chars else 0.0
        # Footnote markers are set a size or more below the line's own text
        # ("Questions for Ordination¹", "issue*").
        superscript = [c for c in chars if c["size"] < self.size * 0.8 and (c["text"].isdigit() or c["text"] == "*")]
        self.markers = "".join(c["text"] for c in superscript)
        self.text = _line_text(raw, superscript)
        body = [c for c in chars if c not in superscript] or chars
        self.x0 = min(c["x0"] for c in body) if body else 0.0
        self.x1 = max(c["x1"] for c in body) if body else 0.0
        self.top = min(c["top"] for c in body) if body else 0.0
        fonts = [c["fontname"] for c in body]
        self.bold = bool(fonts) and "Bold" in fonts[0]
        self.all_bold = bool(fonts) and all("Bold" in f for f in fonts)
        self.italic = bool(fonts) and all("Italic" in f for f in fonts)
        self.page = page_number
        self.margin = margin

    @property
    def indent(self):
        return self.x0 - self.margin

    @property
    def is_short(self):
        return self.x1 < self.margin + MEASURE - SHORT_LINE_SLACK

    def __repr__(self):
        return f"<p{self.page} {self.indent:+.0f} {self.text[:60]!r}>"


def _line_text(raw, drop):
    """The line's text without private-use glyphs or the characters in ``drop``.

    pdfplumber infers the spaces between words, so they appear in the line's
    text but not among its characters; every other character of the text is
    one of ``raw['chars']``, in order.
    """
    drop_ids = {id(c) for c in drop}
    chars = iter(raw["chars"])
    out = []
    for ch in raw["text"]:
        if ch.isspace():
            out.append(" ")
            continue
        source = next(chars, None)
        while source is not None and source["text"] != ch:
            source = next(chars, None)
        if source is None:
            # Character stream out of step with the text: keep the text as is.
            return re.sub(r"\s+", " ", PUA_RE.sub("", raw["text"])).strip()
        if id(source) in drop_ids or PUA_RE.match(ch):
            continue
        out.append(ch)
    return re.sub(r"\s+", " ", "".join(out)).strip()


# Scripture cited inline in the text: "(Isaiah 9:6-7)", "Gal. 5:22-23",
# "1 Timothy 3". A trailing ", 25" continues the verse list unless it is the
# numeral of the next book ("Matt. 19:4-6, 1 Cor. 7:2").
_BOOKS = (
    r"Genesis|Gen\.|Exodus|Exod?\.|Leviticus|Lev\.|Numbers|Num\.|Deuteronomy|Deut\.|Joshua|Judges|"
    r"Ruth|Samuel|Sam\.|Kings|Chronicles|Chr\.|Ezra|Nehemiah|Esther|Job|Psalms?|Ps\.|Proverbs|Prov\.|"
    r"Ecclesiastes|Eccl\.|Song of Solomon|Isaiah|Isa\.|Jeremiah|Jer\.|Lamentations|Ezekiel|Daniel|"
    r"Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|"
    r"Matthew|Matt\.|Mark|Luke|John|Acts|Romans|Rom\.|Corinthians|Cor\.|Galatians|Gal\.|"
    r"Ephesians|Eph\.|Philippians|Phil\.|Colossians|Col\.|Thessalonians|Thess\.|Timothy|Tim\.|"
    r"Titus|Philemon|Hebrews|Heb\.|James|Peter|Pet\.|Jude|Revelation|Rev\."
)
SCRIPTURE_RE = re.compile(
    r"(?:\b[123] )?(?:" + _BOOKS + r") \d{1,3}"
    r"(?::\d{1,3}(?:[-\u2013]\d{1,3})?(?:, ?\d{1,3}(?:[-\u2013]\d{1,3})?(?! ?[A-Z]))*)?"
)


def scripture_references(text):
    """The Scripture passages a section cites, in order, without repeats."""
    found = []
    for match in SCRIPTURE_RE.finditer(text):
        reference = match.group(0).replace("\u2013", "-")
        if reference not in found:
            found.append(reference)
    return found


BOOKMARK_RE = re.compile(r"^Chapter (\d{1,2}): (.+)$")
FOOTNOTE_START_RE = re.compile(r"^(\d{1,2}|\*)\s*(?=\S)")


def page_lines(page, page_number, bookmarks=None, footnotes=None):
    """The content lines of a page, with running headers and labels removed.

    The 6pt bookmark labels are dropped from the text, but chapter labels are
    collected into ``bookmarks``: they give each chapter's title on one line,
    where the printed heading may wrap or carry a subtitle (chapter 56).
    Footnotes (9pt, at the foot of the page) are collected into ``footnotes``
    keyed by ``(page, marker)``.
    """
    margin = 36.0 if page_number % 2 == 0 else 54.0
    lines = []
    notes = []
    for raw in page.extract_text_lines(return_chars=True):
        line = Line(raw, page_number, margin)
        if not line.text:
            continue                      # amendment bullet on a line of its own
        if line.size < 8:
            match = BOOKMARK_RE.match(line.text)
            if match and bookmarks is not None:
                bookmarks.setdefault(int(match.group(1)), match.group(2).strip())
            continue                      # 6pt bookmark labels
        if line.size < 12 and line.top < 62:
            continue                      # running header (9pt, occasionally 11pt)
        if line.text.rstrip(".") == "This page intentionally left blank":
            continue
        if line.size < 9.6:
            # Footnote: its first line opens with the marker (set small when
            # numeric, which Line strips into ``markers``).
            marker = line.markers
            if not marker:
                match = FOOTNOTE_START_RE.match(line.text)
                if match and match.group(1) == "*":
                    marker = "*"
                    line.text = line.text[match.end():].strip()
            if marker or not notes:
                notes.append([marker, line.text])
            else:
                notes[-1][1] += " " + line.text
            continue
        lines.append(line)
    if footnotes is not None:
        for marker, text in notes:
            footnotes[(page_number, marker)] = normalise_quotes(text.strip())
    return lines


def starts_paragraph(prev, line, first):
    """Whether ``line`` opens a new paragraph after ``prev``.

    ``first`` is the first line of the paragraph ``prev`` belongs to.
    """
    if prev is None:
        return True
    if prev.is_short:
        return True
    if line.indent > prev.indent + FIRST_LINE_INDENT:
        return True
    if LIST_MARKER_RE.match(line.text):
        # Stepping into or back out of a hanging indent, opening a list
        # after a colon, or a sibling item at the same indent as the item
        # before it ("c. ...;" then "d. ...").
        if abs(line.indent - prev.indent) > 5 or prev.text.endswith(":"):
            return True
        if line.indent > 1 and abs(line.indent - first.indent) < 2 and LIST_MARKER_RE.match(first.text):
            return True
    return False


def join_lines(lines):
    """Reflow printed lines into paragraphs separated by blank lines."""
    paragraphs = []
    current = ""
    prev = first = None
    for line in lines:
        if current and starts_paragraph(prev, line, first):
            paragraphs.append(current)
            current = ""
        if not current:
            current = line.text
            first = line
        elif current.endswith(("-", "\u2014", "/")):
            # Word-processor source with no automatic hyphenation: a hyphen at
            # a line end is a real one ("non-\ncommuning", "BCO 36-\n5").
            current += line.text
        else:
            current += " " + line.text
        prev = line
    if current:
        paragraphs.append(current)
    return "\n\n".join(p.strip() for p in paragraphs)


def normalise_quotes(text):
    return (
        text.replace("‘", "'").replace("’", "'")
        .replace("“", '"').replace("”", '"')
    )


def parse(pdf_path):
    pdf = pdfplumber.open(pdf_path)

    all_lines = []
    bookmarks = {}
    footnotes = {}
    pages = set()
    started = False
    for index, page in enumerate(pdf.pages):
        number = index + 1
        lines = page_lines(page, number, bookmarks, footnotes)
        texts = [line.text for line in lines]
        if not started:
            if "PREFACE TO" in texts:
                started = True
            else:
                continue
        if "APPENDICES" in texts:
            break
        pages.add(number)
        all_lines.extend(lines)
    footnotes = {key: note for key, note in footnotes.items() if key[0] in pages}

    preface = []
    parts = []
    part_intro = {}
    state = None          # 'preface', 'part-heading', 'part-intro', 'chapter-title', 'section'
    current_part = None
    chapter = None
    section = None
    buffer = []

    dropped = []

    def flush():
        nonlocal buffer
        if section is not None:
            section["lines"].extend(buffer)
        else:
            dropped.extend(buffer)
        buffer = []

    pending_division = None

    def is_section_start(candidate):
        return bool(SECTION_RE.match(candidate.text)) and candidate.bold and candidate.indent < 1

    for position, line in enumerate(all_lines):
        text = line.text
        following = all_lines[position + 1] if position + 1 < len(all_lines) else None

        if (line.all_bold and line.size < 12 and line.is_short and DIVISION_RE.match(text)
                and following is not None and is_section_start(following)
                and chapter is not None and state in ("section", "chapter-title")):
            flush()
            pending_division = line
            state = "section"
            continue

        if line.size >= 12.5 and line.bold:
            # 13pt headings: the preface title or a Part title
            flush()
            if text.startswith("PART "):
                label = "Part " + text.split()[1]
                current_part = {"part": label, "title": dict(PARTS)[label], "chapters": []}
                parts.append(current_part)
                section = None
                state = "part-heading"
            continue

        match = PREFACE_HEAD_RE.match(text)
        if match and line.bold and not parts:
            flush()
            numeral = match.group(1)
            section = {
                "reference": f"Preface {numeral}",
                "id": f"preface-{len(preface) + 1}",
                "title": PREFACE_TITLES[numeral],
                "lines": [],
            }
            preface.append(section)
            state = "preface"
            continue

        match = CHAPTER_RE.match(text)
        if match and line.bold:
            flush()
            chapter = {"chapter": int(match.group(1)), "title_lines": [], "sections": []}
            current_part["chapters"].append(chapter)
            section = None
            state = "chapter-title"
            continue

        if state == "part-heading":
            if line.size >= 12.5:
                continue
            state = "part-intro"
            section = part_intro.setdefault(current_part["part"], {"lines": []})

        if state == "chapter-title":
            if line.italic and not SECTION_RE.match(text):
                chapter["title_lines"].append(text)
                continue
            state = "section"

        match = SECTION_RE.match(text)
        if match and is_section_start(line) and chapter is not None:
            ch, num = int(match.group(1)), int(match.group(2))
            if ch == chapter["chapter"] and num == len(chapter["sections"]) + 1:
                flush()
                section = {"number": f"{ch}-{num}", "lines": []}
                if pending_division:
                    section["division"] = pending_division.text
                    section["heading_lines"] = [pending_division]
                    pending_division = None
                chapter["sections"].append(section)
                # Strip the number itself; the site shows it as the reference.
                stripped = SECTION_RE.sub("", text, count=1)
                heading_only = line.is_short and line.all_bold
                line.text = stripped
                if heading_only and stripped:
                    section["title"] = stripped
                    continue
                buffer.append(line)
                continue

        if state == "chapter-title" and chapter is not None:
            continue
        buffer.append(line)

    flush()
    if dropped:
        sys.exit("Lines outside any section: " + "; ".join(repr(line) for line in dropped))

    # Assemble the final structure.
    used_notes = set()

    def finish(sec):
        lines = sec.pop("lines")
        body = normalise_quotes(join_lines(lines))
        notes = []
        for line in sec.pop("heading_lines", []) + lines:
            for marker in ([line.markers] if line.markers == "*" else list(line.markers)):
                key = (line.page, marker)
                if key in footnotes and key not in used_notes:
                    used_notes.add(key)
                    note = footnotes[key]
                    if not re.match(r"(?i)(editor's )?note:", note):
                        note = "Note: " + note
                    notes.append(note)
        sec["text"] = "\n\n".join([body] + notes) if body else "\n\n".join(notes)
        return sec

    out_preface = [finish(s) for s in preface]
    out_parts = []
    for part in parts:
        intro = part_intro.get(part["part"])
        chapters = []
        for ch in part["chapters"]:
            printed = " ".join(ch.pop("title_lines")).strip()
            title = normalise_quotes(bookmarks.get(ch["chapter"], printed))
            sections = [finish(s) for s in ch["sections"]]
            chapters.append({"chapter": ch["chapter"], "title": title, "sections": sections})
        entry = {"part": part["part"], "title": part["title"]}
        if intro and intro["lines"]:
            entry["introduction"] = normalise_quotes(join_lines(intro["lines"]))
            entry["introduction_title"] = INTRODUCTION_TITLES.get(part["part"], "Introduction")
        entry["chapters"] = chapters
        out_parts.append(entry)
    unused = set(footnotes) - used_notes
    if unused:
        sys.exit(f"Footnotes with no marker in the text: {sorted(unused)}")
    return out_preface, out_parts


def edition_details(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        cover = pdf.pages[0].extract_text() or ""
        intro = pdf.pages[1].extract_text() or ""
    assembly = re.search(r"the (\d+)(?:st|nd|rd|th) General Assembly, in ([^\n]+)\n([^\n]+)", cover)
    year = re.search(r"Copyright © (\d{4})", intro)
    if not assembly or not year:
        sys.exit("Could not read the edition details from the PDF cover pages.")
    number = int(assembly.group(1))
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10 if number % 100 not in (11, 12, 13) else 0, "th")
    return {
        "year": int(year.group(1)),
        "assembly": f"{number}{suffix}",
        "place": assembly.group(2).strip(),
        "dates": assembly.group(3).strip(),
    }


def validate(preface, parts):
    problems = []
    if [s["reference"] for s in preface] != ["Preface I", "Preface II", "Preface III"]:
        problems.append("preface sections are not I, II, III")
    expected = 1
    for part in parts:
        for ch in part["chapters"]:
            if ch["chapter"] != expected:
                problems.append(f"chapter {ch['chapter']} found where {expected} was expected")
            expected = ch["chapter"] + 1
            if not ch["title"]:
                problems.append(f"chapter {ch['chapter']} has no title")
            for sec in ch["sections"]:
                if not sec["text"] and not sec.get("title"):
                    problems.append(f"{sec['number']} is empty")
                if PUA_RE.search(sec["text"]):
                    problems.append(f"{sec['number']} still contains a private-use glyph")
                for paragraph in sec["text"].split("\n\n"):
                    if re.match(r"\d{1,2}-\d{1,2}\.? [A-Z]", paragraph):
                        problems.append(f"{sec['number']} swallowed what looks like a section: {paragraph[:40]!r}")
                if "THE BOOK OF CHURCH ORDER" in sec["text"]:
                    problems.append(f"{sec['number']} contains a running header")
    if expected != 64:
        problems.append(f"last chapter was {expected - 1}, expected 63")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--url", required=True, help="where the PDF was downloaded from")
    parser.add_argument("--out", type=Path, default=DATA_DIR)
    args = parser.parse_args()

    details = edition_details(args.pdf)
    preface, parts = parse(args.pdf)
    problems = validate(preface, parts)
    if problems:
        for problem in problems:
            print("PROBLEM:", problem, file=sys.stderr)
        sys.exit(1)

    edition = (
        f"{details['year']} Edition, including amendments approved up to and including "
        f"the {details['assembly']} General Assembly ({details['place']}, {details['dates']})"
    )
    document = {
        "name": "Book of Church Order of the Presbyterian Church in America",
        "abbreviation": "BCO",
        "year": details["year"],
        "edition": edition,
        "copyright": (
            f"Copyright © {details['year']} by the Office of the Stated Clerk of the "
            "General Assembly of the Presbyterian Church in America. All rights reserved."
        ),
        "source_url": args.url,
        "preface": preface,
        "parts": parts,
    }

    # Scripture cited by each section, keyed by its reference; the BCO loader
    # stores these as the section's proof texts so the Scripture index finds
    # them. (The file name matches the ``*proof_texts*.json`` glob that
    # ``build_scripture_index`` hashes.)
    citations = {}
    for sec in preface:
        refs = scripture_references(sec["text"])
        if refs:
            citations[sec["reference"]] = "; ".join(refs)
    for part in parts:
        for ch in part["chapters"]:
            for sec in ch["sections"]:
                refs = scripture_references(sec["text"])
                if refs:
                    citations[sec["number"]] = "; ".join(refs)

    args.out.mkdir(parents=True, exist_ok=True)
    with open(args.out / "pca-bco_proof_texts.json", "w") as f:
        json.dump(citations, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(args.out / "pca_bco.json", "w") as f:
        json.dump(document, f, indent=2, ensure_ascii=False)
        f.write("\n")

    version = {
        "url": args.url,
        "sha256": hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
        "downloaded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "edition": f"{details['year']} Edition",
        "general_assembly": details["assembly"],
    }
    with open(args.out / "version.json", "w") as f:
        json.dump(version, f, indent=2)
        f.write("\n")

    total = len(preface) + sum(len(ch["sections"]) for p in parts for ch in p["chapters"])
    print(f"Wrote {total} sections ({details['year']} edition, {details['assembly']} GA)")


if __name__ == "__main__":
    main()
