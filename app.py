"""Streamlit interface for the Bengaluru rent estimator."""
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / "models" / "bengaluru_rent_model.joblib"

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
    estimate = max(0, float(model.predict(example)[0]))
    st.metric("Estimated monthly rent", f"₹{estimate:,.0f}")
    st.caption("Use this as a learning/demo estimate. It is not a quote or a current market valuation.")

with st.expander("About this estimate"):
    st.write("The model was trained on historical rental listings posted in 2022. Its input locality names and property patterns come from that dataset, so the estimate may be inaccurate for newer listings or locations with few examples.")
    st.write("The test score is available in `models/metrics.json` after training. This score comes from a random holdout of the same historical dataset and does not measure future market accuracy.")

