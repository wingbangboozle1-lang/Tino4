# Home Inheritance Decision Guide

A privacy-first, static GitHub Pages dashboard for organizing current California and federal rules relevant to an expected future trust inheritance involving two California homes. It compares hold/live, rent, and sell/reinvest decisions without publishing the user's property-specific estimates, addresses, ZIP codes, rent, tax history, utility bills, or personal identifiers.

## Pages

- `index.html` — executive summary and decision briefing
- `scenarios.html` — live / rent / sell comparison and decision gates
- `inheritance.html` — trust transfer sequence and current tax rules
- `forecast.html` — 2040–2050 forecast status and legal-change watch
- `costs.html` — blank-by-design operating cost ledger
- `review.html` — flagged verification items and privacy checks
- `sources.html` — official-source register

## Privacy and evidence policy

- No user-specific property records or identifying values are included. Cases use generic labels.
- No analytics, tracking, form, or visitor input storage is configured.
- User-supplied property/cost figures are not treated as verified evidence and are not republished.
- Numeric fields are left blank where no official source can confirm the value. No invented appreciation, inflation, utility, insurance, maintenance, or tax projections are used.
- Every data-table row links to an official government/court/utility source. Unresolved items are listed on the **Flagged for review** page.
- Amounts displayed in dollar terms are rounded to the nearest $10 where practical; when a legal amount is rounded for display, the exact statutory/source amount is stated.

## Local preview

This site uses static HTML and CSS only; open `index.html` directly or serve the repository root with any static web server. There are no build-time dependencies.

## GitHub Pages

A workflow in `.github/workflows/pages.yml` publishes the root static site on pushes to `main` and supports manual deployment. Enable GitHub Pages with **GitHub Actions** as the build/deploy source in repository settings if it is not already configured.

## Disclaimer

The dashboard is general research, not legal, tax, investment, insurance, or property-management advice. Rules and dollar thresholds can change before the projected 2040–2050 transfer. Confirm the actual trust, tax residence, federal estate, title, property-tax assessment, rental obligations, and insurance circumstances with qualified professionals and the relevant authorities at the time.
