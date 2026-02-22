import hashlib
from pathlib import Path


def _compute_hash(*paths):
    """Compute a combined SHA-256 hash of one or more files/directories."""
    h = hashlib.sha256()
    for p in sorted(paths):
        p = Path(p)
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file():
                    h.update(f.read_bytes())
        elif p.is_file():
            h.update(p.read_bytes())
    return h.hexdigest()


def data_is_current(name, *paths):
    """Return True if source data files haven't changed since last load."""
    from catechism.models import DataVersion

    try:
        version = DataVersion.objects.get(name=name)
    except DataVersion.DoesNotExist:
        return False

    return version.data_hash == _compute_hash(*paths)


def mark_data_current(name, *paths):
    """Record the current hash of source data files after a successful load."""
    from catechism.models import DataVersion

    DataVersion.objects.update_or_create(
        name=name,
        defaults={"data_hash": _compute_hash(*paths)},
    )