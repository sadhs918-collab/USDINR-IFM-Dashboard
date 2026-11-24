# USD/INR IFM Dashboard

A three-tab Streamlit dashboard for an undergraduate International Financial Management assignment.

## Currency quote and period
- Pair: USD/INR, quoted as Indian rupees per one US dollar.
- Monthly dataset: January 2020 to October 2026 (82 calendar months).
- Daily USD/INR observations are converted to monthly observations using the last available daily quote in each month.

## Data sources (FRED series IDs)
| Variable | Series | Notes |
|---|---|---|
| USD/INR | `DEXINUS` | Daily; last available quote per month |
| US CPI | `CPIAUCNS` | Monthly, not seasonally adjusted |
| India CPI | `INDCPALTT01IXNBM` | Supplied monthly FRED series |
| US interest rate | `FEDFUNDS` | Monthly effective federal funds rate |
| India interest rate | `IRSTCI01INM156N` | Monthly India call money/interbank rate series |

The original five CSV downloads are retained in `data/`. The merged files are:
- `data/combined_monthly_raw.csv`
- `data/calculated_metrics.csv`

## Important coverage limitation
The uploaded India CPI file ends in **November 2023**, while the other monthly series extend to October 2026. Therefore:
- Relative PPP is available only for months with both country CPI series.
- India year-on-year inflation requires CPI observations 12 months apart and is available only while the India CPI series supports it.
- IFE uses only months with both inflation and interest-rate differentials available.
- No missing values are filled with zero or interpolated.

The uploaded US CPI file also contains a missing monthly observation; calculations depending on that month or its 12-month lag remain blank.

## Formulas
- US YoY inflation = `(US_CPI_t / US_CPI_(t-12) - 1) * 100`
- India YoY inflation = `(India_CPI_t / India_CPI_(t-12) - 1) * 100`
- Inflation differential = `US inflation - India inflation`
- Interest differential = `US rate - India rate` (percentage points)
- Relative PPP = `S0 * (India_CPI_t / India_CPI_0) / (US_CPI_t / US_CPI_0)`
- Misalignment = `(Actual USDINR / PPP USDINR - 1) * 100`
- Trailing spot change = `(S_t / S_(t-12) - 1) * 100`
- Carry return = `(((1 + US_rate/100) * (S_(t+12)/S_t) / (1 + India_rate/100)) - 1) * 100`
- Carry index = `100 * (1 + carry_return/100)`

## Interpretation
Since the exchange rate is INR per USD, an increase in USD/INR means USD appreciation and INR depreciation. Positive PPP misalignment means actual USD/INR is above the PPP benchmark (USD relatively overvalued, INR relatively undervalued). Under basic UIP, a positive US-minus-India interest differential implies expected USD depreciation, i.e. a fall in USD/INR. The historical comparison is descriptive, not a formal UIP test.

Carry-trade return is a simplified unhedged historical calculation. It excludes transaction costs, bid-ask spreads, taxes, capital controls, and funding constraints. IFE theory concerns expected inflation; realised CPI inflation is used here as a proxy. CIP cannot be tested without matched-maturity forward exchange rates.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository and upload the contents of this folder.
2. In Streamlit Community Cloud, connect the repository.
3. Set the main file path to `app.py`.
4. Deploy.

Do not upload API keys or private credentials. The dashboard reads its CSV data from the repository's `data/` folder.
