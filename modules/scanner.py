# modules/scanner.py

from pathlib import Path
from modules.hasher import hash_file, get_metadata
from config import WATCH_PATHS


def scan(paths=WATCH_PATHS):
    """
    Scan all files from the given paths.
    Accepts both individual files and directories.
    Returns a dict of {filepath: {hash, metadata}}.
    """
    results = {}

    for path in paths:
        p = Path(path)

        if p.is_file():
            targets = [p]                                        # single file

        elif p.is_dir():
            targets = [f for f in p.rglob("*") if f.is_file()]  # walk directory

        else:
            print(f"  [WARN] Path not found: {path}")
            continue

        for target in targets:
            fp = str(target)

            file_hash = hash_file(fp)
            metadata  = get_metadata(fp)

            if file_hash is None:
                print(f"  [SKIP] Cannot read: {fp}")
                continue

            results[fp] = {
                "hash":     file_hash,
                "metadata": metadata,
            }

    return results
