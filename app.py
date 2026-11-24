import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from scipy.stats import linregress

st.set_page_config(page_title="USD/INR IFM Dashboard", page_icon="💱", layout="wide")
st.title("International Financial Management – USD/INR Dashboard")
st.caption("Monthly analysis | January 2020–October 2026 | Exchange rate quoted as INR per USD")

DATA = Path(__file__).parent / "data" / "calculated_metrics.csv"
df = pd.read_csv(DATA, parse_dates=["date"]).sort_values("date")

with st.expander("Data sources and important coverage note", expanded=True):
    st.markdown("""
    - **USD/INR:** FRED `DEXINUS` (daily observations; last available quote in each month).
    - **US CPI:** FRED `CPIAUCNS` (monthly, not seasonally adjusted).
    - **India CPI:** FRED `INDCPALTT01IXNBM`.
    - **US interest rate:** FRED `FEDFUNDS`.
    - **India interest rate:** FRED `IRSTCI01INM156N`.

    The supplied India CPI file ends in **November 2023**. Therefore PPP and India-inflation-based IFE calculations cannot be extended beyond the months supported by that series. One US CPI month is also missing in the supplied file. Missing values are retained as missing and are not imputed.
    """)

tab1, tab2, tab3, tab4 = st.tabs([
    "1. PPP & Misalignment", "2. Interest Rates & Carry", "3. International Fisher Effect", "Data"
])

with tab1:
    st.subheader("Purchasing Power Parity")
    ppp = df.dropna(subset=["usd_inr", "ppp_usdinr", "misalignment_pct"]).copy()
    if ppp.empty:
        st.warning("PPP cannot be calculated because the CPI inputs are unavailable.")
    else:
        latest = ppp.iloc[-1]
        status = ("USD relatively overvalued / INR relatively undervalued"
                  if latest["misalignment_pct"] > 0 else
                  "USD relatively undervalued / INR relatively overvalued"
                  if latest["misalignment_pct"] < 0 else "At PPP benchmark")
        c1,c2,c3 = st.columns(3)
        c1.metric("Latest actual USD/INR", f'{latest["usd_inr"]:.2f}')
        c2.metric("Latest PPP-implied USD/INR", f'{latest["ppp_usdinr"]:.2f}')
        c3.metric("Misalignment", f'{latest["misalignment_pct"]:.2f}%')
        st.info(f"Interpretation for {latest['date']:%B %Y}: {status}.")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ppp.date, y=ppp.usd_inr, name="Actual USD/INR"))
        fig.add_trace(go.Scatter(x=ppp.date, y=ppp.ppp_usdinr, name="PPP-implied USD/INR"))
        fig.update_layout(title="Actual vs PPP-implied USD/INR", xaxis_title="Month",
                          yaxis_title="INR per USD", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Relative PPP: S₀ × (India CPIₜ / India CPI₀) ÷ (US CPIₜ / US CPI₀). Misalignment = (Actual / PPP − 1) × 100.")
        st.caption(f"PPP observations available: {len(ppp)} of {len(df)} months. The available India CPI series ends in November 2023.")

with tab2:
    st.subheader("Interest-rate differential and simplified carry trade")
    rate = df.dropna(subset=["rate_diff_us_minus_india"]).copy()
    carry = df.dropna(subset=["carry_gross_return_12m_pct"]).copy()
    if not rate.empty:
        latest = rate.iloc[-1]
        c1,c2,c3 = st.columns(3)
        c1.metric("US rate", f'{latest["us_rate"]:.2f}%')
        c2.metric("India rate", f'{latest["india_rate"]:.2f}%')
        c3.metric("US − India differential", f'{latest["rate_diff_us_minus_india"]:.2f} pp')
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=rate.date, y=rate.rate_diff_us_minus_india, name="US − India rate differential"))
        if rate.annual_spot_change_pct.notna().any():
            fig.add_trace(go.Scatter(x=rate.date, y=rate.annual_spot_change_pct, name="Trailing 12-month USD/INR change", yaxis="y2"))
        fig.update_layout(title="Interest-rate differential and trailing 12-month spot change",
                          xaxis_title="Month", yaxis=dict(title="Rate differential (percentage points)"),
                          yaxis2=dict(title="Spot change (%)", overlaying="y", side="right"),
                          hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("**Carry-trade model**")
    st.write("Borrow INR, convert to USD, invest at the US rate, then convert back to INR after 12 months.")
    if not carry.empty:
        c1,c2,c3 = st.columns(3)
        c1.metric("Valid 12-month trade starts", f"{len(carry)}")
        c2.metric("Average realised return", f'{carry.carry_gross_return_12m_pct.mean():.2f}%')
        c3.metric("Positive outcomes", f'{(carry.carry_gross_return_12m_pct > 0).sum()} / {len(carry)}')
        fig2 = px.bar(carry, x="date", y="carry_gross_return_12m_pct",
                      title="Simplified realised 12-month carry-trade return",
                      labels={"date":"Trade start month","carry_gross_return_12m_pct":"Return (%)"})
        fig2.add_hline(y=0, line_dash="dash")
        st.plotly_chart(fig2, use_container_width=True)
        st.line_chart(carry.set_index("date")[["carry_profitability_index"]])
    else:
        st.warning("No complete 12-month carry observations are available.")
    st.caption("Carry return = {[(1 + US rate) × (Sₜ₊₁₂ / Sₜ) / (1 + India rate)] − 1} × 100. Rates are converted from percentages to decimals.")
    st.caption("This is a simplified unhedged historical calculation; transaction costs, bid-ask spreads, taxes and funding frictions are excluded.")
    st.caption("For S quoted as INR per USD, a positive US-minus-India rate differential implies expected USD depreciation (a fall in USD/INR) under basic UIP. The chart is descriptive, not a formal UIP test.")

with tab3:
    st.subheader("International Fisher Effect")
    ife = df.dropna(subset=["inflation_diff_us_minus_india","rate_diff_us_minus_india"]).copy()
    c1,c2 = st.columns(2)
    c1.metric("Complete paired observations", f"{len(ife)}")
    if len(ife) >= 10:
        res = linregress(ife["inflation_diff_us_minus_india"], ife["rate_diff_us_minus_india"])
        c2.metric("Pearson correlation", f"{res.rvalue:.3f}")
        fig = px.scatter(ife, x="inflation_diff_us_minus_india", y="rate_diff_us_minus_india",
                         trendline="ols", title="Inflation differential vs nominal interest-rate differential",
                         labels={"inflation_diff_us_minus_india":"US − India inflation differential (pp)",
                                 "rate_diff_us_minus_india":"US − India nominal rate differential (pp)"})
        st.plotly_chart(fig, use_container_width=True)
        st.write(f"OLS equation: Rate differential = {res.intercept:.3f} + ({res.slope:.3f} × inflation differential)")
        st.write(f"R-squared: {res.rvalue**2:.3f}")
        st.write("A positive relationship is generally expected under the IFE. This sample's estimated relationship should be interpreted from the displayed correlation and slope, not assumed in advance.")
    else:
        st.warning("Fewer than 10 complete paired observations are available; correlation and regression are not displayed.")
    st.caption("IFE theory concerns expected inflation. This dashboard uses realised year-on-year CPI inflation as a proxy, which is a limitation.")

with tab4:
    st.subheader("Combined monthly dataset")
    st.write("Use the table filters to inspect the monthly source variables and calculated metrics.")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Download calculated metrics CSV", df.to_csv(index=False).encode("utf-8"),
                       "usd_inr_calculated_metrics.csv", "text/csv")
    raw_path = Path(__file__).parent / "data" / "combined_monthly_raw.csv"
    if raw_path.exists():
        raw_bytes = raw_path.read_bytes()
        st.download_button("Download combined raw monthly CSV", raw_bytes,
                           "usd_inr_combined_monthly_raw.csv", "text/csv")
