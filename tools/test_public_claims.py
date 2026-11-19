"""Guard that the public site describes its current privacy boundary honestly."""
import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import sitebuild


class PublicClaimsMatchTheBuild(unittest.TestCase):
    def rendered_pages(self):
        for path, title, group in sitebuild.PAGES:
            yield path, sitebuild.render(path, title, group)

    def test_no_page_claims_household_projections_are_published(self):
        for path, html in self.rendered_pages():
            self.assertNotIn("model's rounded output", html.lower(), path)
            self.assertNotIn("modelled case inputs", html.lower(), path)

    def test_site_is_generic_and_privacy_page_explains_historical_limit(self):
        pages = dict(self.rendered_pages())
        self.assertIn("earlier commits", pages["pages/privacy.html"])
        self.assertIn("no household", pages["pages/model-figures.html"].lower())

    def test_decision_changers_precede_explanatory_prose_on_homepage(self):
        pages = dict(self.rendered_pages())
        homepage = pages["index.html"]
        self.assertLess(homepage.index("What would change the answer?"), homepage.index("Read this page in plain language"))

    def test_the_generator_does_not_import_or_read_private_model_data(self):
        source = (ROOT / "sitebuild.py").read_text(encoding="utf-8")
        self.assertNotIn("case_model", source)
        self.assertNotIn(".read_text(", source)
        self.assertNotIn("import json\nimport os\nimport pathlib\nimport subprocess", source)

    def test_manifest_matches_the_page_list(self):
        manifest = json.loads((ROOT / "site-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest), len(sitebuild.PAGES))
        self.assertEqual(sorted(manifest), sorted(path for path, _, _ in sitebuild.PAGES))


if __name__ == "__main__":
    unittest.main()
