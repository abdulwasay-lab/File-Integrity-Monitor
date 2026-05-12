# modules/reporter.py

import os
from datetime import datetime
from config import LOG_FILE, LOG_ENABLED


# ── Severity & Icons ──────────────────────────────────────
SEVERITY = {
    "ADDED":        ("🟡", "MEDIUM", "ADDED"),
    "DELETED":      ("🔴", "HIGH",   "DELETED"),
    "MODIFIED":     ("🔴", "HIGH",   "MODIFIED"),
    "PERM_CHANGE":  ("🟡", "MEDIUM", "PERM CHANGE"),
    "OWNER_CHANGE": ("🔴", "HIGH",   "OWNER CHANGE"),
}


def print_report(findings):
    """
    Print findings to the terminal in a clean format.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{'='*60}")
    print(f"  FIM Report — {timestamp}")
    print(f"{'='*60}")

    if not findings:
        print("  ✅  No changes detected. All files are intact.")
        print(f"{'='*60}\n")
        return

    print(f"  ⚠️   {len(findings)} issue(s) found\n")

    for f in findings:
        icon, severity, label = SEVERITY.get(f["type"], ("⚪", "INFO", f["type"]))
        print(f"  {icon}  [{severity}] {label}")
        print(f"      File   : {f['file']}")
        print(f"      Detail : {f['detail']}")
        print(f"      Time   : {f['timestamp']}")
        print()

    print(f"{'='*60}\n")

    if LOG_ENABLED:
        write_log(findings)


def write_log(findings):
    """
    Append findings to the log file.
    """
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    with open(LOG_FILE, "a") as f:
        for finding in findings:
            icon, severity, label = SEVERITY.get(
                finding["type"], ("⚪", "INFO", finding["type"])
            )
            f.write(
                f"[{finding['timestamp']}] "
                f"[{severity}] {label} — "
                f"{finding['file']} — "
                f"{finding['detail']}\n"
            )
