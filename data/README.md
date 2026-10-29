# Data sources and limitations

## Current neighborhood benchmark

`market/bengaluru-rent-index-2026-10.csv` is the October 2026 edition of the [Bengaluru Rent Index](https://bengaluru.rent/bengaluru-rent-index). It summarizes tenant-reported rents from the 90 days ending 6 October 2026 and permits reuse with attribution. Its source reports 2,220 tenant reports; this CSV contains 31 locality/BHK summary rows with median rent and report counts, not individual properties.

For example, the Koramangala 2 BHK row has a ₹25,000 median from 22 tenant reports. It is the app's current baseline for that neighborhood/BHK. It is not adjusted for square footage, bathrooms, furnishing, amenities or building condition. Reported paid rents may differ from current asking prices and from a specific lease negotiation.

## Future-year assumptions

The app applies a selected annual rate to the current median, compounded for the number of years:

`projected rent = current median × (1 + annual rate)^years × (1 + optional agent premium)`

Rate presets are sourced as follows:

- 2.22%: September 2026 year-over-year inflation for actual rental payments in India's urban CPI basket, from the [official CPI release](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2322244&lang=1&reg=3). This is not Bangalore-specific.
- 4.88%: September 2026 year-over-year urban CPI general inflation, from the same release. General inflation is not rent inflation.
- 10.4%: annualized compound equivalent of JLL's reported 2.5% quarter-over-quarter Bengaluru residential rent increase in Q2 2026, from [JLL](https://www.jll.com/en-in/insights/market-dynamics/bengaluru-residential). This annualizes one quarter and is presented only as a high-growth scenario, not an established long-run forecast.
- Custom: user-entered assumption.

The optional agent-involved asking premium is also a user-selected scenario, defaults to 0%, and is not measured in the data. Brokerage is typically a one-time cost and should not be interpreted as recurring rent.

These scenarios do not create a training dataset and should not be described as guaranteed forecasts. Historical/current aggregate medians cannot establish an individual property's future rent.

## Historical property-level training data

`raw/House_Rent_Dataset.csv` is the House Rent Prediction Dataset attributed on Kaggle to Sourav Banerjee and commonly described as scraped from MagicBricks. It contains 4,746 listings from six Indian cities, posted April–July 2022. The source labels Bengaluru as `Bangalore`; `src/train.py` filters to those rows.

The CSV was downloaded from a public GitHub mirror. That mirror does not establish redistribution rights, so the CSV is excluded from Git. Before redistributing or using commercially, obtain it from its [original Kaggle page](https://www.kaggle.com/datasets/iamsouravbanerjee/house-rent-prediction-dataset) and check the current terms.

The historic listings can support a learning exercise, but they are too old and sparse to estimate current prices reliably. The saved model remains in `models/` for educational comparison; the current app does not use it for today's estimate.

## What would support a better property-level model?

Acquire a recent, permission-cleared set of individual listings or signed leases with rent date, rent, BHK, floor area, locality, furnishing, bathrooms and listing/lease status. Deduplicate reposts, distinguish asking rent from agreed rent, retain source and collection date, and evaluate using a time-based holdout. Do not fabricate synthetic properties or train on neighborhood summary rows as though they were individual homes.

