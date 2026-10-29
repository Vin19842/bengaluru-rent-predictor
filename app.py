"""Bengaluru rent market dashboard using recent observed data."""
from pathlib import Path
import re

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
MARKET_DIR = ROOT / "data" / "market"
PAID_INDEX = MARKET_DIR / "bengaluru-rent-index-2026-10.csv"
ASKING_SOURCES = MARKET_DIR / "koramangala-source-snapshots-2026-10.csv"
LISTING_SAMPLE = MARKET_DIR / "koramangala-asking-listings-2026-10.csv"

GROWTH_RATES = {
    "Urban rent inflation (2.22%)": 2.22,
    "General urban CPI (4.88%)": 4.88,
    "Bengaluru residential trend (10.4% annualized)": 10.38,
    "Custom assumption": None,
}
GROWTH_HELP = {
    "Urban rent inflation (2.22%)": "India urban CPI inflation for actual rental payments, Sep 2026. National indicator, not Bengaluru-specific.",
    "General urban CPI (4.88%)": "India urban general CPI inflation, Sep 2026. General consumer inflation is not the same as Bengaluru rent growth.",
    "Bengaluru residential trend (10.4% annualized)": "JLL reported residential rents rose 2.5% quarter over quarter in Q2 2026. Annualizing one quarter is only a high-growth scenario, not a reliable long-term forecast.",
}

st.set_page_config(page_title="Bengaluru Rent Market Dashboard", page_icon="🏠", layout="wide")
st.title("🏠 Bengaluru Rent Market Dashboard")
st.caption("Current paid-rent reports and advertised asking prices are shown separately because they measure different things.")


def inr(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"₹{float(value):,.0f}"


def clean_locality(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


@st.cache_data
def read_csv(path: str) -> pd.DataFrame:
    file = Path(path)
    return pd.read_csv(file) if file.exists() else pd.DataFrame()


paid = read_csv(str(PAID_INDEX))
source_snapshot = read_csv(str(ASKING_SOURCES))
listing_sample = read_csv(str(LISTING_SAMPLE))

if paid.empty:
    st.error("The current Bengaluru Rent Index CSV is missing. Check data/README.md for the source and setup.")
    st.stop()

with st.sidebar:
    st.header("Market filters")
    locality_names = sorted(paid["area"].dropna().astype(str).unique().tolist())
    locality = st.selectbox("Locality", locality_names, index=locality_names.index("Koramangala") if "Koramangala" in locality_names else 0)
    bhk = st.selectbox("Bedrooms", [1, 2, 3], index=1)
    st.caption("The paid-rent index covers 31 area/BHK combinations. Asking-listing examples in this project are currently available only for Koramangala 2 BHK.")

selected = paid.loc[(paid["area"] == locality) & (pd.to_numeric(paid["bhk"], errors="coerce") == bhk)]
selected_row = selected.iloc[0] if not selected.empty else None

tab_overview, tab_estimator, tab_sources, tab_method = st.tabs([
    "Market overview", "Rent estimate", "Source comparison", "Data & methodology"
])

with tab_overview:
    st.subheader(f"{locality} · {bhk} BHK")
    st.caption("Tenant-reported paid-rent index · 90-day window ending 6 October 2026")
    if selected_row is None:
        st.info("No paid-rent row is available for this locality and BHK in the current index.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Reported median paid rent", inr(selected_row["median_rent_inr_90d"]), f"{selected_row['change_pct']:+.1f}% vs previous 90 days" if pd.notna(selected_row["change_pct"]) else None)
        m2.metric("Reports in latest window", f"{int(selected_row['reports_90d']):,}")
        m3.metric("Previous 90-day median", inr(selected_row["median_rent_inr_prev_90d"]))
        m4.metric("Previous window reports", f"{int(selected_row['reports_prev_90d']):,}")

    st.markdown("#### Compare localities")
    bhk_rows = paid.loc[pd.to_numeric(paid["bhk"], errors="coerce") == bhk].sort_values("median_rent_inr_90d", ascending=False)
    chart_data = bhk_rows.set_index("area")[["median_rent_inr_90d"]]
    st.bar_chart(chart_data, horizontal=True, x_label="Monthly rent (₹)", y_label="Locality")
    show_cols = ["area", "median_rent_inr_90d", "reports_90d", "median_rent_inr_prev_90d", "change_pct"]
    view = bhk_rows[show_cols].rename(columns={
        "area": "Locality", "median_rent_inr_90d": "Median paid rent (₹)",
        "reports_90d": "Reports", "median_rent_inr_prev_90d": "Previous median (₹)", "change_pct": "Change (%)",
    })
    st.dataframe(view, hide_index=True, use_container_width=True)
    st.caption("Source: Bengaluru Rent Index, tenant-reported paid rents. This is not an advertised asking-price index.")

with tab_estimator:
    st.subheader("Estimate with evidence, not a made-up point prediction")
    st.write("Choose the basis that matches your question. A tenant-paid median and an advertised listing price should not be averaged together.")
    c1, c2, c3 = st.columns(3)
    with c1:
        area_sqft = st.number_input("Property size (sq ft)", min_value=150, max_value=10000, value=1400, step=50)
    with c2:
        area_basis = st.selectbox("Area measurement", ["carpet", "super", "covered", "unknown / mixed"])
    with c3:
        target_year = st.selectbox("Estimate year", [2026, 2027, 2028, 2029], index=0)
    size_tolerance = st.select_slider("Comparable size tolerance", options=[10, 15, 20, 25, 30, 40], value=25, format_func=lambda value: f"±{value}%")

    growth_name = st.selectbox("Growth scenario", list(GROWTH_RATES))
    if growth_name == "Custom assumption":
        annual_rate = st.number_input("Custom annual rate (%)", min_value=-10.0, max_value=30.0, value=4.0, step=0.5)
        growth_note = "User-entered scenario assumption."
    else:
        annual_rate = GROWTH_RATES[growth_name]
        growth_note = GROWTH_HELP[growth_name]
    st.caption(growth_note)

    if selected_row is None:
        st.warning("There is no current paid-rent benchmark for this locality/BHK combination.")
    else:
        paid_base = float(selected_row["median_rent_inr_90d"])
        paid_projected = paid_base * (1 + float(annual_rate) / 100) ** (target_year - 2026)
        st.markdown("##### Tenant-paid market anchor")
        p1, p2 = st.columns(2)
        p1.metric(f"{target_year} scenario from paid-rent median", f"{inr(paid_projected)} / month", f"Base: {inr(paid_base)} · {int(selected_row['reports_90d'])} recent reports")
        p2.metric("Recent reported change", f"{float(selected_row['change_pct']):+.1f}%" if pd.notna(selected_row["change_pct"]) else "Not available", "90-day window vs prior 90 days")

    if locality == "Koramangala" and bhk == 2 and not listing_sample.empty:
        st.markdown("##### Similar advertised listings")
        st.caption(f"These are portal asking prices, not agreed rents. Matching uses the selected area basis and a ±{size_tolerance}% size band; it does not account for exact block, building quality or duplicate reposts.")
        sample = listing_sample.copy()
        sample["rent_inr"] = pd.to_numeric(sample["rent_inr"], errors="coerce")
        sample["area_sqft"] = pd.to_numeric(sample["area_sqft"], errors="coerce")
        if area_basis == "unknown / mixed":
            basis_sample = sample
            st.info("You selected mixed measurement types. Carpet, super and covered areas are not directly comparable; the sample below is descriptive only.")
        else:
            basis_sample = sample.loc[sample["area_basis"].str.lower() == area_basis]
        comparable = basis_sample.dropna(subset=["rent_inr", "area_sqft"]).loc[
            (basis_sample["area_sqft"] >= area_sqft * (1 - size_tolerance / 100)) & (basis_sample["area_sqft"] <= area_sqft * (1 + size_tolerance / 100))
        ].copy()
        if not comparable.empty:
            comp_median = float(comparable["rent_inr"].median())
            comp_low = float(comparable["rent_inr"].quantile(0.25))
            comp_high = float(comparable["rent_inr"].quantile(0.75))
            years = target_year - 2026
            st.write(f"**{len(comparable)} size/basis matches** between {area_sqft * (1 - size_tolerance / 100):,.0f} and {area_sqft * (1 + size_tolerance / 100):,.0f} sq ft")
            if len(comparable) >= 5:
                est_low = comp_low * (1 + float(annual_rate) / 100) ** years
                est_mid = comp_median * (1 + float(annual_rate) / 100) ** years
                est_high = comp_high * (1 + float(annual_rate) / 100) ** years
                st.metric(f"Indicative {target_year} asking range (middle half of sample)", f"{inr(est_low)} – {inr(est_high)} / month", f"Sample median {inr(est_mid)} · n={len(comparable)}")
            else:
                st.metric("Observed comparable listing(s)", f"{inr(comp_median)} / month", f"Only {len(comparable)} match(es); too few to call this a reliable estimate")
                st.warning("The matched sample is too small to produce a trustworthy property-level range. Use the comparable as one reference and check the live source listings below.")
            table_cols = ["rent_inr", "area_sqft", "area_basis", "furnishing", "bathrooms", "maintenance_inr", "posted_on"]
            display = comparable[table_cols].rename(columns={
                "rent_inr": "Asking rent (₹)", "area_sqft": "Area (sq ft)", "area_basis": "Area basis",
                "furnishing": "Furnishing", "bathrooms": "Bathrooms", "maintenance_inr": "Maintenance (₹)", "posted_on": "Posted date",
            })
            st.dataframe(display, hide_index=True, use_container_width=True)
        else:
            st.info("No same-area-basis listings fell within the selected size band. Widen the size band only after collecting more comparable records; this app will not invent a number.")
        st.markdown("[Open current Koramangala 2 BHK listings on Magicbricks](https://www.magicbricks.com/2-bhk-flats-for-rent-in-koramangala-bangalore-pppfr)")
        st.caption("The manually captured listing sample was viewed on 29 Oct 2026. Portal cards can be stale, duplicated or unavailable by the time you open them. It is a small research sample, not a retrained model.")
    else:
        st.info("A recent property-level asking-listing sample is not available for this locality/BHK yet. The output above is the neighborhood paid-rent median, not a size-adjusted quote.")

with tab_sources:
    st.subheader("Koramangala 2 BHK: why sources disagree")
    st.write("The first two sources summarize what renters say they pay. The next sources measure asking prices in posts or portals. Their populations, periods and verification differ, so the dashboard keeps each source separate instead of blending them into one average.")
    if source_snapshot.empty:
        st.info("No cross-source snapshot file is available.")
    else:
        display = source_snapshot.copy()
        display["Observed rent"] = display.apply(
            lambda r: f"p25 {inr(r['low_inr'])} · median {inr(r['central_inr'])} · p75 {inr(r['high_inr'])}" if pd.notna(r["low_inr"]) and pd.notna(r["high_inr"]) and pd.notna(r["central_inr"])
            else (f"{inr(r['low_inr'])}–{inr(r['high_inr'])}" if pd.notna(r["low_inr"]) and pd.notna(r["high_inr"])
            else inr(r["central_inr"]) if pd.notna(r["central_inr"]) else f"{inr(r['low_inr'])}–{inr(r['high_inr'])}" if pd.notna(r["low_inr"]) or pd.notna(r["high_inr"]) else "—"), axis=1
        )
        display["Source / method"] = display["source"] + " · " + display["measure"]
        display["Sample"] = display["sample_count"].astype(str)
        display["Period / updated"] = display["observation_period"] + " · page date " + display["source_as_of"].astype(str)
        display["Notes"] = display["interpretation"]
        st.dataframe(display[["Source / method", "Observed rent", "Sample", "Period / updated", "Notes", "source_url"]], hide_index=True, use_container_width=True, column_config={"source_url": st.column_config.LinkColumn("Source link", display_text="Open source")})
    st.markdown("#### What this says for the 1,400 sq ft example")
    st.write("A recent tenant-paid index reports ₹25,000 (22 reports), while other renter/post aggregates report around ₹33,000. Portal asking prices are wider and include premium furnished societies; a current portal page shows examples from ₹47,000 to ₹1,00,000 and a broad advertised range. For the default 1,400 sq ft carpet-area property, the manually captured page sample has four carpet-area matches within ±25%, with a ₹60,000 median. That is a useful comparison but too few listings to call a reliable prediction; exact block and property quality matter.")

with tab_method:
    st.subheader("Data quality and model status")
    st.markdown("""
    **Why the old ML number failed:** the Random Forest was trained on 2022 listings. Its random holdout MAE was ₹7,528, and that split did not test whether it generalizes to today's market. It is retained for learning but is not used by this dashboard.

    **Why this version does not retrain yet:** 17 visible portal rows from one locality/BHK are a useful comparable sample, not a safe training set. A credible model needs hundreds or thousands of unique, recent property-level rows across localities, clean area measurement types, stable listing IDs for deduplication, and a time-based holdout. Aggregated area medians and Reddit anecdotes do not provide the feature/label pairs needed for that model.

    **Data collection status:** the portal examples are a manually recorded, dated research snapshot. The app does not run a crawler. Magicbricks' terms require prior written consent for automated extraction, and Reddit's Data API terms prohibit using user content to train ML without the relevant rights-holder's express permission. A production crawler or Reddit training corpus needs permission and the approved API route.

    **Forecast status:** 2027–2029 values compound a selected growth assumption from an observed current figure. They are scenarios, not learned predictions. Brokerage is excluded; it is usually a one-time fee, not monthly rent.
    """)
    st.markdown("Sources: [Bengaluru Rent Index](https://bengaluru.rent/bengaluru-rent-index) · [MyBharat Rent](https://mybharat.rent/rent-in/bengaluru/koramangala/2-bhk-for-rent) · [Ghar4 Rent](https://www.ghar4.rent/areas/koramangala-bengaluru/2-bhk) · [Magicbricks](https://www.magicbricks.com/2-bhk-flats-for-rent-in-koramangala-bangalore-pppfr) · [Reddit Data API Terms](https://redditinc.com/policies/data-api-terms) · [Magicbricks Terms](https://property.magicbricks.com/terms/terms.html)")

