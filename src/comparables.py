"""Comparable listing selection helpers shared by the dashboard and tests."""

import pandas as pd

COMPARABLE_COLUMNS = {"bhk", "rent_inr", "area_sqft", "area_basis"}


def select_comparables(
    listings: pd.DataFrame,
    *,
    bhk: int,
    area_sqft: float,
    area_basis: str,
    size_tolerance_pct: int,
) -> pd.DataFrame:
    """Filter asking listings by bedroom count, area basis, and size band."""
    missing = COMPARABLE_COLUMNS.difference(listings.columns)
    if missing:
        raise ValueError(f"Listing data is missing required columns: {', '.join(sorted(missing))}.")
    if area_sqft <= 0:
        raise ValueError("Area must be greater than zero.")
    if not 0 <= size_tolerance_pct <= 100:
        raise ValueError("Size tolerance must be between 0 and 100 percent.")

    rows = listings.copy()
    for column in ("bhk", "rent_inr", "area_sqft"):
        rows[column] = pd.to_numeric(rows[column], errors="coerce")
    rows["area_basis"] = rows["area_basis"].fillna("unknown").astype(str).str.casefold()
    if area_basis.casefold() != "unknown / mixed":
        rows = rows.loc[rows["area_basis"] == area_basis.casefold()]
    lower = area_sqft * (1 - size_tolerance_pct / 100)
    upper = area_sqft * (1 + size_tolerance_pct / 100)
    return rows.loc[
        (rows["bhk"] == bhk)
        & rows["rent_inr"].notna()
        & rows["area_sqft"].between(lower, upper)
    ].copy()

