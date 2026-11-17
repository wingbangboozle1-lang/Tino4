"""Guard: the framework prose must keep agreeing with the published model.

`tools/case_model.py` publishes modelled figures on most pages. Until now the hand-written
framework text still claimed the opposite in a dozen places ("amounts stay private", "no
household ranking is emitted", "the answer is not currently knowable"), which is exactly the
kind of contradiction that makes a decision site unreadable a year later. These tests pin the
corrected wording and refuse to let the stale claims come back.
"""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import sitebuild  # noqa: E402

STALE = [
    "no household ranking is emitted",
    "Framework (amounts stay private)",
    "The answer is not currently knowable from public information",
    "no household amounts or year-by-year case projections are emitted",
    "No location, value, parcel identifier, tax history or insurance figure is published",
    "No location, value, rent roll, tax history, tenant or insurance data is published",
    "Use placeholders in this public project",
    "household facts stay private",
    "intentionally contains no property locality, address, parcel identifier, household amount",
    "The generator contains only generic rules and public sources",
    "Location and individual property figures are omitted",
    "no household-specific data is published",
    "no household inputs were read",
]


class PublishedClaimsMatchTheModel(unittest.TestCase):
    def rendered_pages(self):
        for path, title, group in sitebuild.PAGES:
            yield path, sitebuild.render(path, title, group)

    def test_no_page_still_claims_that_no_figures_are_published(self):
        offenders = []
        for path, html in self.rendered_pages():
            for phrase in STALE:
                if phrase in html:
                    offenders.append((path, phrase))
        self.assertEqual(offenders, [], f"stale privacy claim: {offenders[:4]}")

    def test_pages_printing_dollar_figures_say_they_are_modelled(self):
        """A published amount without the modelled-figures note reads like a record."""
        currency = re.compile(r"(?<![\w])\$\s*[0-9][0-9,]{5,}")
        missing = [path for path, html in self.rendered_pages()
                   if currency.search(html) and "model" not in html.lower()]
        self.assertEqual(missing, [], f"figures without a modelled-figures note: {missing}")

    def test_privacy_page_states_the_boundary_the_build_actually_keeps(self):
        page = sitebuild.render("pages/privacy.html", "Privacy & limits", "Adviser & evidence")
        self.assertIn("modelled output", page)
        self.assertIn("traceability", page)
        self.assertIn("no property locality", page)

    def test_the_generator_is_self_contained_apart_from_the_model_module(self):
        source = (ROOT / "sitebuild.py").read_text(encoding="utf-8")
        self.assertIn("import case_model as cm", source)
        self.assertNotIn(".read_text(", source)
        self.assertNotIn("import json\nimport os\nimport pathlib\nimport subprocess", source)

    def test_the_manifest_matches_the_page_list(self):
        manifest = json.loads((ROOT / "site-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest), len(sitebuild.PAGES))
        self.assertEqual(sorted(manifest), sorted(path for path, _t, _g in sitebuild.PAGES))


if __name__ == "__main__":
    unittest.main()
