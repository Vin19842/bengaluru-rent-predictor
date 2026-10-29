"""Streamlit interface for the Bengaluru rent estimator."""
from pathlib import Path
import re

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / "models" / "bengaluru_rent_model.joblib"
MARKET_INDEX = ROOT / "data" / "market" / "bengaluru-rent-index-2026-10.csv"

st.set_page_config(page_title="Bengaluru Rent Estimator", page_icon="🏠", layout="centered")
st.title("🏠 Bengaluru Rent Estimator")
st.caption("A learning project that estimates monthly residential rent from listing details.")

if not MODEL.exists():
    st.error("The model has not been trained yet. Follow the setup steps in README.md.")
    st.stop()

bundle = joblib.load(MODEL)
model = bundle["model"]
options = bundle["options"]
localities = options["localities"]


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
    # Historical source names sometimes include a block or sector after the area.
    partial = candidates.loc[candidates["_area_key"].map(lambda area: key.startswith(area + " "))]
    if not partial.empty:
        return partial.sort_values("_area_key", key=lambda column: column.str.len(), ascending=False).iloc[0]
    return None


market_index = load_market_index()

with st.form("rent_inputs"):
    st.subheader("Describe the property")
    a, b = st.columns(2)
    with a:
        bhk = st.selectbox("Bedrooms (BHK)", [1, 2, 3, 4, 5], index=1)
        size = st.number_input("Area (sq ft)", min_value=150, max_value=10000, value=1000, step=50)
        bathroom = st.selectbox("Bathrooms", [1, 2, 3, 4, 5], index=1)
        locality = st.selectbox("Locality", localities, index=0 if localities else None)
    with b:
        area_type = st.selectbox("Area measurement", options["area_types"])
        furnishing = st.selectbox("Furnishing", ["Unfurnished", "Semi-Furnished", "Furnished"])
        tenant = st.selectbox("Tenant preference", options["tenant_preferences"])
    submitted = st.form_submit_button("Estimate monthly rent", type="primary", use_container_width=True)

if submitted:
    example = pd.DataFrame([{
        "BHK": bhk, "Size": size, "Bathroom": bathroom,
        "Area Type": area_type, "Area Locality": locality,
        "Furnishing Status": furnishing, "Tenant Preferred": tenant,
    }], columns=bundle["features"])
    model_estimate = max(0, float(model.predict(example)[0]))
    market_row = find_market_row(market_index, locality, bhk)

    st.subheader("Property-level model estimate")
    st.metric("Model trained on 2022 listings", f"₹{model_estimate:,.0f} / month")
    st.caption("This estimate uses size, bathrooms, furnishing and other property details, but its training listings are from 2022.")

    if market_row is not None:
        st.subheader("Recent neighborhood benchmark")
        st.metric(f"{market_row['area']} · {bhk} BHK median paid rent", f"₹{int(market_row['median_rent_inr_90d']):,} / month")
        st.caption(f"Based on {int(market_row['reports_90d'])} tenant reports from the 90 days ending 6 Oct 2026. This is a neighborhood/bedroom benchmark, not adjusted for size, bathrooms or furnishing.")
        gap_pct = (model_estimate / float(market_row["median_rent_inr_90d"]) - 1) * 100
        if abs(gap_pct) >= 20:
            st.info(f"The 2022 property model differs from the recent area median by {abs(gap_pct):.0f}%. Use the current benchmark for market context; the listing-based model may be stale or uncertain.")
    else:
        st.info("No recent rent-index row is available for this locality and bedroom count. Treat the 2022 model output as a rough historical reference.")

with st.expander("About this estimate"):
    st.write("The property-level model was trained on advertised listings posted in 2022. Its random-holdout score in `models/metrics.json` does not measure accuracy on current listings.")
    st.write("The recent benchmark comes from bengaluru.rent's October 2026 index of tenant-reported rents. It is aggregated by neighborhood and BHK, so it cannot train a property-level model by itself. See `data/README.md` for sources and limitations.")

