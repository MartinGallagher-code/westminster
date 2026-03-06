import hashlib
import json
import urllib.request
from django.conf import settings
from django.core.management.base import BaseCommand

BCO_URL = "https://www.pcaac.org/wp-content/uploads/2024/08/BCO-2024-1.pdf"


class Command(BaseCommand):
    help = "Check if the PCA Book of Church Order PDF has been updated"

    def handle(self, *args, **options):
        version_path = settings.BASE_DIR / "data" / "pca_bco" / "version.json"

        if not version_path.exists():
            self.stdout.write(self.style.WARNING("No version.json found — run the initial download first."))
            return

        with open(version_path) as f:
            version = json.load(f)

        stored_hash = version['sha256']
        url = version.get('url', BCO_URL)

        self.stdout.write(f"Checking {url} ...")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'StudyReformed-BCO-Check/1.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                pdf_bytes = resp.read()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to download: {e}"))
            return

        current_hash = hashlib.sha256(pdf_bytes).hexdigest()

        if current_hash == stored_hash:
            self.stdout.write(self.style.SUCCESS(
                f"BCO is unchanged (edition: {version.get('edition', 'unknown')})"
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f"BCO HAS BEEN UPDATED!\n"
                f"  Stored hash:  {stored_hash[:16]}...\n"
                f"  Current hash: {current_hash[:16]}...\n"
                f"  Re-download the PDF and re-run the parser to update."
            ))
