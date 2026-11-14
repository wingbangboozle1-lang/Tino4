"""Regression tests for privacy-safe public output."""
import subprocess
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
class PublicSitePrivacyTests(unittest.TestCase):
    def test_build_does_not_publish_household_case_data(self):
        subprocess.run([sys.executable, str(ROOT / 'tools/build.py')], cwd=ROOT, check=True)
        files = [ROOT / 'index.html', *sorted((ROOT / 'pages').glob('*.html'))]
        self.assertGreaterEqual(len(files), 5)
        text = '\n'.join(p.read_text(encoding='utf-8') for p in files)
        for token in ('95014', '94122', 'Cupertino', 'Outer Sunset', '$3,100,000', '$1,800,000', '$7,150'):
            self.assertNotIn(token.lower(), text.lower())
        self.assertFalse((ROOT / 'assets/case-projections.csv').exists())
        self.assertIn('Attorney &amp; CPA briefing sheet', (ROOT / 'pages/attorney-cpa-brief.html').read_text())
        self.assertIn('24–36 months', (ROOT / 'pages/suggestions.html').read_text())
        privacy = (ROOT / 'pages/privacy.html').read_text()
        flagged = (ROOT / 'pages/flagged-for-review.html').read_text()
        self.assertIn('Jekyll exclusions hide content from Pages only', privacy)
        self.assertIn('legacy excluded source/model files', flagged)
if __name__ == '__main__':
    unittest.main()
