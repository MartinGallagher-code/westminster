import json
import re
import time
from urllib.request import urlopen, Request
from urllib.error import URLError

from django.core.management.base import BaseCommand
from catechism.models import Catechism, Question, ScripturePassage

# Map abbreviations used in our proof_texts.json to bolls.life book numbers.
# bolls.life uses sequential book numbering: Genesis=1 ... Revelation=66.
BOOK_MAP = {
    # Old Testament
    'gen': 1, 'genesis': 1,
    'ex': 2, 'exod': 2, 'exodus': 2,
    'lev': 3, 'leviticus': 3,
    'num': 4, 'numbers': 4, 'numb': 4,
    'deut': 5, 'deuteronomy': 5,
    'josh': 6, 'joshua': 6,
    'judg': 7, 'judges': 7,
    'ruth': 8,
    '1 sam': 9, '1 samuel': 9,
    '2 sam': 10, '2 samuel': 10,
    '1 kings': 11, '1 kgs': 11,
    '2 kings': 12, '2 kgs': 12,
    '1 chr': 13, '1 chron': 13, '1 chronicles': 13,
    '2 chr': 14, '2 chron': 14, '2 chronicles': 14,
    'ezra': 15,
    'neh': 16, 'nehemiah': 16,
    'esther': 17, 'esth': 17,
    'job': 18,
    'ps': 19, 'psalm': 19, 'psalms': 19, 'psa': 19,
    'prov': 20, 'proverbs': 20,
    'ecc': 21, 'eccl': 21, 'ecclesiastes': 21, 'eccles': 21,
    'song': 22, 'song of solomon': 22, 'cant': 22,
    'isa': 23, 'isaiah': 23,
    'jer': 24, 'jeremiah': 24,
    'lam': 25, 'lamentations': 25,
    'ezek': 26, 'ezekiel': 26,
    'dan': 27, 'daniel': 27,
    'hos': 28, 'hosea': 28,
    'joel': 29,
    'amos': 30,
    'obad': 31, 'obadiah': 31,
    'jonah': 32,
    'mic': 33, 'micah': 33,
    'nah': 34, 'nahum': 34,
    'hab': 35, 'habakkuk': 35,
    'zeph': 36, 'zephaniah': 36,
    'hag': 37, 'haggai': 37,
    'zech': 38, 'zechariah': 38,
    'mal': 39, 'malachi': 39,
    # New Testament
    'matt': 40, 'matthew': 40,
    'mark': 41,
    'luke': 42,
    'john': 43,
    'acts': 44,
    'rom': 45, 'romans': 45,
    '1 cor': 46, '1 corinthians': 46,
    '2 cor': 47, '2 corinthians': 47,
    'gal': 48, 'galatians': 48,
    'eph': 49, 'ephesians': 49, 'ephes': 49,
    'phil': 50, 'philippians': 50,
    'col': 51, 'colossians': 51,
    '1 thess': 52, '1 thessalonians': 52,
    '2 thess': 53, '2 thessalonians': 53,
    '1 tim': 54, '1 timothy': 54,
    '2 tim': 55, '2 timothy': 55,
    'titus': 56, 'tit': 56,
    'philem': 57, 'philemon': 57,
    'heb': 58, 'hebrews': 58,
    'jas': 59, 'james': 59, 'jam': 59,
    '1 pet': 60, '1 peter': 60,
    '2 pet': 61, '2 peter': 61,
    '1 john': 62,
    '2 john': 63,
    '3 john': 64,
    'jude': 65,
    'rev': 66, 'revelation': 66,
}

# Single-chapter books: the number after the book name is a verse, not a chapter.
SINGLE_CHAPTER_BOOKS = {31, 57, 63, 64, 65}  # Obadiah, Philemon, 2 John, 3 John, Jude

# Chapter cache to avoid refetching the same chapter
_chapter_cache = {}


def fetch_chapter(book_num, chapter):
    """Fetch all verses for a chapter from bolls.life, with caching."""
    key = (book_num, chapter)
    if key in _chapter_cache:
        return _chapter_cache[key]

    url = f"https://bolls.life/get-text/ESV/{book_num}/{chapter}/"
    try:
        req = Request(url, headers={'User-Agent': 'WestminsterCatechism/1.0'})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        # Build verse dict: verse_num -> text
        verses = {v['verse']: v['text'].strip() for v in data}
        _chapter_cache[key] = verses
        return verses
    except (URLError, json.JSONDecodeError, KeyError):
        return None


def _normalize_roman_prefix(ref_str):
    """Convert Roman numeral book prefixes (I, II, III) to Arabic (1, 2, 3)."""
    m = re.match(r'^(III|II|I)\s+', ref_str)
    if m:
        roman_to_arabic = {'I': '1', 'II': '2', 'III': '3'}
        ref_str = roman_to_arabic[m.group(1)] + ref_str[m.end(1):]
    return ref_str


def _normalize_ref(ref_str):
    """Normalize non-standard reference suffixes and dashes."""
    # Normalize multi-word book names
    ref_str = re.sub(r'^Song\s+of\s+Solomon\b', 'Song', ref_str, flags=re.IGNORECASE)
    # Strip "throughout"
    ref_str = re.sub(r'\s+throughout$', '', ref_str, flags=re.IGNORECASE)
    # Strip "chap.", "chaps.", "chapters", "chapter"
    ref_str = re.sub(r'\s+chaps?\.?$', '', ref_str, flags=re.IGNORECASE)
    ref_str = re.sub(r'\s+chapters?$', '', ref_str, flags=re.IGNORECASE)
    # Normalize em-dash / en-dash to hyphen
    ref_str = ref_str.replace('\u2013', '-').replace('\u2014', '-')
    # Handle "to the end" by converting to a large verse range
    m = re.search(r':(\d+)\s+to\s+the\s+end$', ref_str, flags=re.IGNORECASE)
    if m:
        start_verse = m.group(1)
        ref_str = ref_str[:m.start()] + ':' + start_verse + '-200'
    return ref_str.strip()


def expand_references(ref_str):
    """
    Expand a complex reference string into a list of simple ones.

    Handles connectors (with/and/&), chapter ranges (Gen. 1-2),
    comma-separated chapters (Rev. 2, 3), and suffixes (throughout,
    chap., to the end).
    """
    # Split on connectors: "with", "and", "&"
    parts = re.split(r',?\s+(?:with|and|&)\s+', ref_str)

    result = []
    for part in parts:
        part = part.strip().rstrip(',').strip()
        if not part:
            continue

        part = _normalize_ref(part)

        # Cross-reference range: "2 Cor. 8-2 Cor. 9" (book on both sides)
        m = re.match(r'^(.+?\s+\d+)\s*-\s*(.+?\s+\d+)$', part)
        if m and ':' not in part:
            result.append(m.group(1).strip())
            result.append(m.group(2).strip())
            continue

        # Simple chapter range: "Gen. 1-2", "Job 38-41" (no colon)
        m = re.match(r'^(.+?)\s+(\d+)\s*-\s*(\d+)$', part)
        if m and ':' not in part:
            book = m.group(1)
            for ch in range(int(m.group(2)), int(m.group(3)) + 1):
                result.append(f"{book} {ch}")
            continue

        # Comma-separated chapters: "Rev. 2, 3" (no colon, not single-chapter book)
        m = re.match(r'^(.+?)\s+(\d+(?:\s*,\s*\d+)+)$', part)
        if m and ':' not in part:
            book = m.group(1)
            book_clean = book.strip().lower().rstrip('.')
            book_num = BOOK_MAP.get(book_clean) or BOOK_MAP.get(book_clean.rstrip('s'))
            if book_num and book_num not in SINGLE_CHAPTER_BOOKS:
                for ch in m.group(2).split(','):
                    result.append(f"{book} {ch.strip()}")
                continue

        result.append(part)

    return result if result else [ref_str]


def parse_reference(ref_str, last_book_num=None):
    """
    Parse a reference string like '1 Cor. 10:31' into (book_num, chapter, verses).
    Returns (book_num, chapter, verse_list) or None if unparseable.

    If ref_str has no book name (e.g. '15:4'), last_book_num is used.
    """
    ref_str = ref_str.strip().rstrip('.')
    ref_str = _normalize_roman_prefix(ref_str)
    # Normalize multi-word book names and dashes
    ref_str = re.sub(r'^Song\s+of\s+Solomon\b', 'Song', ref_str, flags=re.IGNORECASE)
    ref_str = ref_str.replace('\u2013', '-').replace('\u2014', '-')

    # Normalise "ver." / "vv." notation (e.g. "Jude ver. 4" -> "Jude 1:4")
    ref_str = re.sub(r'\s+ve?r\.?\s+', ' 1:', ref_str)
    ref_str = re.sub(r'\s+vv\.?\s+', ' 1:', ref_str)

    # Rewrite single-chapter book references to explicit chapter 1
    # e.g. "Jude 6, 7" -> "Jude 1:6, 7", "3 John 8-10" -> "3 John 1:8-10"
    sc_match = re.match(r'^(\d?\s*\w+)\.?\s+(\d[\d,\s-]*)$', ref_str)
    if sc_match:
        book_check = sc_match.group(1).strip().lower().rstrip('.')
        if BOOK_MAP.get(book_check) in SINGLE_CHAPTER_BOOKS:
            ref_str = f"{sc_match.group(1)} 1:{sc_match.group(2).strip()}"

    # Handle bare chapter:verse references (e.g. "15:4" continuing from previous book)
    bare_match = re.match(r'^(\d+):(.+)$', ref_str)
    if bare_match and last_book_num is not None:
        # Check if this is truly bare (no book name before the number)
        # by verifying the number before ':' doesn't match a book name
        potential_book = ref_str.split(':')[0].strip().lower()
        if potential_book not in BOOK_MAP and potential_book.rstrip('.') not in BOOK_MAP:
            chapter = int(bare_match.group(1))
            verse_part = bare_match.group(2)
            verses = _parse_verses(verse_part)
            return (last_book_num, chapter, verses)

    # Match book name (possibly with leading number), chapter, and optional verses
    m = re.match(
        r'^(\d?\s*\w+)\.?\s+(\d+)(?::(.+))?$',
        ref_str
    )
    if not m:
        return None

    book_raw = m.group(1).strip().lower().rstrip('.')
    chapter = int(m.group(2))
    verse_part = m.group(3)

    # Look up book number
    book_num = BOOK_MAP.get(book_raw)
    if book_num is None:
        book_num = BOOK_MAP.get(book_raw.rstrip('s'))
    if book_num is None:
        return None

    # Single-chapter books: number after book name is a verse, not a chapter
    if book_num in SINGLE_CHAPTER_BOOKS and verse_part is None:
        verses = _parse_verses(str(chapter))
        return (book_num, 1, verses)

    if verse_part is None:
        return (book_num, chapter, None)

    verses = _parse_verses(verse_part)
    return (book_num, chapter, verses)


def _parse_verses(verse_part):
    """Parse verse specifications: '12,19' or '25-28' or '6-8,13'."""
    verses = []
    for part in verse_part.split(','):
        part = part.strip()
        range_match = re.match(r'^(\d+)-(\d+)$', part)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            verses.extend(range(start, end + 1))
        elif re.match(r'^\d+$', part):
            verses.append(int(part))
    return verses if verses else None


def get_verse_text(book_num, chapter, verses):
    """Fetch specific verses from a chapter and return formatted text."""
    chapter_data = fetch_chapter(book_num, chapter)
    if chapter_data is None:
        return None

    if verses is None:
        # Whole chapter - return first few verses with indication
        sorted_verses = sorted(chapter_data.keys())
        if not sorted_verses:
            return None
        texts = []
        for v in sorted_verses:
            texts.append(f"[{v}] {chapter_data[v]}")
        return ' '.join(texts)

    texts = []
    for v in sorted(verses):
        if v in chapter_data:
            texts.append(f"[{v}] {chapter_data[v]}")

    return ' '.join(texts) if texts else None


class Command(BaseCommand):
    help = "Fetch ESV Scripture text for all proof text references"

    def add_arguments(self, parser):
        parser.add_argument(
            '--question', type=int,
            help='Only fetch for a specific question number'
        )
        parser.add_argument(
            '--catechism', type=str, default='',
            help='Only fetch for a specific catechism slug (e.g. wsc, wlc)'
        )
        parser.add_argument(
            '--delay', type=float, default=0.3,
            help='Delay between API requests in seconds (default: 0.3)'
        )
        parser.add_argument(
            '--count-only', action='store_true',
            help='Only print the count of uncached references, then exit'
        )
        parser.add_argument(
            '--audit', action='store_true',
            help='Print a detailed report of missing and unparseable references by document'
        )

    def handle(self, *args, **options):
        question_num = options.get('question')
        cat_slug = options.get('catechism', '')
        delay = options['delay']

        questions = Question.objects.all()
        if cat_slug:
            catechism = Catechism.objects.get(slug=cat_slug)
            questions = questions.filter(catechism=catechism)
        if question_num:
            questions = questions.filter(number=question_num)

        if options.get('count_only'):
            uncached = 0
            for q in questions:
                for ref in q.get_proof_text_list():
                    if not ScripturePassage.objects.filter(reference=ref).exists():
                        uncached += 1
            self.stdout.write(str(uncached))
            return

        if options.get('audit'):
            self._audit(questions)
            return

        total_fetched = 0
        total_failed = 0

        for q in questions:
            refs = q.get_proof_text_list()
            if not refs:
                continue

            self.stdout.write(f"\nQ{q.number}: {len(refs)} references")

            # Expand compound references into simple ones
            expanded_refs = []
            for ref_str in refs:
                expanded_refs.extend(expand_references(ref_str))

            last_book_num = None

            for ref_str in expanded_refs:
                # Skip if already fetched
                if ScripturePassage.objects.filter(reference=ref_str).exists():
                    # Still track the book for continuation references
                    existing = parse_reference(ref_str, last_book_num)
                    if existing:
                        last_book_num = existing[0]
                    self.stdout.write(f"  [cached] {ref_str}")
                    total_fetched += 1
                    continue

                parsed = parse_reference(ref_str, last_book_num)
                if parsed is None:
                    self.stderr.write(
                        self.style.WARNING(f"  [skip] Cannot parse: {ref_str}")
                    )
                    total_failed += 1
                    continue

                book_num, chapter, verses = parsed
                last_book_num = book_num
                text = get_verse_text(book_num, chapter, verses)

                if text:
                    ScripturePassage.objects.update_or_create(
                        reference=ref_str,
                        defaults={'text': text}
                    )
                    preview = text[:80] + '...' if len(text) > 80 else text
                    self.stdout.write(f"  [ok] {ref_str}: {preview}")
                    total_fetched += 1
                else:
                    self.stderr.write(
                        self.style.WARNING(f"  [fail] Could not fetch: {ref_str}")
                    )
                    total_failed += 1

                time.sleep(delay)

        self.stdout.write(self.style.SUCCESS(
            f"\nDone: {total_fetched} fetched, {total_failed} failed"
        ))

    def _audit(self, questions):
        """Print a detailed report of missing and unparseable references."""
        cached_refs = set(
            ScripturePassage.objects.values_list('reference', flat=True)
        )
        # Group by catechism
        by_cat = {}
        for q in questions.select_related('catechism'):
            refs = q.get_proof_text_list()
            if not refs:
                continue
            abbr = q.catechism.abbreviation
            if abbr not in by_cat:
                by_cat[abbr] = {
                    'total': 0, 'cached': 0,
                    'missing': [], 'unparseable': [],
                }
            entry = by_cat[abbr]
            last_book_num = None
            for ref in refs:
                expanded = expand_references(ref)
                for sub_ref in expanded:
                    entry['total'] += 1
                    if sub_ref in cached_refs:
                        parsed = parse_reference(sub_ref, last_book_num)
                        if parsed:
                            last_book_num = parsed[0]
                        entry['cached'] += 1
                    else:
                        parsed = parse_reference(sub_ref, last_book_num)
                        if parsed:
                            last_book_num = parsed[0]
                            entry['missing'].append(
                                f"  {q.catechism.item_prefix}{q.display_number}: {sub_ref}"
                            )
                        else:
                            entry['unparseable'].append(
                                f"  {q.catechism.item_prefix}{q.display_number}: {sub_ref}"
                            )

        grand_total = sum(e['total'] for e in by_cat.values())
        grand_cached = sum(e['cached'] for e in by_cat.values())
        grand_missing = sum(len(e['missing']) for e in by_cat.values())
        grand_unparse = sum(len(e['unparseable']) for e in by_cat.values())

        self.stdout.write("\nScripture Proof Text Audit")
        self.stdout.write(f"{'=' * 50}")

        for abbr in sorted(by_cat):
            e = by_cat[abbr]
            missing_count = len(e['missing'])
            unparse_count = len(e['unparseable'])
            self.stdout.write(
                f"\n{abbr}: {e['cached']}/{e['total']} cached"
                f" ({missing_count} missing, {unparse_count} unparseable)"
            )
            for line in e['missing']:
                self.stdout.write(self.style.WARNING(line))
            for line in e['unparseable']:
                self.stdout.write(self.style.ERROR(line))

        self.stdout.write(f"\n{'=' * 50}")
        self.stdout.write(
            f"Total: {grand_cached}/{grand_total} cached"
            f" ({grand_missing} missing, {grand_unparse} unparseable)"
        )
