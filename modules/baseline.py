# modules/baseline.py

import json
import os
from datetime import datetime
from config import BASELINE_FILE


def save_baseline(data, filepath=BASELINE_FILE):
    """
    Save the current scan results to a JSON baseline file.
    """
    record = {
        "created_at": datetime.now().isoformat(),
        "files":      data,
    }

    with open(filepath, "w") as f:
        json.dump(record, f, indent=2)

    print(f"\n[+] Baseline saved  : {filepath}")
    print(f"    Files tracked   : {len(data)}")
    print(f"    Timestamp       : {record['created_at']}")


def load_baseline(filepath=BASELINE_FILE):
    """
    Load a previously saved baseline from a JSON file.
    Exits if no baseline file is found.
    """
    if not os.path.exists(filepath):
        print(f"\n[!] No baseline found at: {filepath}")
        print(    "    Run --baseline first to create one.")
        exit(1)

    with open(filepath) as f:
        record = json.load(f)

    print(f"\n[*] Baseline loaded : {filepath}")
    print(f"    Created at      : {record['created_at']}")
    print(f"    Files tracked   : {len(record['files'])}")

    return record["files"]


def baseline_exists(filepath=BASELINE_FILE):
    """
    Check if a baseline file already exists.
    Returns True or False.
    """
    return os.path.exists(filepath)
