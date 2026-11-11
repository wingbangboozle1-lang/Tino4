"""Official historical series used by the black-swan replay (session s-a24b1c8c).

Read on 2026-11-11 (UTC) from the FRED data service of the Federal Reserve Bank of St. Louis,
which republishes the primary official series named below. Values are index levels exactly
as served; nothing is interpolated or filled in.

HPI_SJ  FHFA All-Transactions House Price Index, San Jose-Sunnyvale-Santa Clara, CA (MSA),
        series ATNHPIUS41940Q, annual, end of period (Q4). Primary source: FHFA.
        https://fred.stlouisfed.org/graph/fredgraph.csv?id=ATNHPIUS41940Q&fq=Annual&fam=eop
HPI_SF  FHFA All-Transactions House Price Index, San Francisco-San Mateo-Redwood City, CA
        (MSAD), series ATNHPIUS41884Q, annual, end of period (Q4). Primary source: FHFA.
        https://fred.stlouisfed.org/graph/fredgraph.csv?id=ATNHPIUS41884Q&fq=Annual&fam=eop
CPI     BLS Consumer Price Index for All Urban Consumers, all items, U.S. city average, not
        seasonally adjusted (1982-84=100), series CPIAUCNS, annual average. Primary: BLS.
        https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCNS&fq=Annual&fam=avg
"""

HPI_SJ = {1976: 23.21, 1977: 30.02, 1978: 32.66, 1979: 40.49, 1980: 47.66, 1981: 52.27,
          1982: 50.50, 1983: 52.72, 1984: 56.65, 1985: 60.95, 1986: 65.56, 1987: 72.14,
          1988: 90.70, 1989: 114.25, 1990: 107.32, 1991: 106.23, 1992: 104.34, 1993: 101.44,
          1994: 99.95, 1995: 102.45, 1996: 108.06, 1997: 122.46, 1998: 138.45, 1999: 157.67,
          2000: 203.54, 2001: 205.16, 2002: 216.22, 2003: 220.87, 2004: 255.24, 2005: 309.48,
          2006: 318.32, 2007: 302.81, 2008: 258.84, 2009: 237.76, 2010: 240.85, 2011: 235.66,
          2012: 252.50, 2013: 291.32, 2014: 319.27, 2015: 353.92, 2016: 373.83, 2017: 396.48,
          2018: 425.46, 2019: 415.13, 2020: 419.68, 2021: 463.63, 2022: 510.15, 2023: 546.45,
          2024: 558.19, 2025: 560.05}

HPI_SF = {1976: 23.70, 1977: 28.62, 1978: 31.52, 1979: 40.23, 1980: 45.17, 1981: 46.03,
          1982: 45.89, 1983: 49.44, 1984: 52.64, 1985: 58.13, 1986: 65.71, 1987: 78.06,
          1988: 98.50, 1989: 113.64, 1990: 109.68, 1991: 107.13, 1992: 104.16, 1993: 101.60,
          1994: 98.88, 1995: 100.94, 1996: 103.59, 1997: 114.45, 1998: 127.97, 1999: 150.39,
          2000: 184.16, 2001: 192.89, 2002: 206.94, 2003: 219.05, 2004: 256.29, 2005: 301.62,
          2006: 307.14, 2007: 298.91, 2008: 267.06, 2009: 250.31, 2010: 248.26, 2011: 240.50,
          2012: 257.01, 2013: 296.34, 2014: 329.82, 2015: 374.38, 2016: 396.57, 2017: 416.06,
          2018: 445.81, 2019: 442.90, 2020: 425.06, 2021: 451.73, 2022: 487.95, 2023: 495.49,
          2024: 505.79, 2025: 512.99}

CPI = {1970: 38.825, 1971: 40.492, 1972: 41.817, 1973: 44.400, 1974: 49.308, 1975: 53.817,
       1976: 56.908, 1977: 60.608, 1978: 65.233, 1979: 72.575, 1980: 82.408, 1981: 90.925,
       1982: 96.500, 1983: 99.600, 1984: 103.883, 1985: 107.567, 1986: 109.608, 1987: 113.625,
       1988: 118.258, 1989: 123.967, 1990: 130.658, 1991: 136.192, 1992: 140.317, 1993: 144.458,
       1994: 148.225, 1995: 152.383, 1996: 156.850, 1997: 160.517, 1998: 163.008, 1999: 166.575,
       2000: 172.200, 2001: 177.067, 2002: 179.875, 2003: 183.958, 2004: 188.883, 2005: 195.292,
       2006: 201.592, 2007: 207.342, 2008: 215.303, 2009: 214.537, 2010: 218.056, 2011: 224.939,
       2012: 229.594, 2013: 232.957, 2014: 236.736, 2015: 237.017, 2016: 240.007, 2017: 245.120,
       2018: 251.107, 2019: 255.657, 2020: 258.811, 2021: 270.970, 2022: 292.655, 2023: 304.702,
       2024: 313.689, 2025: 321.943}

# ---------------------------------------------------------------------------------------
# Interest rates and equities
# ---------------------------------------------------------------------------------------
# GS10    Market yield on U.S. Treasury securities at 10-year constant maturity, percent,
#         annual average of monthly values. Primary source: Board of Governors of the
#         Federal Reserve System (H.15).
#         https://fred.stlouisfed.org/graph/fredgraph.csv?id=GS10&fq=Annual&fam=avg
GS10 = {1970: 7.35, 1971: 6.16, 1972: 6.21, 1973: 6.84, 1974: 7.56, 1975: 7.99, 1976: 7.61,
        1977: 7.42, 1978: 8.41, 1979: 9.44, 1980: 11.46, 1981: 13.91, 1982: 13.00, 1983: 11.11,
        1984: 12.44, 1985: 10.62, 1986: 7.68, 1987: 8.38, 1988: 8.85, 1989: 8.50, 1990: 8.55,
        1991: 7.86, 1992: 7.01, 1993: 5.87, 1994: 7.08, 1995: 6.58, 1996: 6.44, 1997: 6.35,
        1998: 5.26, 1999: 5.64, 2000: 6.03, 2001: 5.02, 2002: 4.61, 2003: 4.02, 2004: 4.27,
        2005: 4.29, 2006: 4.79, 2007: 4.63, 2008: 3.67, 2009: 3.26, 2010: 3.21, 2011: 2.79,
        2012: 1.80, 2013: 2.35, 2014: 2.54, 2015: 2.14, 2016: 1.84, 2017: 2.33, 2018: 2.91,
        2019: 2.14, 2020: 0.89, 2021: 1.44, 2022: 2.95, 2023: 3.96, 2024: 4.21, 2025: 4.29}

# SHARE_PX  OECD "Share prices: total, all shares" index for the United States (2015=100),
#           series SPASTT01USM661N, December value of each year. PRICE ONLY - dividends are
#           not included. Primary source: OECD Main Economic Indicators.
#           https://fred.stlouisfed.org/graph/fredgraph.csv?id=SPASTT01USM661N&fq=Annual&fam=eop
SHARE_PX = {1970: 4.852874, 1971: 5.422477, 1972: 6.363502, 1973: 4.990267, 1974: 3.506448,
            1975: 4.632754, 1976: 5.579038, 1977: 5.132763, 1978: 5.316517, 1979: 6.114708,
            1980: 7.594362, 1981: 7.111047, 1982: 7.951669, 1983: 9.400146, 1984: 9.382779,
            1985: 11.816920, 1986: 14.074040, 1987: 13.357500, 1988: 15.384390, 1989: 19.075210,
            1990: 17.782710, 1991: 21.218730, 1992: 23.715260, 1993: 25.522890, 1994: 24.624290,
            1995: 32.471750, 1996: 38.781630, 1997: 49.976530, 1998: 57.038380, 1999: 63.198750,
            2000: 63.890250, 2001: 57.732380, 2002: 47.524850, 2003: 58.519850, 2004: 66.849360,
            2005: 72.956380, 2006: 85.118070, 2007: 91.882580, 2008: 51.736620, 2009: 67.164700,
            2010: 73.439090, 2011: 69.368180, 2012: 78.393570, 2013: 95.091090, 2014: 101.376500,
            2015: 95.553670, 2016: 103.843700, 2017: 119.044800, 2018: 108.755200, 2019: 128.520300,
            2020: 134.594100, 2021: 157.338200, 2022: 143.193000, 2023: 154.877400, 2024: 183.487000,
            2025: 205.567400}

# SP500_EOY, SP500_DIVYLD  Economic Report of the President 2025, Table B-56 "Common stock
#           prices and yields, 2000-2024": Standard & Poor's composite index (1941-43=10), end
#           of year, and S&P dividend-price ratio (percent). Publisher: Council of Economic
#           Advisers / U.S. Government Publishing Office.
#           https://www.govinfo.gov/content/pkg/ERP-2025/pdf/ERP-2025-table56.pdf
SP500_EOY = {2000: 1320.28, 2001: 1148.08, 2002: 879.82, 2003: 1111.92, 2004: 1211.92,
             2005: 1248.29, 2006: 1418.30, 2007: 1468.36, 2008: 903.25, 2009: 1115.10,
             2010: 1257.64, 2011: 1257.60, 2012: 1426.19, 2013: 1848.36, 2014: 2058.90,
             2015: 2043.94, 2016: 2238.83, 2017: 2673.61, 2018: 2506.85, 2019: 3230.78,
             2020: 3756.07, 2021: 4766.18, 2022: 3839.50, 2023: 4769.83}
SP500_DIVYLD = {2000: 1.15, 2001: 1.32, 2002: 1.61, 2003: 1.77, 2004: 1.72, 2005: 1.83,
                2006: 1.87, 2007: 1.86, 2008: 2.37, 2009: 2.40, 2010: 1.98, 2011: 2.05,
                2012: 2.24, 2013: 2.14, 2014: 2.04, 2015: 2.10, 2016: 2.19, 2017: 1.97,
                2018: 1.90, 2019: 1.93, 2020: 1.89, 2021: 1.38, 2022: 1.57, 2023: 1.62}

# TSP_C   Thrift Savings Plan C Fund (S&P 500 index fund run for federal employees),
#         calendar-year rates of return after expenses, percent, as published (whole
#         percents) in "Fund Information" (May 2026). Since inception (Jan. 29, 1988) the
#         published annualized return is 11.34%; "Growth of $100" 1/88 -> 12/25: $5,869
#         against $281 for inflation. Publisher: Federal Retirement Thrift Investment Board.
#         https://www.tsp.gov/publications/tsplf14.pdf
TSP_C = {2016: 12, 2017: 22, 2018: -5, 2019: 32, 2020: 18, 2021: 28, 2022: -18, 2023: 26,
         2024: 25, 2025: 18}
TSP_C_SINCE_1988 = 11.34      # percent per year, published
TSP_F_2022 = -13.0            # bond index fund, calendar 2022, published
TSP_G_OVER_TBILL = 1.48       # G Fund minus 90-day T-bill, April 1987 - Dec 2025, published


def pct_change(series, year):
    """Year-over-year change of an index series, as a fraction."""
    return series[year] / series[year - 1] - 1.0


def equity_return(year):
    """Total-return proxy for U.S. large-company stocks in a calendar year (fraction).

    2016-2025: TSP C Fund published calendar-year return (official, after expenses).
    2001-2015: S&P 500 end-of-year price change plus the S&P dividend-price ratio, both
               from the Economic Report of the President (official table). Cross-check:
               for 2016-2023 this method reproduces the TSP C Fund figures within one
               percentage point every year.
    1971-2000: OECD share-price index change. PRICE ONLY (no dividends) - a conservative
               proxy, flagged on the site.
    """
    if year in TSP_C:
        return TSP_C[year] / 100.0
    if year - 1 in SP500_EOY and year in SP500_EOY:
        return SP500_EOY[year] / SP500_EOY[year - 1] - 1.0 + SP500_DIVYLD[year] / 100.0
    return pct_change(SHARE_PX, year)
