# fim.py  (Windows edition)

import sys
import time
import argparse

# ── Windows guard ─────────────────────────────────────────
if sys.platform != "win32":
    print("[!] This script targets Windows. Use the original fim.py on Linux/macOS.")
    sys.exit(1)

from config import WATCH_PATHS, CHECK_INTERVAL
from modules.scanner    import scan
from modules.baseline   import save_baseline, load_baseline, baseline_exists
from modules.comparator import compare
from modules.reporter   import print_report


# ── Helpers ───────────────────────────────────────────────

def _require_baseline():
    """
    Check for a baseline and exit cleanly if it is missing.

    This replaces the exit(1) that was buried inside load_baseline() —
    keeping library code exit-free and putting control flow here.
    """
    if not baseline_exists():
        print("\n[!] No baseline found.")
        print("    Run:  python fim.py --baseline\n")
        sys.exit(1)


# ── Commands ──────────────────────────────────────────────

def run_baseline():
    """Create a fresh baseline snapshot."""
    print("\n[*] Creating baseline...")
    print(f"    Watching {len(WATCH_PATHS)} path(s)\n")

    if baseline_exists():
        try:
            confirm = input("[!] Baseline already exists. Overwrite? (y/n): ")
        except KeyboardInterrupt:
            print("\n[!] Cancelled.")
            return

        if confirm.strip().lower() != "y":
            print("[!] Baseline creation cancelled.")
            return

    data = scan()

    if not data:
        print("\n[!] No files could be read. Check that the paths in config.py")
        print("    exist and that you are running as Administrator.\n")
        return

    save_baseline(data)


def run_check():
    """Run a single integrity check against the baseline."""
    print("\n[*] Running integrity check...")
    _require_baseline()

    baseline = load_baseline()
    current  = scan()
    findings = compare(baseline, current)

    print_report(findings)


def run_monitor():
    """Continuously check for changes every CHECK_INTERVAL seconds."""
    print(f"\n[*] Monitor mode started — checking every {CHECK_INTERVAL}s")
    print(    "    Press Ctrl+C to stop\n")
    _require_baseline()

    try:
        while True:
            run_check()
            print(f"[*] Next check in {CHECK_INTERVAL} seconds...\n")
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n[*] Monitor stopped.")


def print_status():
    """Print current FIM status — baseline info and watched paths."""
    print("\n[*] FIM Status")
    print(f"{'='*48}")

    if baseline_exists():
        print("    Baseline     : ✅ Found")
    else:
        print("    Baseline     : ❌ Not created yet")

    print(f"    Watching     : {len(WATCH_PATHS)} path(s)")

    for path in WATCH_PATHS:
        print(f"      → {path}")

    # Windows-specific hint
    print()
    print("    [i] Some paths (e.g. RegBack hives) require")
    print("        Administrator privileges to read.")
    print(f"{'='*48}\n")


# ── CLI Entry Point ───────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="File Integrity Monitor (FIM) — Windows Edition",
        epilog=(
            "Examples:\n"
            "  python fim.py --baseline\n"
            "  python fim.py --check\n"
            "  python fim.py --monitor\n\n"
            "Note: Run as Administrator for full access to system paths."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--baseline", action="store_true",
                        help="Create a fresh baseline snapshot")
    parser.add_argument("--check",    action="store_true",
                        help="Run a single integrity check")
    parser.add_argument("--monitor",  action="store_true",
                        help="Continuously monitor for changes")
    parser.add_argument("--status",   action="store_true",
                        help="Show current FIM status")

    args = parser.parse_args()

    if   args.baseline: run_baseline()
    elif args.check:    run_check()
    elif args.monitor:  run_monitor()
    elif args.status:   print_status()
    else:               parser.print_help()


if __name__ == "__main__":
    main()
