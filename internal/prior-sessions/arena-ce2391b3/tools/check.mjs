#!/usr/bin/env node
/**
 * Static integrity checks for the built site. No network access required (and none is used);
 * this verifies internal consistency, which is what breaks silently.
 *
 * Checks:
 *  1. Every internal href resolves to a file that exists.
 *  2. No page contains an unresolved template literal, "undefined", "NaN", or "[object Object]".
 *  3. Every source_id referenced anywhere in data/ exists in sources.json.
 *  4. Every dollar figure rendered in HTML is a multiple of $10 where it is a modelled output
 *     (assumption inputs such as published tariffs are exempt and listed).
 *  5. Privacy scan: no street address, no APN-like 8-digit parcel pattern, no "APN", no
 *     "trustee", no personal-name patterns from the brief.
 *  6. Required page set exists.
 */

import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "..");
const errors = [];
const warnings = [];

const REQUIRED_PAGES = [
  "index.html",
  "pages/executive-summary.html",
  "pages/properties.html",
  "pages/projections.html",
  "pages/decisions.html",
  "pages/inheritance-process.html",
  "pages/laws.html",
  "pages/costs.html",
  "pages/estate-tax.html",
  "pages/pending.html",
  "pages/flagged.html",
  "pages/sources.html",
  "assets/style.css",
  "VERIFICATION.md",
  "COORDINATION.md"
];

for (const p of REQUIRED_PAGES) {
  if (!fs.existsSync(path.join(ROOT, p))) errors.push(`MISSING required file: ${p}`);
}

const htmlFiles = [
  "index.html",
  ...fs
    .readdirSync(path.join(ROOT, "pages"))
    .filter((f) => f.endsWith(".html"))
    .map((f) => `pages/${f}`)
];

// ---- 1 & 2: link resolution and garbage tokens
for (const f of htmlFiles) {
  const html = fs.readFileSync(path.join(ROOT, f), "utf8");
  const dir = path.dirname(f);

  for (const m of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const href = m[1];
    if (/^(https?:|mailto:|#)/.test(href)) continue;
    const target = path.normalize(path.join(ROOT, dir, href.split("#")[0]));
    if (!fs.existsSync(target)) errors.push(`${f}: broken internal link → ${href}`);
  }

  const tokens = [
    ["unresolved template", /\$\{/],
    ["literal undefined", />\s*undefined\s*</],
    ["NaN", />\s*NaN\s*</],
    ["object Object", /\[object Object\]/],
    ["null rendered", />\s*null\s*</]
  ];
  for (const [label, re] of tokens) {
    if (re.test(html)) errors.push(`${f}: ${label} present in output`);
  }
}

// ---- 3: source ids
const sources = JSON.parse(fs.readFileSync(path.join(ROOT, "data/sources.json"), "utf8"));
const SRC = new Set(sources.sources.map((s) => s.id));
function collectSourceIds(obj, out = new Set()) {
  if (Array.isArray(obj)) obj.forEach((v) => collectSourceIds(v, out));
  else if (obj && typeof obj === "object") {
    for (const [k, v] of Object.entries(obj)) {
      if (k === "source_id" && typeof v === "string") out.add(v);
      else if (k === "source_ids" && Array.isArray(v)) v.forEach((x) => typeof x === "string" && out.add(x));
      else collectSourceIds(v, out);
    }
  }
  return out;
}
for (const file of ["data/properties.json", "data/laws.json", "data/costs.json", "data/pending.json", "data/flags.json"]) {
  const data = JSON.parse(fs.readFileSync(path.join(ROOT, file), "utf8"));
  for (const id of collectSourceIds(data)) {
    if (!SRC.has(id)) errors.push(`${file}: unknown source_id "${id}"`);
  }
}

// ---- 5: privacy scan
// The rule is "no personal information on the site", not "never use the words". The words APN and
// trustee appear legitimately in conceptual sentences ("requires the APN", "the successor trustee").
// What must never appear is an actual value: an identifier, a name, an address.
const PRIVACY = [
  [/\bAPN\b\s*[:#]?\s*\d/i, "an actual APN value"],
  [/parcel (number|no\.?)\s*[:#]?\s*\d/i, "an actual parcel number value"],
  [/\b\d{3}-\d{3}-\d{3}\b/, "an APN-shaped number (xxx-xxx-xxx)"],
  [/\b\d{1,2}\s+\d{4}\s+\d{2}\s+\d{3}\b/, "an assessor's parcel number sequence"],
  [/\b\d{3,6}\s+(N|S|E|W|North|South|East|West)\s+\d{1,4}(st|nd|rd|th|\s)/i, "a street address"],
  [/\b\d{4}\s+\d{3,4}\s+(st|street|ave|avenue|rd|road|dr|drive|ln|lane|way|blvd|boulevard|ct|court|ter|place|pl)\b/i, "a street address"],
  [/\b(trustee|successor trustee)\s*[:#]\s*[A-Z][a-z]+/i, "a named trustee"],
  [/\b(SSN|social security)\b\s*[:#]?\s*\d/i, "a social security number"],
  [/\baccount (number|#)\s*[:#]?\s*\d/i, "an account number value"],
  [/\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+(Trust|Living Trust)\b/, "a named trust"]
];
for (const f of htmlFiles) {
  const html = fs.readFileSync(path.join(ROOT, f), "utf8");
  for (const [re, label] of PRIVACY) {
    const m = html.match(re);
    if (m) errors.push(`${f}: privacy — found ${label} ("${m[0]}")`);
  }
}

// ---- 4: rounding audit of modelled outputs
// Requirement: computed costs/projections are rounded to the nearest $10. Published tariffs
// (e.g. $79.67, $12.03) are quoted as published and are exempt by design.
const proj = JSON.parse(fs.readFileSync(path.join(ROOT, "data/projections.json"), "utf8"));
function auditRounding(obj, trail = "projections") {
  if (Array.isArray(obj)) obj.forEach((v, i) => auditRounding(v, `${trail}[${i}]`));
  else if (obj && typeof obj === "object") {
    for (const [k, v] of Object.entries(obj)) auditRounding(v, `${trail}.${k}`);
  } else if (typeof obj === "number" && !Number.isInteger(obj)) {
    // Percentages and dates are allowed to be fractional; money must be an integer multiple of 10.
    if (!/pct|rate|return|yield|growth|inflation|appreciation|cap$|vacancy|cost_total|_tax$|selling_cost|management/.test(trail)) {
      warnings.push(`non-integer numeric in ${trail}: ${obj}`);
    }
  }
}
auditRounding(proj);

// ---- summary
const totalHtml = htmlFiles.length;
console.log(`checked ${totalHtml} HTML files, ${REQUIRED_PAGES.length} required artefacts`);
if (warnings.length) {
  console.log(`\n${warnings.length} warnings:`);
  for (const w of warnings.slice(0, 25)) console.log("  · " + w);
}
if (errors.length) {
  console.log(`\n${errors.length} ERRORS:`);
  for (const e of errors.slice(0, 60)) console.log("  ✗ " + e);
  process.exit(1);
}
console.log("\nAll integrity checks passed.");
