"""Regression checks for the public/private boundary and decision-guide output."""
from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import sitebuild


class PrivacyFirstSiteTests(unittest.TestCase):
    def test_public_generator_has_no_household_model_or_input_file(self):
        self.assertFalse((ROOT / "tools/case_model.py").exists())
        source = (ROOT / "tools/sitebuild.py").read_text(encoding="utf-8")
        self.assertNotIn("case_model", source)
        self.assertNotIn("owner-stated inputs", source.lower())

    def test_public_pages_are_generic_and_do_not_publish_case_rankings(self):
        rendered = "\n".join(sitebuild.render(path, title, group) for path, title, group in sitebuild.PAGES)
        self.assertIn("No household", rendered)
        self.assertNotIn("best-ranked path", rendered.lower())

    def test_privacy_page_discloses_history_limit_and_noindex_is_not_privacy(self):
        page = sitebuild.render("pages/privacy.html", "Privacy & limits", "Adviser & evidence")
        self.assertIn("cannot establish that earlier commits", page)
        self.assertIn("not private storage", page)
        self.assertIn("Rounding is not anonymization", page)

    def test_what_if_tools_are_client_only(self):
        for script in ("assets/app.js", "assets/phase-model.js", "assets/regime-model.js"):
            source = (ROOT / script).read_text(encoding="utf-8")
            self.assertNotIn("localStorage", source)
            self.assertNotIn("sessionStorage", source)
            self.assertNotIn("fetch(", source)
            self.assertNotIn("XMLHttpRequest", source)
        app = (ROOT / "assets/app.js").read_text(encoding="utf-8")
        self.assertNotIn("simulatePath", app)
        self.assertNotIn("dist-run", app)

    def test_suggestions_and_adviser_brief_remain_present(self):
        paths = {path for path, _, _ in sitebuild.PAGES}
        self.assertIn("pages/suggestions.html", paths)
        self.assertIn("pages/attorney-cpa-brief.html", paths)


if __name__ == "__main__":
    unittest.main()
