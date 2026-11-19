"""Regression tests for the generic, read-only history scan."""
import importlib.util
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "privacy_scan", Path(__file__).with_name("privacy_scan.py")
)
privacy_scan = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(privacy_scan)


class GenericPatternTests(unittest.TestCase):
    def test_scanner_only_uses_common_direct_identifier_categories(self):
        self.assertEqual(set(privacy_scan.PATTERNS), {"email", "phone", "street-address"})

    def test_matches_are_not_printed(self):
        def fake_git(*args):
            if args[:2] == ("for-each-ref", "--format=%(refname)"):
                return "refs/heads/test\n"
            if args[:2] == ("rev-list", "refs/heads/test"):
                return "commit-id\n"
            if args[:3] == ("ls-tree", "-r", "--name-only"):
                return "generic-file.txt\n"
            if args[:2] == ("show", "commit-id:generic-file.txt"):
                return "contact example@example.invalid"
            return ""

        output = StringIO()
        with patch.object(privacy_scan, "git", side_effect=fake_git), patch.object(
            privacy_scan, "is_shallow_repository", return_value=False
        ), redirect_stdout(output):
            self.assertEqual(privacy_scan.audit(True, []), 1)
        text = output.getvalue()
        self.assertIn("generic-file.txt", text)
        self.assertNotIn("example@example.invalid", text)


class ShallowHistoryNoticeTests(unittest.TestCase):
    def test_shallow_scan_labels_history_as_incomplete(self):
        output = StringIO()
        with (
            patch.object(privacy_scan, "refs", return_value=[]),
            patch.object(privacy_scan, "is_shallow_repository", return_value=True),
            redirect_stdout(output),
        ):
            self.assertEqual(privacy_scan.audit(False, []), 0)
        self.assertIn("shallow clone; earlier commits are not audited", output.getvalue())

    def test_complete_scan_states_its_local_history_scope(self):
        output = StringIO()
        with (
            patch.object(privacy_scan, "refs", return_value=[]),
            patch.object(privacy_scan, "is_shallow_repository", return_value=False),
            redirect_stdout(output),
        ):
            self.assertEqual(privacy_scan.audit(False, []), 0)
        self.assertIn("full local history for the scanned refs was available", output.getvalue())


if __name__ == "__main__":
    unittest.main()
