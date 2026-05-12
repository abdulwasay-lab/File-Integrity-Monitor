# tests/test_scanner.py

import os
import tempfile
import unittest
from modules.scanner import scan


class TestScanner(unittest.TestCase):

    def setUp(self):
        """Create a temporary directory with test files."""
        self.tmpdir = tempfile.mkdtemp()
        for name in ["file1.txt", "file2.txt", "file3.txt"]:
            path = os.path.join(self.tmpdir, name)
            with open(path, "w") as f:
                f.write(f"Content of {name}")

    def tearDown(self):
        """Remove temporary directory after each test."""
        for f in os.listdir(self.tmpdir):
            os.unlink(os.path.join(self.tmpdir, f))
        os.rmdir(self.tmpdir)


    # ── scan Tests ────────────────────────────────────────

    def test_scan_returns_dict(self):
        result = scan([self.tmpdir])
        self.assertIsInstance(result, dict)

    def test_scan_finds_all_files(self):
        result = scan([self.tmpdir])
        self.assertEqual(len(result), 3)

    def test_scan_result_has_hash(self):
        result = scan([self.tmpdir])
        for filepath, data in result.items():
            self.assertIn("hash", data)
            self.assertIsNotNone(data["hash"])

    def test_scan_result_has_metadata(self):
        result = scan([self.tmpdir])
        for filepath, data in result.items():
            self.assertIn("metadata", data)
            self.assertIsNotNone(data["metadata"])

    def test_scan_single_file(self):
        single = os.path.join(self.tmpdir, "file1.txt")
        result = scan([single])
        self.assertEqual(len(result), 1)

    def test_scan_missing_path_skips(self):
        result = scan(["/nonexistent/path"])
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
