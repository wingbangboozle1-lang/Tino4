# Inheritance decision dashboard

A privacy-first static guide to comparing a future inherited home with a separate, already-owned residence. It covers occupancy, rental and sale choices; property and estate taxes; insurance and operating costs; a blank private-estimate table; and a 50-year synthetic black-swan index scenario. The pages use official-source links and state uncertainty rather than filling in missing household values. Built with Python's standard library only.

```sh
python3 tools/build.py
python3 tools/verify.py
```

`tools/build.py` is a standalone page generator: it does not load private model output or household inputs. The 50-year scenario is based only on explicitly stated synthetic index assumptions; it is not a personal-property projection or an official forecast. `tools/verify.py` checks generated-page links and source-register coverage, row status labels, `noindex,nofollow` metadata, private-identifier patterns, $10 rounding, blank case-specific projection cells, the synthetic annual index, compatibility redirects, Jekyll exclusions, and removal of obsolete working directories. These structural checks do not prove every legal claim, source interpretation or assumption.

The comparison keeps the inherited home separate from the already-owned residence, including consideration of the latter's rental income and costs, without publishing household-specific figures. Some official citations are jurisdiction-specific; their publisher names or URLs identify the source's jurisdiction and provide legal context, but are not verification of any household property's location. The generated pages intentionally omit property addresses, ZIP codes, parcel/account identifiers and case-specific financial estimates. Automated checks and `noindex` metadata are not guarantees of anonymity.

GitHub Pages builds from the root of `main`. Jekyll exclusions control what Pages publishes but do not make files in this public repository private. Earlier public pages, commits, pull-request diffs, task-board entries, caches, other branches and forks may retain case-derived material. A normal follow-up commit cannot purge those copies; history remediation requires repository-owner coordination. Do not add personal or case-specific financial information to repository files, build output, issues or pull requests. See the Flagged for Review page and [GitHub's sensitive-data guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

Educational only—not legal, tax, investment or insurance advice. Unknown values are blank, not zero. Models are hypothetical, not official forecasts or personalized recommendations.
