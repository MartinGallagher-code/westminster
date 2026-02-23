#!/usr/bin/env python3
"""Generate Canons of Dort proof texts JSON.

Combines:
1. Inline scripture references extracted from the text
2. Footnoted references from the CRC edition (crcna.org)
"""
import json
import re
from pathlib import Path

# CRCNA footnoted proof texts keyed by (chapter_key, section_id)
# These supplement the inline quotations in the text
CRCNA_REFS = {
    # Head 1: Divine Election and Reprobation
    ("1", "A1"): "Rom. 3:19, 23; Rom. 6:23",
    ("1", "A2"): "1 John 4:9; John 3:16",
    ("1", "A3"): "Rom. 10:14-15",
    ("1", "A5"): "Eph. 2:8; Phil. 1:29",
    ("1", "A6"): "Acts 15:18; Eph. 1:11",
    ("1", "A7"): "Eph. 1:4-6; Rom. 8:30",
    ("1", "A9"): "Eph. 1:4",
    ("1", "A10"): "Rom. 9:11-13; Acts 13:48",
    ("1", "A14"): "Acts 20:27; Rom. 11:33-34; Rom. 12:3; Heb. 6:17-18",
    ("1", "A16"): "Isa. 42:3",
    ("1", "A18"): "Rom. 9:20; Matt. 20:15; Rom. 11:33-36",
    ("1", "R1"): "John 17:6; Acts 13:48; Eph. 1:4",
    ("1", "R2"): "Rom. 8:30",
    ("1", "R3"): "2 Tim. 1:9",
    ("1", "R4"): "Eph. 2:3-9",
    ("1", "R5"): "Rom. 9:11-12; Acts 13:48; Eph. 1:4; John 15:16; Rom. 11:6; 1 John 4:10",
    ("1", "R6"): "Matt. 24:24; John 6:39; Rom. 8:30",
    ("1", "R7"): "Luke 10:20; Rom. 8:33",
    ("1", "R8"): "Rom. 9:18; Matt. 13:11; Matt. 11:25-26",
    ("1", "R9"): "Deut. 10:14-15; Matt. 11:21",
    # Head 2: Christ's Death and Human Redemption
    ("2", "R1"): "John 10:15, 27; Isa. 53:10",
    ("2", "R2"): "Heb. 7:22; Heb. 9:15, 17",
    ("2", "R4"): "Rom. 3:24-25",
    ("2", "R7"): "Gal. 2:20; Rom. 8:33-34; John 10:15; John 15:12-13",
    # Head 3/4: Human Corruption, Conversion
    ("3&4", "A9"): "Matt. 13",
    ("3&4", "R1"): "Rom. 5:12, 16; Rom. 6:23",
    ("3&4", "R2"): "Eph. 4:24",
    ("3&4", "R3"): "Jer. 17:9; Eph. 2:3",
    ("3&4", "R4"): "Eph. 2:1, 5; Gen. 6:5; Gen. 8:21; Ps. 51:17; Matt. 5:6",
    ("3&4", "R5"): "Ps. 147:19-20; Acts 14:16; Acts 16:6-7",
    ("3&4", "R6"): "Jer. 31:33; Isa. 44:3; Rom. 5:5; Jer. 31:18",
    ("3&4", "R7"): "Ezek. 36:26",
    ("3&4", "R8"): "Eph. 1:19; 2 Thess. 1:11; 2 Pet. 1:3",
    ("3&4", "R9"): "Rom. 9:16; 1 Cor. 4:7; Phil. 2:13",
    # Head 5: Perseverance of the Saints
    ("4", "A10"): "Rom. 8:16-17",
    ("4", "A11"): "1 Cor. 10:13",
    ("4", "R1"): "Rom. 11:7; Rom. 8:32-35",
    ("4", "R2"): "1 Cor. 1:8",
    ("4", "R3"): "Rom. 5:8-9; 1 John 3:9; John 10:28-29",
    ("4", "R4"): "1 John 5:16-18",
    ("4", "R5"): "Rom. 8:39; 1 John 3:24",
    ("4", "R6"): "1 John 3:2-3",
    ("4", "R7"): "Matt. 13:20; Luke 8:13",
    ("4", "R8"): "1 Pet. 1:23",
    ("4", "R9"): "Luke 22:32; John 17:11, 15",
}


def extract_inline_refs(text):
    """Extract scripture references from parenthetical citations in text."""
    # Match parenthetical text containing scripture book names
    book_pattern = (
        r'(?:Gen|Ex|Lev|Num|Deut|Josh|Judg|Ruth|'
        r'1\s*Sam|2\s*Sam|1\s*Kings|2\s*Kings|'
        r'1\s*Chr|2\s*Chr|Ezra|Neh|Esth|Job|Ps|Prov|Ecc|Song|'
        r'Isa|Jer|Lam|Ezek|Dan|Hos|Joel|Amos|Obad|Jonah|Mic|Nah|Hab|Zeph|Hag|Zech|Mal|'
        r'Matt|Mark|Luke|John|Acts|Rom|'
        r'1\s*Cor|2\s*Cor|Gal|Eph|Phil|Col|'
        r'1\s*Thess|2\s*Thess|1\s*Tim|2\s*Tim|Tit|Philem|Heb|Jas|'
        r'1\s*Pet|2\s*Pet|1\s*John|2\s*John|3\s*John|Jude|Rev)'
    )

    refs = []
    # Find all parenthetical text
    for match in re.finditer(r'"([^"]*?)"?\s*\(([^)]+)\)', text):
        paren_content = match.group(2).strip()
        # Check if it contains a scripture reference
        if re.search(book_pattern, paren_content):
            # Clean up: remove "And verse 23:" style prefixes
            cleaned = re.sub(r'^(?:And\s+)?(?:verse|namely)[^:]*:\s*', '', paren_content)
            refs.append(cleaned.strip())

    # Also find standalone parenthetical refs
    for match in re.finditer(r'\((' + book_pattern + r'[^)]+)\)', text):
        ref = match.group(1).strip()
        if ref not in refs:
            refs.append(ref)

    return refs


def main():
    base_dir = Path(__file__).resolve().parent.parent
    data_path = base_dir / "data" / "canons_of_dort.json"

    with open(data_path) as f:
        data = json.load(f)

    proof_texts = {}
    seq = 0
    for chapter in data["Data"]:
        ch_key = chapter["Chapter"]
        for section in chapter["Sections"]:
            seq += 1
            sid = section["Section"]
            content = section["Content"]

            # Collect references from both sources
            all_refs = set()

            # 1. Extract inline refs from text
            inline = extract_inline_refs(content)
            for ref in inline:
                all_refs.add(ref.strip())

            # 2. Add CRCNA footnoted refs
            crcna_key = (ch_key, sid)
            if crcna_key in CRCNA_REFS:
                for ref in CRCNA_REFS[crcna_key].split(";"):
                    all_refs.add(ref.strip())

            if all_refs:
                # Sort for consistency, putting inline refs first
                proof_texts[str(seq)] = "; ".join(sorted(all_refs, key=lambda r: r.lower()))

    output_path = base_dir / "data" / "dort_proof_texts.json"
    with open(output_path, "w") as f:
        json.dump(proof_texts, f, indent=2)

    print(f"Generated proof texts for {len(proof_texts)}/{seq} sections")
    missing = [str(i) for i in range(1, seq + 1) if str(i) not in proof_texts]
    if missing:
        print(f"Sections without any proof texts: {missing}")
    else:
        print("All sections have proof texts!")


if __name__ == "__main__":
    main()
