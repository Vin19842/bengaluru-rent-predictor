"""Single-view Bengaluru rent dashboard backed by recent market snapshots."""
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
MARKET_DIR = ROOT / "data" / "market"
PAID_INDEX_PATH = MARKET_DIR / "bengaluru-rent-index-2026-10.csv"
SOURCE_SNAPSHOT_PATH = MARKET_DIR / "koramangala-source-snapshots-2026-10.csv"
LISTING_SAMPLE_PATH = MARKET_DIR / "koramangala-asking-listings-2026-10.csv"

PAID_REQUIRED = {
    "area", "bhk", "median_rent_inr_90d", "reports_90d",
    "median_rent_inr_prev_90d", "reports_prev_90d", "change_pct",
}
LISTING_REQUIRED = {"rent_inr", "area_sqft", "area_basis", "furnishing", "bathrooms", "maintenance_inr", "posted_on"}
GROWTH_RATES = {
    "Urban rent inflation · 2.22%": 2.22,
    "Urban CPI · 4.88%": 4.88,
    "Bengaluru residential trend · 10.38%": 10.38,
    "Custom assumption": None,
}
GROWTH_NOTES = {
    "Urban rent inflation · 2.22%": "India urban CPI inflation for actual rental payments, September 2026. It is a national indicator, not Bengaluru-specific.",
    "Urban CPI · 4.88%": "India urban general CPI inflation, September 2026. General inflation is not the same as rent growth.",
    "Bengaluru residential trend · 10.38%": "Annualized from JLL's reported 2.5% quarter-over-quarter Bengaluru residential rent rise in Q2 2026. One quarter is a scenario assumption, not a long-term forecast.",
}

st.set_page_config(page_title="Bengaluru Rent Dashboard", page_icon="🏠", layout="wide")
st.title("🏠 Bengaluru Rent Dashboard")
st.caption("Select a locality and home type. The KPIs, market chart, comparable listings and forecast all follow the filters.")


def inr(value) -> str:
    """Format a numeric rupee value without displaying NaN or None."""
    if value is None or pd.isna(value):
        return "—"
    return f"₹{float(value):,.0f}"


@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    """Read a project CSV and return an empty frame when an optional file is absent."""
    file = Path(path)
    if not file.is_file():
        return pd.DataFrame()
    return pd.read_csv(file)


try:
    paid = load_csv(str(PAID_INDEX_PATH))
    source_snapshot = load_csv(str(SOURCE_SNAPSHOT_PATH))
    listing_sample = load_csv(str(LISTING_SAMPLE_PATH))
except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
    st.error(f"A market data file could not be read: {error}")
    st.stop()

if paid.empty:
    st.error("The rent index is missing or empty. Restore data/market/bengaluru-rent-index-2026-10.csv and restart the app.")
    st.stop()
missing_columns = PAID_REQUIRED.difference(paid.columns)
if missing_columns:
    st.error(f"The rent index is missing required columns: {', '.join(sorted(missing_columns))}.")
    st.stop()

for column in ("bhk", "median_rent_inr_90d", "reports_90d", "median_rent_inr_prev_90d", "reports_prev_90d", "change_pct"):
    paid[column] = pd.to_numeric(paid[column], errors="coerce")
paid = paid.dropna(subset=["area", "bhk", "median_rent_inr_90d"]).copy()
paid["bhk"] = paid["bhk"].astype(int)
if paid.empty:
    st.error("The rent index has no usable locality and rent rows.")
    st.stop()

with st.sidebar:
    st.header("Estimate filters")
    locality_names = sorted(paid["area"].astype(str).unique().tolist())
    default_locality = "Koramangala" if "Koramangala" in locality_names else locality_names[0]
    locality = st.selectbox("Locality", locality_names, index=locality_names.index(default_locality))
    locality_rows = paid.loc[paid["area"].astype(str) == locality]
    available_bhks = sorted(locality_rows["bhk"].unique().tolist())
    default_bhk = 2 if 2 in available_bhks else available_bhks[0]
    bhk = st.selectbox("Bedrooms (BHK)", available_bhks, index=available_bhks.index(default_bhk))
    area_sqft = st.number_input("Property size (sq ft)", min_value=150, max_value=10000, value=1400, step=50)
    area_basis = st.selectbox("Area measurement", ["carpet", "super", "covered", "unknown / mixed"], format_func=lambda text: text.title() if text != "unknown / mixed" else "Unknown / mixed")
    size_tolerance = st.select_slider("Comparable size tolerance", options=[10, 15, 20, 25, 30, 40], value=25, format_func=lambda value: f"±{value}%")
    target_year = st.selectbox("Estimate year", [2026, 2027, 2028, 2029], index=0)
    growth_name = st.selectbox("Annual growth scenario", list(GROWTH_RATES))
    if growth_name == "Custom assumption":
        annual_rate = st.number_input("Annual growth (%)", min_value=-10.0, max_value=30.0, value=4.0, step=0.5)
        growth_note = "User-entered scenario; future values are not guaranteed."
    else:
        annual_rate = GROWTH_RATES[growth_name]
        growth_note = GROWTH_NOTES[growth_name]

    chart_type = st.selectbox("Chart view", [
        "Current rent by locality",
        "Selected locality · current vs previous (bar)",
        "Selected locality · rent trend (line)",
        "Rent change by locality",
        "Report volume by locality",
    ])

selected_rows = paid.loc[(paid["area"].astype(str) == locality) & (paid["bhk"] == bhk)]
if selected_rows.empty:
    st.error("No current paid-rent figure is available for the selected filters.")
    st.stop()
selected = selected_rows.iloc[0]
paid_base = float(selected["median_rent_inr_90d"])
years_forward = target_year - 2026
projected_paid = paid_base * (1 + float(annual_rate) / 100) ** years_forward

# Asking-listing comparables are intentionally limited to the locality/BHK for
# which recent property-level examples were manually captured.
comparable = pd.DataFrame()
if {"bhk", *LISTING_REQUIRED}.issubset(listing_sample.columns) and locality == "Koramangala" and bhk == 2:
    sample = listing_sample.copy()
    for column in ("bhk", "rent_inr", "area_sqft", "bathrooms", "maintenance_inr"):
        sample[column] = pd.to_numeric(sample[column], errors="coerce")
    sample["area_basis"] = sample["area_basis"].fillna("unknown").astype(str).str.casefold()
    if area_basis == "unknown / mixed":
        basis_rows = sample
        st.info("This includes carpet, super and covered area records together. Those measurements are not directly comparable; treat this sample as directional only.")
    else:
        basis_rows = sample.loc[sample["area_basis"] == area_basis]
    comparable = basis_rows.loc[
        (basis_rows["bhk"] == bhk)
        & basis_rows["rent_inr"].notna()
        & basis_rows["area_sqft"].notna()
        & basis_rows["area_sqft"].between(area_sqft * (1 - size_tolerance / 100), area_sqft * (1 + size_tolerance / 100))
    ].copy()

# Current market KPIs. Asking and paid-rent measures are never blended.
st.subheader(f"{locality} · {bhk} BHK rent estimate")
metric_row_1 = st.columns(3)
latest_reports = int(selected["reports_90d"]) if pd.notna(selected["reports_90d"]) else 0
prior_reports = int(selected["reports_prev_90d"]) if pd.notna(selected["reports_prev_90d"]) else 0
metric_row_1[0].metric("Latest reported paid median", f"{inr(paid_base)} / month", help=f"{latest_reports:,} tenant reports · 90 days ending 6 Oct 2026")
change = selected["change_pct"]
metric_row_1[1].metric("Change vs previous 90 days", f"{float(change):+.1f}%" if pd.notna(change) else "—", help="Change in the tenant-reported median between two 90-day windows")
metric_row_1[2].metric(f"{target_year} paid-rent scenario", f"{inr(projected_paid)} / month", help=f"Base {inr(paid_base)} · {annual_rate:.2f}% annual assumption · {years_forward} years")

metric_row_2 = st.columns(3)
metric_row_2[0].metric("Previous 90-day median", f"{inr(selected['median_rent_inr_prev_90d'])} / month", help=f"{prior_reports:,} reports in the previous window" if prior_reports else "Previous-window report count unavailable")
if not comparable.empty:
    comp_median = float(comparable["rent_inr"].median())
    metric_row_2[1].metric("Size-matched asking sample", f"{inr(comp_median)} / month", help=f"{len(comparable)} listings · {area_basis} · ±{size_tolerance}% size band · not a trained prediction")
else:
    metric_row_2[1].metric("Size-matched asking sample", "Not available", help="No matching listings for these filters")

portal_band = source_snapshot.loc[
    (source_snapshot["source"] == "Magicbricks")
    & (source_snapshot["measure"] == "portal asking range")
] if {"source", "measure", "low_inr", "high_inr"}.issubset(source_snapshot.columns) else pd.DataFrame()
if locality == "Koramangala" and bhk == 2 and not portal_band.empty:
    low, high = portal_band.iloc[0][["low_inr", "high_inr"]]
    metric_row_2[2].metric("Portal-wide asking range", f"{inr(low)}–{inr(high)}", help="Broad portal range across mixed sizes, blocks and property quality")
else:
    metric_row_2[2].metric("Portal-wide asking range", "Not available", help="No comparable source snapshot for this selection")

if years_forward:
    st.caption(growth_note)
st.caption("Paid-rent medians, asking-listing examples and portal-wide asking ranges describe different samples. Treat the future value as a scenario, not a guaranteed rent.")

st.divider()
chart_col, chart_info = st.columns([3, 1])
with chart_col:
    st.subheader(chart_type)
    bhk_rows = paid.loc[paid["bhk"] == bhk].copy()
    if chart_type == "Current rent by locality":
        chart_data = bhk_rows[["area", "median_rent_inr_90d"]].rename(columns={"area": "Locality", "median_rent_inr_90d": "Monthly rent (₹)"})
        chart_data["Selected locality"] = chart_data["Locality"].map(lambda name: "Selected" if name == locality else "Other")
        chart_data = chart_data.sort_values("Monthly rent (₹)", ascending=False)
        st.bar_chart(chart_data, x="Locality", y="Monthly rent (₹)", color="Selected locality", horizontal=True, sort="-Monthly rent (₹)")
    elif chart_type in {"Selected locality · current vs previous (bar)", "Selected locality · rent trend (line)"}:
        chart_data = pd.DataFrame({
            "Period": ["Previous 90 days", "Latest 90 days"],
            "Monthly rent (₹)": [selected["median_rent_inr_prev_90d"], selected["median_rent_inr_90d"]],
        }).dropna()
        if chart_type.endswith("(line)"):
            st.line_chart(chart_data.set_index("Period"), y="Monthly rent (₹)")
        else:
            st.bar_chart(chart_data, x="Period", y="Monthly rent (₹)", color="Period")
    elif chart_type == "Rent change by locality":
        chart_data = bhk_rows.dropna(subset=["change_pct"])[["area", "change_pct"]].rename(columns={"area": "Locality", "change_pct": "Change (%)"})
        chart_data["Selected locality"] = chart_data["Locality"].map(lambda name: "Selected" if name == locality else "Other")
        chart_data = chart_data.sort_values("Change (%)")
        st.bar_chart(chart_data, x="Locality", y="Change (%)", color="Selected locality", horizontal=True, sort="Change (%)")
    else:
        chart_data = bhk_rows[["area", "reports_90d"]].rename(columns={"area": "Locality", "reports_90d": "Reports"})
        chart_data["Selected locality"] = chart_data["Locality"].map(lambda name: "Selected" if name == locality else "Other")
        chart_data = chart_data.sort_values("Reports", ascending=False)
        st.bar_chart(chart_data, x="Locality", y="Reports", color="Selected locality", horizontal=True, sort="-Reports")

with chart_info:
    st.markdown("#### Reading this view")
    st.write(f"All market charts use {bhk} BHK records. **{locality}** is highlighted where the chart compares localities.")
    st.write("Change the filters in the left panel. The estimate cards and chart refresh together.")
    st.write("Current and previous values are separate 90-day windows; the chart is descriptive, not a time-series forecast.")

if locality == "Koramangala" and bhk == 2:
    st.markdown("#### Listings close to this property")
    if comparable.empty:
        st.info("No same-area-basis listing was found in this size band. Try another area basis or tolerance, or open the source page.")
    else:
        st.write(f"{len(comparable)} portal asking-price examples fall between {area_sqft * (1 - size_tolerance / 100):,.0f} and {area_sqft * (1 + size_tolerance / 100):,.0f} sq ft. These are comparisons, not a trained estimate.")
        display = comparable[["rent_inr", "area_sqft", "area_basis", "furnishing", "bathrooms", "maintenance_inr", "posted_on"]].rename(columns={
            "rent_inr": "Asking rent (₹)", "area_sqft": "Area (sq ft)", "area_basis": "Area basis",
            "furnishing": "Furnishing", "bathrooms": "Bathrooms", "maintenance_inr": "Maintenance (₹)", "posted_on": "Posted date",
        }).sort_values("Asking rent (₹)")
        st.dataframe(display, hide_index=True, width="stretch")
    st.markdown("[View current Koramangala 2 BHK listings](https://www.magicbricks.com/2-bhk-flats-for-rent-in-koramangala-bangalore-pppfr)")

with st.expander("Sources and estimate notes"):
    st.markdown("- Paid-rent index: [Bengaluru Rent Index](https://bengaluru.rent/bengaluru-rent-index), 90-day reports ending 6 Oct 2026.\n- Listing comparisons: a small, manually captured [Magicbricks search page](https://www.magicbricks.com/2-bhk-flats-for-rent-in-koramangala-bangalore-pppfr), viewed 29 Oct 2026. Listings can be stale or duplicated; maintenance is separate where shown.\n- CPI assumptions: [September 2026 official release](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2322244&lang=1&reg=3). Bengaluru trend scenario: [JLL Q2 2026](https://www.jll.com/en-in/insights/market-dynamics/bengaluru-residential).")
    st.caption("The original model was trained on 2022 listings and is not used in this dashboard. New observations are too small and narrow to train a reliable property-level model. The dashboard does not run a crawler or use Reddit content as training data.")

