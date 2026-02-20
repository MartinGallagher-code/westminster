import json
import re
import time
from urllib.request import urlopen, Request
from urllib.error import URLError

from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.models import Catechism, Question, ScripturePassage

# Map abbreviations used in our proof_texts.json to bolls.life book numbers.
# bolls.life uses sequential book numbering: Genesis=1 ... Revelation=66.
BOOK_MAP = {
    # Old Testament
    'gen': 1, 'genesis': 1,
    'ex': 2, 'exod': 2, 'exodus': 2,
    'lev': 3, 'leviticus': 3,
    'num': 4, 'numbers': 4,
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
    'ecc': 21, 'eccl': 21, 'ecclesiastes': 21,
    'song': 22, 'song of solomon': 22,
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
    'eph': 49, 'ephesians': 49,
    'phil': 50, 'philippians': 50,
    'col': 51, 'colossians': 51,
    '1 thess': 52, '1 thessalonians': 52,
    '2 thess': 53, '2 thessalonians': 53,
    '1 tim': 54, '1 timothy': 54,
    '2 tim': 55, '2 timothy': 55,
    'titus': 56,
    'philem': 57, 'philemon': 57,
    'heb': 58, 'hebrews': 58,
    'jas': 59, 'james': 59,
    '1 pet': 60, '1 peter': 60,
    '2 pet': 61, '2 peter': 61,
    '1 john': 62,
    '2 john': 63,
    '3 john': 64,
    'jude': 65,
    'rev': 66, 'revelation': 66,
}

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
    except (URLError, json.JSONDecodeError, KeyError) as e:
        return None


def parse_reference(ref_str, last_book_num=None):
    """
    Parse a reference string like '1 Cor. 10:31' into (book_num, chapter, verses).
    Returns (book_num, chapter, verse_list) or None if unparseable.

    If ref_str has no book name (e.g. '15:4'), last_book_num is used.
    """
    ref_str = ref_str.strip().rstrip('.')

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

        total_fetched = 0
        total_failed = 0

        for q in questions:
            refs = q.get_proof_text_list()
            if not refs:
                continue

            self.stdout.write(f"\nQ{q.number}: {len(refs)} references")

            # Expand "with" references: "Heb. 12:25 with 2 Cor. 13:3" -> two refs
            expanded_refs = []
            for ref_str in refs:
                if ' with ' in ref_str:
                    parts = ref_str.split(' with ')
                    expanded_refs.extend(p.strip() for p in parts)
                else:
                    expanded_refs.append(ref_str)

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
