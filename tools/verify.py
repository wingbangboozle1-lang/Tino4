#!/usr/bin/env python3
"""Privacy-boundary checks for the public static site."""
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if __name__ == '__main__':
    html = [ROOT / 'index.html', *sorted((ROOT / 'pages').glob('*.html'))]
    bad = re.compile(r'\b9[45]\d{3}\b|Cupertino|San Francisco|Outer Sunset|\$\s*[0-9][0-9,]{4,}|case-projections', re.I)
    errors = []
    for file in html:
        text = file.read_text(encoding='utf-8')
        for match in bad.finditer(text):
            errors.append(f'{file.relative_to(ROOT)} contains prohibited case-like content: {match.group(0)}')
        if 'noindex,nofollow,noarchive' not in text:
            errors.append(f'{file.relative_to(ROOT)} missing noindex')
    if (ROOT / 'assets/case-projections.csv').exists():
        errors.append('case projection data file exists in public assets')
    if len(html) < 4:
        errors.append('expected home plus privacy, brief and review pages')
    if errors:
        print('\n'.join(errors)); sys.exit(1)
    print(f'OK — {len(html)} public HTML files pass privacy checks; no case projection file.')
