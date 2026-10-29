"""Current-market Bengaluru rent benchmark and transparent scenario planner."""
from pathlib import Path
import re

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
MARKET_INDEX = ROOT / "data" / "market" / "bengaluru-rent-index-2026-10.csv"

# September 2026 official CPI release. These are scenario assumptions, not
# learned Bengaluru rent-growth coefficients.
INFLATION_SCENARIOS = {
    "India urban housing rent inflation (2.22%)": 2.22,
    "India urban CPI inflation (4.88%)": 4.88,
    "Bengaluru residential trend (10.4% annualized)": 10.38,
    "Custom annual growth rate": None,
}
SCENARIO_NOTES = {
    "India urban housing rent inflation (2.22%)": "Official year-over-year inflation for actual rental payments in India's urban CPI basket, September 2026. It is a broad national indicator, not Bengaluru-only.",
    "India urban CPI inflation (4.88%)": "Official year-over-year urban CPI inflation for September 2026. General consumer inflation is not the same as rent growth.",
    "Bengaluru residential trend (10.4% annualized)": "JLL reported Bengaluru residential rents rose 2.5% quarter over quarter in Q2 2026. This converts that single quarter's pace to an annual compound rate; it is an illustrative high-growth scenario, not a long-term forecast.",
}

st.set_page_config(page_title="Bengaluru Rent Estimator", page_icon="🏠", layout="centered")
st.title("🏠 Bengaluru Rent Estimator")
st.caption("Current neighborhood rent benchmarks with transparent future-year scenarios.")


def normalize_area(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


@st.cache_data
def load_market_index() -> pd.DataFrame:
    if not MARKET_INDEX.exists():
        return pd.DataFrame()
    return pd.read_csv(MARKET_INDEX)


def find_market_row(index: pd.DataFrame, locality: str, bedrooms: int):
    if index.empty:
        return None
    candidates = index.loc[pd.to_numeric(index["bhk"], errors="coerce") == bedrooms].copy()
    key = normalize_area(locality)
    candidates["_area_key"] = candidates["area"].map(normalize_area)
    exact = candidates.loc[candidates["_area_key"] == key]
    if not exact.empty:
        return exact.iloc[0]
    partial = candidates.loc[candidates["_area_key"].map(lambda area: key.startswith(area + " "))]
    if not partial.empty:
        return partial.sort_values("_area_key", key=lambda col: col.str.len(), ascending=False).iloc[0]
    return None


market_index = load_market_index()
if market_index.empty:
    st.error("The recent market benchmark file is missing. See data/README.md for its source and setup.")
    st.stop()

areas = sorted(market_index["area"].dropna().astype(str).unique().tolist())
with st.form("rent_inputs"):
    st.subheader("Describe the property")
    left, right = st.columns(2)
    with left:
        bhk = st.selectbox("Bedrooms (BHK)", [1, 2, 3, 4, 5], index=1)
        locality = st.selectbox("Locality", areas, index=areas.index("Koramangala") if "Koramangala" in areas else 0)
        area_sqft = st.number_input("Area (sq ft) · reference only", min_value=150, max_value=10000, value=1000, step=50)
    with right:
        target_year = st.selectbox("Estimate for year", [2026, 2027, 2028, 2029], index=0)
        growth_scenario = st.selectbox("Annual growth scenario", list(INFLATION_SCENARIOS))
        if growth_scenario == "Custom annual growth rate":
            annual_growth = st.number_input("Custom annual growth (%)", min_value=-10.0, max_value=30.0, value=4.0, step=0.5)
        else:
            annual_growth = INFLATION_SCENARIOS[growth_scenario]
            st.caption(f"Assumption: {annual_growth:.2f}% per year")
    agent_premium = st.slider("Optional agent-involved asking premium (%)", min_value=0, max_value=30, value=0, step=1)
    st.caption("This is an optional scenario adjustment only. Brokerage is usually a one-time fee, so it is not included in monthly rent by default.")
    submitted = st.form_submit_button("Estimate rent", type="primary", use_container_width=True)

if submitted:
    row = find_market_row(market_index, locality, bhk)
    if row is None:
        st.warning(f"The latest market index has no {bhk} BHK benchmark for {locality}. Choose another listed locality or BHK.")
    else:
        base_rent = float(row["median_rent_inr_90d"])
        report_count = int(row["reports_90d"])
        years_forward = max(target_year - 2026, 0)
        projected = base_rent * ((1 + float(annual_growth) / 100) ** years_forward)
        projected *= 1 + agent_premium / 100

        st.subheader(f"{target_year} neighborhood estimate")
        st.metric(f"{row['area']} · {bhk} BHK", f"₹{projected:,.0f} / month")
        st.write(f"**Current observed benchmark:** ₹{base_rent:,.0f} / month")
        if years_forward:
            st.write(f"**Scenario calculation:** ₹{base_rent:,.0f} × (1 + {float(annual_growth):.2f}%)^{years_forward} × (1 + {agent_premium}%) = **₹{projected:,.0f} / month**")
        else:
            st.write("For 2026, the estimate is the latest observed neighborhood median with the optional asking premium applied.")
        st.caption(f"The observed median is based on {report_count} tenant reports in the 90 days ending 6 Oct 2026. {SCENARIO_NOTES.get(growth_scenario, 'The rate is a user-entered scenario assumption.')}")
        if agent_premium:
            st.info("The agent premium is user-selected and is not measured by the rent dataset. Compare it with 0% to see its effect.")
        st.warning("This is a neighborhood/BHK benchmark, not a property-specific valuation. The current dataset does not adjust for floor area, bathrooms, furnishing, amenities or building condition. Future values are scenarios, not guaranteed predictions.")

with st.expander("Why this estimate differs from the old model"):
    st.write("The original property model learned from 2022 advertised listings. For the screenshot example it estimated ₹17,222, while the recent Koramangala 2 BHK tenant-reported median is ₹25,000. The historical model's average test error was ₹7,528, and its random holdout did not test performance on today's market.")
    st.write("The recent index contains neighborhood-and-BHK medians, not individual homes with size, bathrooms and furnishing. It is not valid training data for a property-level machine-learning model. This app therefore uses the recent median as its anchor instead of presenting the stale model as today's property estimate.")
    st.write("The area figure is a median of reported rents, so it is a more defensible local starting point than the old model. It still may not represent every building or negotiated lease, and low report counts increase uncertainty.")
    st.markdown("Sources: [Bengaluru Rent Index](https://bengaluru.rent/bengaluru-rent-index) · [MoSPI September 2026 CPI release](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2322244&lang=1&reg=3) · [JLL Bengaluru Q2 2026 residential market](https://www.jll.com/en-in/insights/market-dynamics/bengaluru-residential)")

