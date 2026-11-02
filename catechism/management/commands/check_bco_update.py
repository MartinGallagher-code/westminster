"""Report whether the PCA has published a BCO newer than the one loaded.

The PCA publishes each edition at a new URL (``.../2025/08/BCO2025-1.pdf``,
``.../2026/07/BCO_2026.pdf``), so re-downloading the URL recorded in
``version.json`` can never notice a new edition — the old file stays where it
was. This command reads the download link from the PCA's BCO page instead,
and only falls back to hashing the recorded URL when the page cannot be read.
"""

import hashlib
import json
import re
import urllib.request
from html import unescape

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

BCO_PAGE_URL = "https://www.pcaac.org/bco/"
USER_AGENT = "StudyReformed-BCO-Check/2.0"

# The English edition: "BCO_2026.pdf", "BCO2025-1.pdf" — not the Korean
# ("2026-KBCO-ALL.pdf") or Spanish ("LDO_2025.pdf") translations.
_PDF_LINK_RE = re.compile(r'href="([^"]+\.pdf)"', re.IGNORECASE)
_ENGLISH_BCO_RE = re.compile(r'/BCO[^/]*\.pdf$', re.IGNORECASE)


def current_pdf_url(page_html):
    """The English BCO PDF linked from the PCA's BCO page, or None."""
    for href in _PDF_LINK_RE.findall(page_html):
        href = unescape(href)
        if _ENGLISH_BCO_RE.search(href):
            return href
    return None


def _fetch(url, timeout=30):
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


class Command(BaseCommand):
    help = "Check whether the PCA has published a newer Book of Church Order than the one loaded"

    def add_arguments(self, parser):
        parser.add_argument(
            '--fail-if-outdated', action='store_true',
            help='Exit with an error when a newer edition is available (for scheduled checks)',
        )

    def handle(self, *args, **options):
        version_path = settings.BASE_DIR / "data" / "pca_bco" / "version.json"
        if not version_path.exists():
            self.stdout.write(self.style.WARNING("No version.json found — run scripts/parse_pca_bco.py first."))
            return

        with open(version_path) as f:
            version = json.load(f)
        loaded_url = version.get('url', '')
        edition = version.get('edition', 'unknown edition')

        self.stdout.write(f"Loaded: {edition} ({loaded_url})")
        self.stdout.write(f"Checking {BCO_PAGE_URL} ...")
        try:
            page = _fetch(BCO_PAGE_URL).decode('utf-8', errors='replace')
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Could not read the PCA's BCO page: {exc}"))
            page = ''

        published_url = current_pdf_url(page) if page else None
        if page and not published_url:
            self.stdout.write(self.style.WARNING(
                "The BCO page no longer links a PDF named like BCO*.pdf; check it by hand."
            ))

        outdated = False
        if published_url and published_url != loaded_url:
            outdated = True
            self.stdout.write(self.style.WARNING(
                "A NEW EDITION OF THE BCO HAS BEEN PUBLISHED.\n"
                f"  Loaded:    {loaded_url}\n"
                f"  Published: {published_url}\n"
                "  Download it and run:\n"
                f"    python scripts/parse_pca_bco.py BCO.pdf --url {published_url}\n"
                "    python manage.py load_pca_bco"
            ))
        else:
            # Same URL (or the page could not be read): the PCA occasionally
            # replaces the file in place with corrections.
            try:
                current_hash = hashlib.sha256(_fetch(published_url or loaded_url)).hexdigest()
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"Failed to download the PDF: {exc}"))
                return
            if current_hash != version.get('sha256'):
                outdated = True
                self.stdout.write(self.style.WARNING(
                    "The published PDF has changed since it was parsed "
                    f"(stored {version.get('sha256', '')[:16]}..., now {current_hash[:16]}...).\n"
                    "  Re-download it and re-run scripts/parse_pca_bco.py."
                ))
            else:
                self.stdout.write(self.style.SUCCESS(f"BCO is up to date ({edition})."))

        if outdated and options['fail_if_outdated']:
            raise CommandError("The loaded BCO is out of date.")
