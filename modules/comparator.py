# modules/comparator.py

from datetime import datetime


def compare(baseline, current):
    """
    Compare baseline scan vs current scan.
    Returns a list of findings — each finding is a dict.
    """
    findings  = []
    all_files = set(baseline) | set(current)    # every file from both scans

    for fp in all_files:
        b = baseline.get(fp)
        c = current.get(fp)

        # ── New file found ────────────────────────────────
        if b is None:
            findings.append({
                "type":      "ADDED",
                "file":      fp,
                "detail":    "New file detected",
                "timestamp": datetime.now().isoformat(),
            })

        # ── File deleted ──────────────────────────────────
        elif c is None:
            findings.append({
                "type":      "DELETED",
                "file":      fp,
                "detail":    "File has been removed",
                "timestamp": datetime.now().isoformat(),
            })

        else:
            bm = b.get("metadata", {})
            cm = c.get("metadata", {})

            # ── Content changed ───────────────────────────
            if b["hash"] != c["hash"]:
                findings.append({
                    "type":      "MODIFIED",
                    "file":      fp,
                    "detail":    f"Hash changed | Before: {b['hash'][:16]}... | After: {c['hash'][:16]}...",
                    "timestamp": datetime.now().isoformat(),
                })

            # ── Permissions changed ───────────────────────
            if bm.get("permissions") != cm.get("permissions"):
                findings.append({
                    "type":      "PERM_CHANGE",
                    "file":      fp,
                    "detail":    f"Permissions changed: {bm.get('permissions')} → {cm.get('permissions')}",
                    "timestamp": datetime.now().isoformat(),
                })

            # ── Owner changed ─────────────────────────────
            if bm.get("uid") != cm.get("uid") or bm.get("gid") != cm.get("gid"):
                findings.append({
                    "type":      "OWNER_CHANGE",
                    "file":      fp,
                    "detail":    f"Owner changed: uid {bm.get('uid')}→{cm.get('uid')}, gid {bm.get('gid')}→{cm.get('gid')}",
                    "timestamp": datetime.now().isoformat(),
                })

    return findings
