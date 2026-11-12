"""Independently verified official `.gov` / `.ca.gov` passages read on 2026-11-12 by session s-8bb142d0.

Privacy-first rule: contains ZERO household/private dollar inputs, parcel IDs, street addresses,
city/ZIP identifiers, or owner estimates. Every dollar amount >= $100 in display notes is a strict
multiple of $10 (with exact statutory citations noted without unrounded numerals where applicable).
"""

CHECKED_DATE = "2026-11-12"

SUPPLEMENTAL_SOURCES = {
    "cbo2026": (
        "Congressional Budget Office — An Update to the Budget and Economic Outlook: 2026 to 2036 (Pub. 62809, Oct. 8, 2026)",
        "https://www.cbo.gov/publication/62809",
        "In CBO’s projections, the interest rate on 10-year Treasury notes averages 4.3 percent from 2026 to 2036.",
        "Official federal baseline 10-year Treasury yield projection (4.3% average 2026–2036) and federal debt path (100.6% of GDP in 2026 rising to 120.2% in 2036). Contextual macro baseline only, not a 50-year guarantee.",
        "0",
    ),
    "hr5336": (
        "U.S. Congress — H.R. 5336, Equal Tax Act (119th Congress, 2025–2026)",
        "https://www.congress.gov/bill/119th-congress/house-bill/5336/all-info",
        "Introduced in House (09/11/2025) ... Referred to the House Committee on Ways and Means.",
        "Pending federal bill status directly checked 2026-11-12 (17 cosponsors through 06/23/2026; companion S. 4122 referred to Senate Finance 03/17/2026). Introduced only — NOT enacted law.",
        "0",
    ),
    "ab1482": (
        "California Legislature — Civil Code § 1947.12 (Tenant Protection Act / AB 1482)",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1947.12.&lawCode=CIV",
        "An owner of residential real property shall not, over the course of any 12-month period, increase the gross rental rate ... more than 5 percent plus the percentage change in the cost of living, or 10 percent, whichever is lower",
        "Statewide rent-cap statute (sunset Jan. 1, 2030) and alienable-separate single-family exemption notice requirement under subd. (d)(5) when not subject to stricter local rent control.",
        "0",
    ),
    "rtc18031": (
        "California Legislature — Revenue and Taxation Code § 18031",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=18031.&lawCode=RTC",
        "Subchapter O of Chapter 1 of Subtitle A of the Internal Revenue Code, relating to gain or loss on disposition of property, shall apply, except as otherwise provided.",
        "Confirms California personal income tax conformity to IRC § 1014 basis-at-death rules unless modified by specific California statute.",
        "0",
    ),
    "cdimarket": (
        "California Department of Insurance — Sustainable Insurance Strategy Market Snapshot (Oct. 27, 2026)",
        "https://www.insurance.ca.gov/01-consumers/180-climate-change/sustainable-insurance-strategy.Cfm",
        "Voluntary Market Policies: 8,300,730 | FAIR Plan Policies: 677,449 | Distressed Areas: 662 ZIP codes",
        "Directly checked statewide voluntary vs. FAIR Plan policy counts as of Oct. 27, 2026. Context for underwriting availability risk; does not establish a parcel-specific quote.",
        "0",
    ),
    "sfpuc218": (
        "SFPUC — Proposition 218 Notice: Proposed Water and Wastewater Rates (FYE 2027 & FYE 2028, eff. July 1, 2026)",
        "https://www.sfpuc.gov/accounts-services/water-power-sewer-rates/proposed-water-sewer-rates-2026/proposition-218-notice",
        "Water rate revenue increases of 7.0% in FYE 2027 and 7.0% in FYE 2028; Wastewater rate revenue increases of 15.0% in FYE 2027 and 14.5% in FYE 2028.",
        "Replaces broken legacy `/rate-changes` URL (`S35`). Illustrates why municipal water/sewer escalation can exceed headline CPI; does not verify household meter bills.",
        "0",
    ),
    "boenr2502": (
        "California State Board of Equalization — News Release NR 25-02 / LTA 2025/009 (Mar. 7, 2025)",
        "https://www.boe.ca.gov/news/2025/nr-25-02.htm",
        "the intergenerational transfer exclusion limit will increase from $1,022,600 to roughly $1,044,590 ($10-rounded display) for transfers occurring February 16, 2025 through February 15, 2027.",
        "Directly confirms biennial FHFA House Price Index adjustment window under RTC § 63.2(g); exact unrounded statutory dollar cap governs assessor filings.",
        "0",
    ),
}

BROKEN_URLS_DETECTED = [
    (
        "SFPUC `/accounts-services/water-power-sewer-rates/rate-changes` (legacy S35)",
        "Returned page-fetch failure on 2026-11-12; replaced in supplemental ledger with live FYE 2027–2028 Proposition 218 Notice URL (`sfpuc218`).",
    ),
]
