# tests/test_comparator.py

import unittest
from modules.comparator import compare


class TestComparator(unittest.TestCase):

    def setUp(self):
        """Set up a standard baseline to test against."""
        self.baseline = {
            "/etc/hosts": {
                "hash": "abc123",
                "metadata": { "permissions": "0o644", "uid": 0, "gid": 0 }
            },
            "/etc/passwd": {
                "hash": "def456",
                "metadata": { "permissions": "0o644", "uid": 0, "gid": 0 }
            }
        }

    # ── No Changes ────────────────────────────────────────

    def test_no_changes(self):
        findings = compare(self.baseline, self.baseline)
        self.assertEqual(len(findings), 0)

    # ── Modified ──────────────────────────────────────────

    def test_detects_modified_file(self):
        current = {
            "/etc/hosts":  { "hash": "CHANGED", "metadata": self.baseline["/etc/hosts"]["metadata"] },
            "/etc/passwd": self.baseline["/etc/passwd"]
        }
        findings = compare(self.baseline, current)
        self.assertIn("MODIFIED", [f["type"] for f in findings])

    # ── Deleted ───────────────────────────────────────────

    def test_detects_deleted_file(self):
        current = { "/etc/hosts": self.baseline["/etc/hosts"] }
        findings = compare(self.baseline, current)
        self.assertIn("DELETED", [f["type"] for f in findings])

    # ── Added ─────────────────────────────────────────────

    def test_detects_added_file(self):
        current = {
            **self.baseline,
            "/etc/newfile": { "hash": "new123", "metadata": { "permissions": "0o644", "uid": 0, "gid": 0 } }
        }
        findings = compare(self.baseline, current)
        self.assertIn("ADDED", [f["type"] for f in findings])

    # ── Permission Change ─────────────────────────────────

    def test_detects_permission_change(self):
        current = {
            "/etc/hosts":  { "hash": "abc123", "metadata": { "permissions": "0o777", "uid": 0, "gid": 0 } },
            "/etc/passwd": self.baseline["/etc/passwd"]
        }
        findings = compare(self.baseline, current)
        self.assertIn("PERM_CHANGE", [f["type"] for f in findings])

    # ── Owner Change ──────────────────────────────────────

    def test_detects_owner_change(self):
        current = {
            "/etc/hosts":  { "hash": "abc123", "metadata": { "permissions": "0o644", "uid": 999, "gid": 0 } },
            "/etc/passwd": self.baseline["/etc/passwd"]
        }
        findings = compare(self.baseline, current)
        self.assertIn("OWNER_CHANGE", [f["type"] for f in findings])

    # ── Finding Structure ─────────────────────────────────

    def test_finding_has_required_keys(self):
        current = { "/etc/hosts": self.baseline["/etc/hosts"] }
        findings = compare(self.baseline, current)
        for f in findings:
            for key in ["type", "file", "detail", "timestamp"]:
                self.assertIn(key, f)


if __name__ == "__main__":
    unittest.main()
