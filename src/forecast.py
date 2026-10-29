"""Shared, deterministic rent scenario calculations."""

BASE_YEAR = 2026
FORECAST_YEARS = tuple(range(BASE_YEAR, 2030))


def forecast_rent(base_rent: float, annual_rate: float, year: int) -> float:
    """Compound an annual scenario from the current 2026 rent baseline."""
    if year not in FORECAST_YEARS:
        raise ValueError(f"Forecast year must be between {FORECAST_YEARS[0]} and {FORECAST_YEARS[-1]}.")
    return float(base_rent) * (1 + float(annual_rate) / 100) ** (year - BASE_YEAR)

