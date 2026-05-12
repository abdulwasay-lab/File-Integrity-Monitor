# tests/test_hasher.py

import os
import tempfile
import unittest
from modules.hasher import hash_file, get_metadata


class TestHasher(unittest.TestCase):

    def setUp(self):
        """Create a temporary file to test against."""
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        self.tmp.write(b"Hello, FIM!")
        self.tmp.close()

    def tearDown(self):
        """Remove the temporary file after each test."""
        os.unlink(self.tmp.name)


    # ── hash_file Tests ───────────────────────────────────

    def test_hash_returns_string(self):
        result = hash_file(self.tmp.name)
        self.assertIsInstance(result, str)

    def test_hash_is_64_chars(self):
        result = hash_file(self.tmp.name)
        self.assertEqual(len(result), 64)

    def test_hash_is_consistent(self):
        hash1 = hash_file(self.tmp.name)
        hash2 = hash_file(self.tmp.name)
        self.assertEqual(hash1, hash2)

    def test_hash_changes_when_file_changes(self):
        hash1 = hash_file(self.tmp.name)
        with open(self.tmp.name, "wb") as f:
            f.write(b"Changed content!")
        hash2 = hash_file(self.tmp.name)
        self.assertNotEqual(hash1, hash2)

    def test_hash_missing_file_returns_none(self):
        result = hash_file("/nonexistent/file.txt")
        self.assertIsNone(result)


    # ── get_metadata Tests ────────────────────────────────

    def test_metadata_returns_dict(self):
        result = get_metadata(self.tmp.name)
        self.assertIsInstance(result, dict)

    def test_metadata_has_required_keys(self):
        result = get_metadata(self.tmp.name)
        for key in ["size", "permissions", "uid", "gid", "mtime"]:
            self.assertIn(key, result)

    def test_metadata_size_is_correct(self):
        result = get_metadata(self.tmp.name)
        self.assertEqual(result["size"], os.path.getsize(self.tmp.name))

    def test_metadata_missing_file_returns_none(self):
        result = get_metadata("/nonexistent/file.txt")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
