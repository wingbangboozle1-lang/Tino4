# Inheritance decision dashboard

A privacy-first static dashboard for reviewing inheritance decisions, with official-source links, an uncertainty register, and a 50-year stress test. The site is built using only Python's standard library.

```sh
python3 tools/build.py
python3 tools/verify.py
```

GitHub Pages is configured to build from the root of `main`. Jekyll's `_config.yml` excludes the board, tooling and working directories from the site. The public site uses anonymized placeholders (Property A / Property B) and rounds every owner-supplied and projected dollar amount to the nearest $10. No names, street addresses, parcel numbers, ZIP codes, e-mail addresses or account data are published. Rounding is not a guarantee of anonymity: distinctive figures combined over time can still be identifying, and the repository and its history are public. Deleting files in a subsequent commit does not erase previous commits, deployments, caches, or forks. Keep exact figures and private documents out of this public repository. See the task board for the privacy incident and outstanding remediation.

The dashboard is educational, not legal, tax, investment or insurance advice. Every table row links to an official source and carries a status label (Verified / Owner-supplied / Projection / Assumption / Not verified). Values that cannot be confirmed from an official source are left blank and listed on the Flagged for Review page. Models are hypothetical, not official predictions or personalized recommendations.
