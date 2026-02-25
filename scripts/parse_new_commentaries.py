#!/usr/bin/env python3
"""Parse four new Heidelberg Catechism commentaries from Archive.org OCR text."""
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Heidelberg Catechism Lord's Day to Question mapping
LORDS_DAY_QUESTIONS = {
    1: [1, 2], 2: [3, 4, 5], 3: [6, 7, 8], 4: [9, 10, 11],
    5: [12, 13, 14, 15], 6: [16, 17, 18, 19], 7: [20, 21, 22, 23],
    8: [24, 25], 9: [26], 10: [27, 28], 11: [29, 30], 12: [31, 32],
    13: [33, 34], 14: [35, 36], 15: [37, 38, 39],
    16: [40, 41, 42, 43, 44], 17: [45], 18: [46, 47, 48, 49],
    19: [50, 51, 52], 20: [53], 21: [54, 55, 56], 22: [57, 58],
    23: [59, 60, 61], 24: [62, 63, 64], 25: [65, 66, 67, 68],
    26: [69, 70, 71, 72, 73, 74], 27: [75, 76, 77], 28: [78, 79, 80],
    29: [81, 82], 30: [83, 84, 85], 31: [86, 87],
    32: [88, 89, 90, 91], 33: [92, 93], 34: [94, 95],
    35: [96, 97, 98], 36: [99, 100, 101, 102], 37: [103],
    38: [104], 39: [105, 106, 107],
    40: [108, 109, 110, 111, 112], 41: [113, 114, 115], 42: [116],
    43: [117, 118, 119], 44: [120, 121], 45: [122], 46: [123],
    47: [124], 48: [125], 49: [126], 50: [127], 51: [128], 52: [129],
}

QUESTION_TO_LD = {}
for ld, qs in LORDS_DAY_QUESTIONS.items():
    for q in qs:
        QUESTION_TO_LD[q] = ld


def write_question_file(out_dir, q_num, text, append=False):
    """Write commentary text for a single question."""
    outpath = os.path.join(out_dir, f"q{q_num:03d}.txt")
    if append and os.path.exists(outpath):
        with open(outpath, 'a', encoding='utf-8') as f:
            f.write("\n\n" + text)
    else:
        with open(outpath, 'w', encoding='utf-8') as f:
            f.write(text)


def parse_fisher():
    """Parse Fisher's Exercises on the Heidelberg Catechism.

    Structure: Organized by Lord's Day, then Q. N. within each section.
    Pattern: 'Q.  1.  What is thy only comfort...'
    Body starts after the table of contents around line 324.
    """
    print("Parsing Fisher...")
    with open("/tmp/fisher_hc.txt", 'r', encoding='utf-8') as f:
        full_text = f.read()

    out_dir = os.path.join(DATA_DIR, "fisher_heidelberg")
    os.makedirs(out_dir, exist_ok=True)

    # Find the body start - the second occurrence of "EXERCISES" after TOC
    # The TOC ends around "Question 128 and 129" then body starts
    toc_end = full_text.find("Question  128  and  129")
    if toc_end == -1:
        toc_end = full_text.find("Question 128")
    if toc_end == -1:
        toc_end = 2000
    body_start = toc_end

    body_text = full_text[body_start:]

    # Fisher uses: "Q.  1.  What is thy only comfort..."
    # Match Q. followed by number and then the question text starting with capital
    pattern = r'\nQ\.\s+(\d+)\.\s+[A-Z]'

    splits = list(re.finditer(pattern, body_text))

    count = 0
    seen = set()

    for i, match in enumerate(splits):
        q_num = int(match.group(1))
        if q_num < 1 or q_num > 129 or q_num in seen:
            continue
        seen.add(q_num)

        start = match.start()
        # Find next new question
        end = len(body_text)
        for j in range(i + 1, len(splits)):
            next_q = int(splits[j].group(1))
            if next_q not in seen and 1 <= next_q <= 129:
                end = splits[j].start()
                break

        section = body_text[start:end].strip()

        # Clean page header artifacts
        section = re.sub(r'\[Q\.\s+\d+\.?\s*\]?', '', section)
        section = re.sub(r'Q\.\s+\d+\.\]\s*', '', section)
        section = re.sub(r'CATECHETICAL\s+EXERCISES\.?\s*', '', section)
        section = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', section)

        if section and len(section) > 50:
            write_question_file(out_dir, q_num, section)
            count += 1

    print(f"  Wrote {count} Fisher files")
    return count


def parse_whitmer():
    """Parse Whitmer's Notes on the Heidelberg Catechism.

    Structure: Organized by Question number directly.
    Pattern: 'Question 1.  What is thy only comfort...'
    """
    print("Parsing Whitmer...")
    with open("/tmp/whitmer_hc.txt", 'r', encoding='utf-8') as f:
        full_text = f.read()

    out_dir = os.path.join(DATA_DIR, "whitmer_heidelberg")
    os.makedirs(out_dir, exist_ok=True)

    # Whitmer uses: "Question 1.  What is thy only comfort..."
    pattern = r'\n\s*Question\s+(\d+)\.\s+'

    splits = list(re.finditer(pattern, full_text, re.IGNORECASE))

    count = 0
    seen = set()

    for i, match in enumerate(splits):
        q_num = int(match.group(1))
        if q_num < 1 or q_num > 129 or q_num in seen:
            continue
        seen.add(q_num)

        start = match.start()
        end = splits[i + 1].start() if i + 1 < len(splits) else len(full_text)

        section = full_text[start:end].strip()

        # Clean page header artifacts
        section = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', section)
        section = re.sub(r'NOTES\s+ON\s+THE\s*\n?', '', section)

        if section and len(section) > 50:
            write_question_file(out_dir, q_num, section)
            count += 1

    print(f"  Wrote {count} Whitmer files")
    return count


def parse_vanderkemp():
    """Parse Vanderkemp's sermons on the Heidelberg Catechism.

    Structure: 53 sermons organized by Lord's Day across 2 volumes.
    Markers: 'Q. N.' introduces each question's catechism text.
    Page headers: 'I. LORD'S DAY, Q. 1, 2.'
    """
    print("Parsing Vanderkemp...")

    with open("/tmp/vanderkemp_v1.txt", 'r', encoding='utf-8') as f:
        v1_text = f.read()
    with open("/tmp/vanderkemp_v2.txt", 'r', encoding='utf-8') as f:
        v2_text = f.read()

    full_text = v1_text + "\n\n" + v2_text

    out_dir = os.path.join(DATA_DIR, "vanderkemp_heidelberg")
    os.makedirs(out_dir, exist_ok=True)

    # Find question markers: "Q. N." at start of line
    # Also handle OCR garble for Q.1: "Q,  L  -" or "Q,  1."
    pattern = r'\nQ[.,]\s+(\d+)\.\s+'

    splits = list(re.finditer(pattern, full_text))

    # Also try to find Q.1 which is often garbled in OCR
    q1_match = re.search(r'\nQ[,. ]+\s*[L1l]\s*[-. ]+\s*["\']?\s*[VWvw]\s*HAT', full_text)
    if q1_match and not any(int(m.group(1)) == 1 for m in splits if m.group(1).isdigit()):
        # Insert a synthetic match for Q1 at this position
        class FakeMatch:
            def __init__(self, start_pos):
                self._start = start_pos
            def start(self):
                return self._start
            def group(self, n):
                return "1" if n == 1 else None
        splits.insert(0, FakeMatch(q1_match.start()))

    count = 0
    seen = set()
    ld_texts = {}  # lord's day -> accumulated text

    for i, match in enumerate(splits):
        q_num = int(match.group(1))
        if q_num < 1 or q_num > 129 or q_num in seen:
            continue
        seen.add(q_num)

        ld = QUESTION_TO_LD.get(q_num)
        if ld is None:
            continue

        start = match.start()

        # Find next Q. that's in a DIFFERENT Lord's Day
        end = len(full_text)
        for j in range(i + 1, len(splits)):
            next_q_num = int(splits[j].group(1))
            if next_q_num < 1 or next_q_num > 129 or next_q_num in seen:
                continue
            next_ld = QUESTION_TO_LD.get(next_q_num)
            if next_ld is not None and next_ld != ld:
                end = splits[j].start()
                break

        section = full_text[start:end].strip()

        # Remove page header artifacts
        section = re.sub(
            r'[IVXLCivxlc]+\.?\s+LORD.S\s+(?:DAY|PAY),?\s+Q\.\s+[\d,\s]+\.?\s*\d*',
            '', section
        )
        section = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', section)

        if ld in ld_texts:
            ld_texts[ld] += "\n\n" + section
        else:
            ld_texts[ld] = section

    # Write one file per question, using the Lord's Day text
    for ld, text in ld_texts.items():
        text = text.strip()
        if not text or len(text) < 50:
            continue
        for q_num in LORDS_DAY_QUESTIONS[ld]:
            write_question_file(out_dir, q_num, text)
            count += 1

    print(f"  Wrote {count} Vanderkemp files")
    return count


def roman_to_int(s):
    """Convert Roman numeral string to integer."""
    s = s.upper().strip()
    roman_vals = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100}
    result = 0
    for i, c in enumerate(s):
        if c not in roman_vals:
            continue
        val = roman_vals[c]
        if i + 1 < len(s) and s[i + 1] in roman_vals and roman_vals[s[i + 1]] > val:
            result -= val
        else:
            result += val
    return result


def parse_bethune():
    """Parse Bethune's Expository Lectures on the Heidelberg Catechism.

    Structure: 47 lectures organized by Lord's Day.
    Volume 1: Lectures I-XXII (LD 1-19, Q1-52)
    Volume 2: Lectures XXIII-XLVII (LD 19-37, Q50-103)
    """
    print("Parsing Bethune...")

    with open("/tmp/bethune_v1.txt", 'r', encoding='utf-8') as f:
        v1_text = f.read()
    with open("/tmp/bethune_v2.txt", 'r', encoding='utf-8') as f:
        v2_text = f.read()

    full_text = v1_text + "\n\n" + v2_text

    out_dir = os.path.join(DATA_DIR, "bethune_heidelberg")
    os.makedirs(out_dir, exist_ok=True)

    # Lecture -> Lord's Day mapping based on Bethune's TOC
    lecture_to_ld = {
        1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6,
        7: 7, 8: 7,        # LD 7 spans two lectures
        9: 8, 10: 8,       # LD 8 spans two lectures
        11: 9, 12: 10, 13: 11, 14: 12, 15: 13, 16: 14,
        17: 15,
        18: 16, 19: 16,    # LD 16 spans two lectures
        20: 17, 21: 18, 22: 19,
        23: 19,            # Continues LD 19 (Judgment)
        24: 20, 25: 21, 26: 21,  # LD 21 spans two lectures
        27: 22, 28: 22,    # LD 22 spans two lectures
        29: 23, 30: 24,
        31: 25,
        32: 26, 33: 26, 34: 26,  # LD 26 (baptism) spans three lectures
        35: 27,
        36: 28, 37: 28, 38: 28,  # LD 28 spans three lectures
        39: 30,            # Keys of the kingdom (LD 30, Q83-85)
        40: 31, 41: 32, 42: 32,  # LD 32 spans two lectures
        43: 33, 44: 34, 45: 35, 46: 36, 47: 37,
    }

    # Find body start - skip TOC, find "EXPOSITORY LECTUR" header before body
    body_match = re.search(r'EXPOSITORY\s+LECTUR', full_text[3000:])
    if body_match:
        body_start = 3000 + body_match.start()
    else:
        body_start = 0

    body_text = full_text[body_start:]

    # Split by LECTURE markers (various OCR spellings)
    pattern = r'\n\s*(?:LECTTTRE|LECTURK|LECTURE)\s+([IVXLC]+)[\.\s]'

    splits = list(re.finditer(pattern, body_text, re.IGNORECASE))

    count = 0
    seen_lectures = set()
    ld_texts = {}

    for i, match in enumerate(splits):
        lect_num = roman_to_int(match.group(1))

        if lect_num < 1 or lect_num > 47 or lect_num in seen_lectures:
            continue
        seen_lectures.add(lect_num)

        ld = lecture_to_ld.get(lect_num)
        if ld is None:
            continue

        start = match.start()
        end = len(body_text)
        for j in range(i + 1, len(splits)):
            next_num = roman_to_int(splits[j].group(1))
            if next_num > lect_num and next_num not in seen_lectures:
                end = splits[j].start()
                break

        section = body_text[start:end].strip()

        # Clean page header artifacts
        section = re.sub(r'Lect\.\s+[IVXLC]+\.?\]\s*', '', section)
        section = re.sub(r'\[\s*Lect\.\s+[IVXLC]+\.?\s*', '', section)
        section = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', section)

        if ld in ld_texts:
            ld_texts[ld] += "\n\n" + section
        else:
            ld_texts[ld] = section

    # Write one file per question
    for ld, text in ld_texts.items():
        text = text.strip()
        if not text or len(text) < 100:
            continue
        for q_num in LORDS_DAY_QUESTIONS[ld]:
            write_question_file(out_dir, q_num, text)
            count += 1

    print(f"  Wrote {count} Bethune files (covers Q1-103)")
    return count


if __name__ == "__main__":
    # Clear existing output dirs
    for d in ["fisher_heidelberg", "whitmer_heidelberg",
              "vanderkemp_heidelberg", "bethune_heidelberg"]:
        dirpath = os.path.join(DATA_DIR, d)
        if os.path.exists(dirpath):
            for f in os.listdir(dirpath):
                os.remove(os.path.join(dirpath, f))

    parse_fisher()
    parse_whitmer()
    parse_vanderkemp()
    parse_bethune()
    print("\nDone!")
