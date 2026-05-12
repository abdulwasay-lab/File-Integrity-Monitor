# modules/hasher.py

import hashlib
import os
import stat


def hash_file(filepath):
    """
    Read a file in chunks and return its SHA-256 hash.
    Returns None if the file cannot be read.
    """
    try:
        h = hashlib.sha256()

        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)

        return h.hexdigest()

    except (PermissionError, FileNotFoundError, OSError):
        return None


def get_metadata(filepath):
    """
    Return file metadata — size, permissions, owner, and modified time.
    Returns None if the file cannot be accessed.
    """
    try:
        s = os.stat(filepath)

        return {
            "size":        s.st_size,
            "permissions": oct(stat.S_IMODE(s.st_mode)),
            "uid":         s.st_uid,
            "gid":         s.st_gid,
            "mtime":       s.st_mtime,
        }

    except OSError:
        return None
