# Phased-investing test inputs (generator only, not published)

`fred_quarterly_1976Q1_2026Q3.csv`: quarterly averages of three official FRED series, copied from the
quarterly-average CSV fetched for each series on 2026-11-14.

| Column | FRED series | Source | Note |
| --- | --- | --- | --- |
| share_index_2015_100_qavg | SPASTT01USM661N | OECD via FRED (Federal Reserve Bank of St. Louis) | Broad share-price index for the United States, index 2015=100. Price only. It is not the S&P 500. |
| tb3ms_pct_qavg | TB3MS | FRED, 3-month Treasury bill, percent per year | Secondary-market rate |
| gs2_pct_qavg | GS2 | FRED, 2-year Treasury constant maturity, percent per year | Starts 1976-06 |

Blank cells mean no value for that quarter: GS2 before 1976Q3. No 2026Q4 row exists yet.
