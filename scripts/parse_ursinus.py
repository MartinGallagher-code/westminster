"""
Parse Zacharias Ursinus's Commentary on the Heidelberg Catechism
from Internet Archive DjVu OCR text.

Downloads the 1888 4th American Edition (Williard translation) and
extracts per-question commentary text into data/ursinus_heidelberg/.

The text is organized by Lord's Day (52 total), with 129 questions.
Some questions share exposition blocks.
"""

import os
import re
import sys
import urllib.request
from pathlib import Path

# DjVu text URL from Internet Archive (1888 4th American Edition)
URSINUS_URL = (
    "https://archive.org/download/commentaryofzach00ursiuoft/"
    "commentaryofzach00ursiuoft_djvu.txt"
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

# Known OCR misreads of question numbers in the DjVu text
# Maps (OCR'd number, line context) -> actual question number
# We'll fix these by checking sequential order
OCR_FIXES = {
    82: 32,   # "Question 82. But why art thou called a Christian"
    84: 34,   # "Question 84. Wherefore callest thou him our Lord"
    87: 37,   # "Question 87. What dost thou understand bj the words"
    7: 67,    # "Question 07. Are both word and sacraments" (at line ~22811)
}


def download_text(cache_path):
    """Download DjVu text from Internet Archive if not cached."""
    if cache_path.exists():
        print(f"Using cached text: {cache_path}")
        return cache_path.read_text(encoding="utf-8", errors="replace")

    print(f"Downloading from {URSINUS_URL}...")
    urllib.request.urlretrieve(URSINUS_URL, cache_path)
    print(f"Downloaded {cache_path.stat().st_size / 1024:.0f} KB")
    return cache_path.read_text(encoding="utf-8", errors="replace")


def find_content_start(text):
    """Find where the actual catechism commentary begins (after preface/intro)."""
    # Look for "FIRST LORD'S DAY" which marks the start of Q1
    match = re.search(r'FIRST\s+LORD.S\s+DAY', text)
    if match:
        return match.start()
    raise ValueError("Could not find 'FIRST LORD'S DAY' marker")


def find_question_positions(text):
    """
    Find all 'Question N.' markers and return list of (position, question_number).
    Handles OCR errors in question numbers.
    """
    # Match "Question N." with a number
    pattern = re.compile(r'^(Question\s+(\d+)\.\s+)', re.MULTILINE)
    raw_positions = []

    for m in pattern.finditer(text):
        pos = m.start()
        num = int(m.group(2))
        raw_positions.append((pos, num))

    # Also find "Question." without a number (OCR dropped it)
    # These appear in Lord's Day sections where context tells us the number
    bare_pattern = re.compile(r'^(Question\.\s+)', re.MULTILINE)
    for m in bare_pattern.finditer(text):
        pos = m.start()
        raw_positions.append((pos, 0))  # 0 = unknown, will be fixed below

    # Sort by position
    raw_positions.sort(key=lambda x: x[0])

    # Fix OCR errors
    # Strategy: walk through in order and fix numbers that are clearly wrong
    fixed = []
    expected_next = 1

    for pos, num in raw_positions:
        if num == 0:
            # Bare "Question." with no number - assign expected
            actual = expected_next
        elif num in OCR_FIXES and abs(OCR_FIXES[num] - expected_next) < abs(num - expected_next):
            actual = OCR_FIXES[num]
        elif abs(num - expected_next) <= 2:
            actual = num
        elif num < expected_next and num + 100 >= expected_next:
            # e.g., "07" when we expect 67
            for offset in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
                candidate = num + offset
                if abs(candidate - expected_next) <= 2:
                    actual = candidate
                    break
            else:
                actual = num
        else:
            actual = num

        fixed.append((pos, actual))
        expected_next = actual + 1

    return fixed


def clean_commentary_text(text):
    """Clean OCR artifacts from commentary text."""
    # Remove underscores (used for emphasis in DjVu)
    text = re.sub(r'_', '', text)
    # Remove bare page numbers
    text = re.sub(r'^\s*\d{1,3}\s*$', '', text, flags=re.MULTILINE)
    # Remove page headers like "THE QUESTION OF COMFORT.  19"
    text = re.sub(r'^\s*[A-Z][A-Z\s,.\'-]+\s+\d{1,3}\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d{1,3}\s+[A-Z][A-Z\s,.\'-]+$', '', text, flags=re.MULTILINE)
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
    Extract the EXPOSITION section from a question block.
    The block contains: Question text, Answer text, then EXPOSITION.
    """
    # Find "EXPOSITION." marker
    expo_match = re.search(r'EXPOSITION\.?\s*\n', block_text, re.IGNORECASE)
    if expo_match:
        return block_text[expo_match.end():]

    # Fallback: find first paragraph break after Answer
    answer_match = re.search(r'Answer\.', block_text, re.IGNORECASE)
    if answer_match:
        # Skip the answer text and find commentary start
        after_answer = block_text[answer_match.start():]
        # Find double newline after answer
        para_break = re.search(r'\n\s*\n\s*[A-Z]', after_answer[100:])
        if para_break:
            return after_answer[100 + para_break.start():]

    return None


def parse_ursinus(text):
    """
    Parse the full Ursinus text into per-question commentary blocks.
    Returns dict of {question_number: commentary_text}.
    """
    content_start = find_content_start(text)
    text = text[content_start:]

    positions = find_question_positions(text)
    print(f"Found {len(positions)} question markers")

    # Check which questions we found
    found_questions = set(p[1] for p in positions)
    all_questions = set(range(1, 130))
    missing = sorted(all_questions - found_questions)
    if missing:
        print(f"Missing question markers: {missing}")

    commentaries = {}

    for i, (pos, qnum) in enumerate(positions):
        # Get text from this question to the next
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

    # For missing questions, try to assign from the Lord's Day structure
    # If a question is missing but its Lord's Day siblings have commentary,
    # the missing question likely shares the exposition
    for ld_num, questions in LORDS_DAY_QUESTIONS.items():
        missing_in_ld = [q for q in questions if q not in commentaries]
        present_in_ld = [q for q in questions if q in commentaries]

        if missing_in_ld and present_in_ld:
            # Use the first present question's commentary for missing ones
            shared_text = commentaries[present_in_ld[0]]
            for mq in missing_in_ld:
                commentaries[mq] = shared_text
                print(f"  Q{mq}: shared from Q{present_in_ld[0]} (Lord's Day {ld_num})")

    return commentaries


def main():
    base_dir = Path(__file__).resolve().parent.parent
    cache_path = Path("/tmp/ursinus_raw.txt")
    output_dir = base_dir / "data" / "ursinus_heidelberg"

    text = download_text(cache_path)
    commentaries = parse_ursinus(text)

    print(f"\nExtracted commentary for {len(commentaries)} questions")

    # Write per-question files
    output_dir.mkdir(parents=True, exist_ok=True)
    for qnum in sorted(commentaries.keys()):
        filepath = output_dir / f"q{qnum:03d}.txt"
        filepath.write_text(commentaries[qnum], encoding="utf-8")

    print(f"Wrote {len(commentaries)} files to {output_dir}")

    # Report stats
    total_chars = sum(len(v) for v in commentaries.values())
    print(f"Total commentary text: {total_chars:,} characters")

    still_missing = sorted(set(range(1, 130)) - set(commentaries.keys()))
    if still_missing:
        print(f"Still missing: {still_missing}")
    else:
        print("All 129 questions have commentary!")


if __name__ == "__main__":
    main()
