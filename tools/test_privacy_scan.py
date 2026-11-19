"""Precision tests for the read-only exposure audit's value-shape matching."""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "privacy_scan", Path(__file__).with_name("privacy_scan.py")
)
privacy_scan = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(privacy_scan)


class ValueShapeMatchingTests(unittest.TestCase):
    def _grep(self, text: str, pattern: str, bounded: bool) -> bool:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q", tmp], check=True)
            (Path(tmp) / "page.html").write_text(text, encoding="utf-8")
            subprocess.run(["git", "-C", tmp, "add", "page.html"], check=True)
            subprocess.run(
                ["git", "-C", tmp, "-c", "user.name=t", "-c", "user.email=t@t",
                 "commit", "-qm", "t"], check=True)
            flags = ["-w"] if bounded else []
            out = subprocess.run(
                ["git", "-C", tmp, "grep", "-l", "-i", "-F", *flags, pattern, "HEAD", "--"],
                capture_output=True, text=True, check=False).stdout
            return bool(out.strip())

    def test_shape_inside_longer_figure_is_not_a_hit_when_bounded(self):
        # Regression: a synthetic longer figure must not match a shorter shape inside it.
        self.assertFalse(self._grep("<td>$91,234</td>", "1,234", bounded=True))
        self.assertTrue(self._grep("<td>$91,234</td>", "1,234", bounded=False))

    def test_standalone_shape_is_still_a_hit_when_bounded(self):
        self.assertTrue(self._grep("monthly $1,234 fee", "1,234", bounded=True))
        self.assertTrue(self._grep("total: 1,234.", "1,234", bounded=True))

    def test_scanner_uses_bounded_matching_for_shapes_only(self):
        source = Path(SPEC.origin).read_text(encoding="utf-8")
        self.assertIn('bounded = ["-w"] if pattern in shapes else []', source)
        self.assertIn("*bounded", source)


if __name__ == "__main__":
    unittest.main()
