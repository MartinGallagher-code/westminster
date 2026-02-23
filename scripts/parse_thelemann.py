"""
Parse Otto Thelemann's "An Aid to the Heidelberg Catechism" (1896)
from Internet Archive DjVu OCR text.

Downloads the text and extracts per-question commentary into
data/thelemann_heidelberg/.
"""

import re
import urllib.request
from pathlib import Path

THELEMANN_URL = (
    "https://archive.org/download/aidtoheidelbergc00thel/"
    "aidtoheidelbergc00thel_djvu.txt"
)

# Standard Heidelberg Catechism Lord's Day -> Question mapping
LORDS_DAY_QUESTIONS = {
    1: [1, 2], 2: [3, 4, 5], 3: [6, 7, 8], 4: [9, 10, 11],
    5: [12, 13, 14, 15], 6: [16, 17, 18, 19], 7: [20, 21],
    8: [22, 23, 24, 25], 9: [26], 10: [27, 28],
    11: [29, 30], 12: [31, 32], 13: [33, 34], 14: [35, 36],
    15: [37, 38, 39], 16: [40, 41, 42, 43, 44], 17: [45],
    18: [46, 47, 48, 49], 19: [50, 51, 52], 20: [53],
    21: [54, 55, 56], 22: [57, 58], 23: [59, 60, 61, 62],
    24: [63, 64], 25: [65, 66, 67, 68], 26: [69, 70, 71],
    27: [72, 73, 74], 28: [75, 76, 77], 29: [78, 79],
    30: [80, 81, 82], 31: [83, 84, 85], 32: [86, 87],
    33: [88, 89, 90, 91], 34: [92, 93, 94, 95],
    35: [96, 97, 98], 36: [99, 100], 37: [101, 102],
    38: [103], 39: [104], 40: [105, 106, 107],
    41: [108, 109], 42: [110, 111], 43: [112],
    44: [113, 114, 115], 45: [116, 117, 118, 119],
    46: [120, 121], 47: [122], 48: [123], 49: [124],
    50: [125], 51: [126], 52: [127, 128, 129],
}


def download_text(cache_path):
    """Download DjVu text from Internet Archive if not cached."""
    if cache_path.exists():
        print(f"Using cached text: {cache_path}")
        return cache_path.read_text(encoding="utf-8", errors="replace")

    print(f"Downloading from {THELEMANN_URL}...")
    urllib.request.urlretrieve(THELEMANN_URL, cache_path)
    print(f"Downloaded {cache_path.stat().st_size / 1024:.0f} KB")
    return cache_path.read_text(encoding="utf-8", errors="replace")


def find_content_start(text):
    """Find where the actual commentary begins (after prefaces/TOC)."""
    # Look for the first "Question 1." that starts the actual commentary
    # (skip table of contents references like "Question 1  Page 1")
    match = re.search(r'^Question\s+1\.\s*$', text, re.MULTILINE)
    if match:
        return match.start()
    # Fallback: find "Question 1." followed by question text
    match = re.search(r'^Question\s+1\.\s*\n', text, re.MULTILINE)
    if match:
        return match.start()
    raise ValueError("Could not find start of commentary")


def find_question_positions(text):
    """
    Find all 'Question N.' markers and return list of (position, question_number).
    Filters out table-of-contents entries and inline references.
    """
    # Match "Question N." or "Question N" at start of line
    pattern = re.compile(
        r'^Question\s+(\d+)[.\s]*$',
        re.MULTILINE
    )
    raw_positions = []

    for m in pattern.finditer(text):
        num = int(m.group(1))
        if 1 <= num <= 129:
            raw_positions.append((m.start(), num))

    # Also catch "Question N." followed by newline (OCR may not have period)
    pattern2 = re.compile(
        r'^Question\s+(\d+)\.\s*\n',
        re.MULTILINE
    )
    seen_positions = set(p[0] for p in raw_positions)
    for m in pattern2.finditer(text):
        if m.start() not in seen_positions:
            num = int(m.group(1))
            if 1 <= num <= 129:
                raw_positions.append((m.start(), num))

    # Also catch "Question N-" pattern (OCR artifact for Q57)
    pattern3 = re.compile(
        r'^Question\s+(\d+)[-]\s*$',
        re.MULTILINE
    )
    seen_positions = set(p[0] for p in raw_positions)
    for m in pattern3.finditer(text):
        if m.start() not in seen_positions:
            num = int(m.group(1))
            if 1 <= num <= 129:
                raw_positions.append((m.start(), num))

    # Sort by position and deduplicate
    raw_positions.sort(key=lambda x: x[0])

    # Deduplicate same question number (keep first)
    seen_nums = set()
    deduped = []
    for pos, num in raw_positions:
        if num not in seen_nums:
            seen_nums.add(num)
            deduped.append((pos, num))

    return deduped


def clean_commentary_text(text):
    """Clean OCR artifacts from commentary text."""
    # Remove underscores
    text = re.sub(r'_', '', text)
    # Remove bare page numbers
    text = re.sub(r'^\s*\d{1,3}\s*$', '', text, flags=re.MULTILINE)
    # Remove page headers like "THE HEIDELBERG CATECHISM.  123"
    text = re.sub(r'^\s*THE\s+HEIDELBE[A-Z]+\s+[A-Z]+[.\s]*\d*\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\s+THE\s+HEIDELBE[A-Z]+\s+[A-Z]+[.\s]*$', '', text, flags=re.MULTILINE)
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


def extract_exposition(block_text):
    """
    Extract the commentary section from a question block.
    Strip the question text and answer, return the commentary.
    """
    # Find the Answer section
    answer_match = re.search(r'(?:Answer|xAlNswer|An[s]wer)\s*\.', block_text, re.IGNORECASE)
    if not answer_match:
        # Some blocks may start directly with commentary
        # Skip the question header line
        skip = re.search(r'\n\s*\n', block_text[20:])
        if skip:
            return block_text[20 + skip.start():]
        return block_text

    # Skip past the answer text to find the start of commentary.
    # The answer text typically ends with a double newline followed by
    # a heading (roman numeral, numbered point, or uppercase heading).
    after_answer = block_text[answer_match.start():]

    # Look for the start of commentary: a double newline after the answer,
    # followed by commentary content (heading, numbered point, etc.)
    # First try to find a clear section heading
    commentary_start = re.search(
        r'\n\s*\n\s*(?:I\.\s|1\.\s|[A-Z][A-Z\s]{3,}[A-Z])',
        after_answer[50:]  # skip at least 50 chars into the answer
    )
    if commentary_start:
        return after_answer[50 + commentary_start.start():]

    # Fallback: second paragraph break after the answer starts
    breaks = list(re.finditer(r'\n\s*\n', after_answer[50:]))
    if len(breaks) >= 1:
        return after_answer[50 + breaks[0].start():]

    return None


def parse_thelemann(text):
    """
    Parse the full Thelemann text into per-question commentary blocks.
    Returns dict of {question_number: commentary_text}.
    """
    content_start = find_content_start(text)
    text = text[content_start:]

    positions = find_question_positions(text)
    print(f"Found {len(positions)} question markers")

    found_questions = set(p[1] for p in positions)
    all_questions = set(range(1, 130))
    missing = sorted(all_questions - found_questions)
    if missing:
        print(f"Missing question markers: {missing}")

    commentaries = {}

    for i, (pos, qnum) in enumerate(positions):
        if i + 1 < len(positions):
            next_pos = positions[i + 1][0]
        else:
            next_pos = len(text)

        block = text[pos:next_pos]
        exposition = extract_exposition(block)

        if exposition:
            cleaned = clean_commentary_text(exposition)
            if cleaned and len(cleaned) >= 50:
                commentaries[qnum] = cleaned

    # For missing questions, share commentary from Lord's Day siblings
    for ld_num, questions in LORDS_DAY_QUESTIONS.items():
        missing_in_ld = [q for q in questions if q not in commentaries]
        present_in_ld = [q for q in questions if q in commentaries]

        if missing_in_ld and present_in_ld:
            shared_text = commentaries[present_in_ld[0]]
            for mq in missing_in_ld:
                commentaries[mq] = shared_text
                print(f"  Q{mq}: shared from Q{present_in_ld[0]} (Lord's Day {ld_num})")

    return commentaries


def main():
    base_dir = Path(__file__).resolve().parent.parent
    cache_path = Path("/tmp/thelemann_raw.txt")
    output_dir = base_dir / "data" / "thelemann_heidelberg"

    text = download_text(cache_path)
    commentaries = parse_thelemann(text)

    print(f"\nExtracted commentary for {len(commentaries)} questions")

    output_dir.mkdir(parents=True, exist_ok=True)
    for qnum in sorted(commentaries.keys()):
        filepath = output_dir / f"q{qnum:03d}.txt"
        filepath.write_text(commentaries[qnum], encoding="utf-8")

    print(f"Wrote {len(commentaries)} files to {output_dir}")

    total_chars = sum(len(v) for v in commentaries.values())
    print(f"Total commentary text: {total_chars:,} characters")

    still_missing = sorted(set(range(1, 130)) - set(commentaries.keys()))
    if still_missing:
        print(f"Still missing: {still_missing}")
    else:
        print("All 129 questions have commentary!")


if __name__ == "__main__":
    main()
