import re
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Question, BibleBook, ScriptureIndex

# Canonical list of Bible books: (number, name, abbreviation, slug, testament)
BIBLE_BOOKS = [
    (1, 'Genesis', 'Gen.', 'genesis', 'OT'),
    (2, 'Exodus', 'Ex.', 'exodus', 'OT'),
    (3, 'Leviticus', 'Lev.', 'leviticus', 'OT'),
    (4, 'Numbers', 'Num.', 'numbers', 'OT'),
    (5, 'Deuteronomy', 'Deut.', 'deuteronomy', 'OT'),
    (6, 'Joshua', 'Josh.', 'joshua', 'OT'),
    (7, 'Judges', 'Judg.', 'judges', 'OT'),
    (8, 'Ruth', 'Ruth', 'ruth', 'OT'),
    (9, '1 Samuel', '1 Sam.', '1-samuel', 'OT'),
    (10, '2 Samuel', '2 Sam.', '2-samuel', 'OT'),
    (11, '1 Kings', '1 Kings', '1-kings', 'OT'),
    (12, '2 Kings', '2 Kings', '2-kings', 'OT'),
    (13, '1 Chronicles', '1 Chr.', '1-chronicles', 'OT'),
    (14, '2 Chronicles', '2 Chr.', '2-chronicles', 'OT'),
    (15, 'Ezra', 'Ezra', 'ezra', 'OT'),
    (16, 'Nehemiah', 'Neh.', 'nehemiah', 'OT'),
    (17, 'Esther', 'Esth.', 'esther', 'OT'),
    (18, 'Job', 'Job', 'job', 'OT'),
    (19, 'Psalms', 'Ps.', 'psalms', 'OT'),
    (20, 'Proverbs', 'Prov.', 'proverbs', 'OT'),
    (21, 'Ecclesiastes', 'Eccl.', 'ecclesiastes', 'OT'),
    (22, 'Song of Solomon', 'Song', 'song-of-solomon', 'OT'),
    (23, 'Isaiah', 'Isa.', 'isaiah', 'OT'),
    (24, 'Jeremiah', 'Jer.', 'jeremiah', 'OT'),
    (25, 'Lamentations', 'Lam.', 'lamentations', 'OT'),
    (26, 'Ezekiel', 'Ezek.', 'ezekiel', 'OT'),
    (27, 'Daniel', 'Dan.', 'daniel', 'OT'),
    (28, 'Hosea', 'Hos.', 'hosea', 'OT'),
    (29, 'Joel', 'Joel', 'joel', 'OT'),
    (30, 'Amos', 'Amos', 'amos', 'OT'),
    (31, 'Obadiah', 'Obad.', 'obadiah', 'OT'),
    (32, 'Jonah', 'Jonah', 'jonah', 'OT'),
    (33, 'Micah', 'Mic.', 'micah', 'OT'),
    (34, 'Nahum', 'Nah.', 'nahum', 'OT'),
    (35, 'Habakkuk', 'Hab.', 'habakkuk', 'OT'),
    (36, 'Zephaniah', 'Zeph.', 'zephaniah', 'OT'),
    (37, 'Haggai', 'Hag.', 'haggai', 'OT'),
    (38, 'Zechariah', 'Zech.', 'zechariah', 'OT'),
    (39, 'Malachi', 'Mal.', 'malachi', 'OT'),
    (40, 'Matthew', 'Matt.', 'matthew', 'NT'),
    (41, 'Mark', 'Mark', 'mark', 'NT'),
    (42, 'Luke', 'Luke', 'luke', 'NT'),
    (43, 'John', 'John', 'john', 'NT'),
    (44, 'Acts', 'Acts', 'acts', 'NT'),
    (45, 'Romans', 'Rom.', 'romans', 'NT'),
    (46, '1 Corinthians', '1 Cor.', '1-corinthians', 'NT'),
    (47, '2 Corinthians', '2 Cor.', '2-corinthians', 'NT'),
    (48, 'Galatians', 'Gal.', 'galatians', 'NT'),
    (49, 'Ephesians', 'Eph.', 'ephesians', 'NT'),
    (50, 'Philippians', 'Phil.', 'philippians', 'NT'),
    (51, 'Colossians', 'Col.', 'colossians', 'NT'),
    (52, '1 Thessalonians', '1 Thess.', '1-thessalonians', 'NT'),
    (53, '2 Thessalonians', '2 Thess.', '2-thessalonians', 'NT'),
    (54, '1 Timothy', '1 Tim.', '1-timothy', 'NT'),
    (55, '2 Timothy', '2 Tim.', '2-timothy', 'NT'),
    (56, 'Titus', 'Titus', 'titus', 'NT'),
    (57, 'Philemon', 'Philem.', 'philemon', 'NT'),
    (58, 'Hebrews', 'Heb.', 'hebrews', 'NT'),
    (59, 'James', 'Jas.', 'james', 'NT'),
    (60, '1 Peter', '1 Pet.', '1-peter', 'NT'),
    (61, '2 Peter', '2 Pet.', '2-peter', 'NT'),
    (62, '1 John', '1 John', '1-john', 'NT'),
    (63, '2 John', '2 John', '2-john', 'NT'),
    (64, '3 John', '3 John', '3-john', 'NT'),
    (65, 'Jude', 'Jude', 'jude', 'NT'),
    (66, 'Revelation', 'Rev.', 'revelation', 'NT'),
]

# Map abbreviations to book numbers (reuses logic from fetch_scripture.py)
ABBREV_MAP = {
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
    'titus': 56, 'tit': 56,
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


def extract_book_number(ref_str):
    """Extract the Bible book number from a reference string like 'Rom. 2:14, 15'."""
    ref_str = ref_str.strip()
    if not ref_str:
        return None

    # Handle "with" references - take the first part
    if ' with ' in ref_str:
        ref_str = ref_str.split(' with ')[0].strip()

    # Try to match a book name pattern: optional number + letters, then chapter:verse
    m = re.match(r'^(\d?\s*\w+)\.?\s+\d', ref_str)
    if not m:
        return None

    book_raw = m.group(1).strip().lower().rstrip('.')

    book_num = ABBREV_MAP.get(book_raw)
    if book_num is None:
        book_num = ABBREV_MAP.get(book_raw.rstrip('s'))
    return book_num


class Command(BaseCommand):
    help = "Build the scripture index from proof text references"

    def add_arguments(self, parser):
        parser.add_argument(
            '--rebuild', action='store_true',
            help='Clear existing index before rebuilding'
        )

    def handle(self, *args, **options):
        # Skip if proof text source files haven't changed
        proof_paths = [
            settings.BASE_DIR / "data" / "proof_texts.json",
            settings.BASE_DIR / "data" / "wlc_proof_texts.json",
            settings.BASE_DIR / "data" / "wcf_proof_texts.json",
        ]
        existing = [p for p in proof_paths if p.exists()]
        if not options['rebuild'] and data_is_current("scripture-index", *existing):
            self.stdout.write("Scripture index unchanged, skipping.")
            return

        # 1. Ensure all BibleBook rows exist
        for num, name, abbrev, slug, testament in BIBLE_BOOKS:
            BibleBook.objects.update_or_create(
                book_number=num,
                defaults={
                    'name': name,
                    'slug': slug,
                    'abbreviation': abbrev,
                    'testament': testament,
                }
            )
        self.stdout.write(f"Ensured {len(BIBLE_BOOKS)} Bible books exist")

        # 2. Optionally clear existing index
        if options['rebuild']:
            deleted, _ = ScriptureIndex.objects.all().delete()
            self.stdout.write(f"Cleared {deleted} existing index entries")

        # 3. Build index from all questions with proof texts
        book_cache = {b.book_number: b for b in BibleBook.objects.all()}
        created_count = 0
        skipped_count = 0
        last_book_num = None

        questions = Question.objects.exclude(
            proof_texts=''
        ).select_related('catechism')

        for q in questions:
            refs = q.get_proof_text_list()
            last_book_num = None

            for ref_str in refs:
                # Handle "with" references
                parts = [ref_str]
                if ' with ' in ref_str:
                    parts = [p.strip() for p in ref_str.split(' with ')]

                for part in parts:
                    book_num = extract_book_number(part)

                    # For bare references like "15:4", use last book
                    if book_num is None:
                        bare = re.match(r'^(\d+):(.+)$', part.strip())
                        if bare and last_book_num is not None:
                            book_num = last_book_num

                    if book_num is None:
                        skipped_count += 1
                        continue

                    last_book_num = book_num
                    book = book_cache.get(book_num)
                    if not book:
                        skipped_count += 1
                        continue

                    _, created = ScriptureIndex.objects.get_or_create(
                        question=q,
                        reference=ref_str,
                        defaults={'book': book}
                    )
                    if created:
                        created_count += 1

        mark_data_current("scripture-index", *existing)
        self.stdout.write(self.style.SUCCESS(
            f"Created {created_count} index entries ({skipped_count} refs skipped)"
        ))
