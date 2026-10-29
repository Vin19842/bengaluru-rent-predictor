# Bengaluru Rent Estimator

**Project on GitHub:** [Vin19842/bengaluru-rent-predictor](https://github.com/Vin19842/bengaluru-rent-predictor)  
**Live app:** _Add the Streamlit Community Cloud URL after deployment._

An educational Streamlit dashboard for exploring Bengaluru rents. One filter-driven view combines the rent estimate and market overview: locality/BHK KPIs, selectable charts, size-matched Koramangala listing examples, and 2026–2029 scenarios. Tenant-reported paid rents remain separate from asking prices. The old 2022 model is retained for learning but is not used for current estimates.

## Run on Windows

Open PowerShell in this folder:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

If `python` is not recognized, install Python from [python.org](https://www.python.org/downloads/windows/) and select **Add python.exe to PATH** during setup. Then reopen PowerShell.

Run the calculation and filter checks with:

```powershell
python -m unittest discover -s tests -v
```

## Dashboard and estimate logic

The single dashboard view updates its KPI cards and charts together when locality and BHK change. Forecast charts and the projected-rent KPI also respond to the selected year and growth assumption; 2029 is three compounded years from the 2026 baseline. Switch among forecast-by-locality, a 2026–2029 forecast chart, current rent bars, selected-locality period bars or a line chart, rent-change bars, and report-volume bars. For Koramangala 2 BHK, it also checks manually captured portal examples against size, area-measurement type and tolerance. It requires at least five comparable listings before showing a middle-half asking range; smaller samples are shown as individual evidence and are not called a reliable prediction.

Future scenarios compound a selected annual rate through 2029. Options include September 2026 urban actual-rent inflation (2.22%), general urban CPI inflation (4.88%), a Bengaluru residential rent trend scenario (10.4% annualized from JLL's Q2 2026 quarter-over-quarter report), and a custom assumption. There is no agent markup. These are scenarios, not fitted forecasts.

Paid-rent reports, asking posts and portal asking prices have different populations. The app keeps them separate and displays sample sizes, dates and source links. A user's square footage only affects the small Koramangala listing comparison; the area/BHK paid-rent median is not adjusted by size.

## Why the old machine-learning estimate was wrong

The original Random Forest learned from 886 Bengaluru listings posted in April–July 2022. On the screenshot example it predicted ₹17,222, while the October 2026 Koramangala 2 BHK tenant-reported median was ₹25,000. Its random-holdout MAE was ₹7,528, but that evaluation did not test today's market. The model remains in `models/` as a historical educational artifact and is not used for current app results.

The current paid-rent index contains 31 locality/BHK aggregates from 2,220 renter reports. The manual portal snapshot has only 17 visible Koramangala 2 BHK examples. Neither is sufficient to retrain a multi-locality property model. Do not mix synthetic values or area-level medians into property-level training. A credible model needs many more recent, unique, permission-cleared listings or leases, plus a time-based evaluation set.

## Data and sources

- Recent neighborhood medians: [Bengaluru Rent Index](https://bengaluru.rent/bengaluru-rent-index), October 2026 edition. It summarizes tenant-reported rents in the 90 days ending 6 October 2026 and permits reuse with attribution. Details and limits: [`data/README.md`](data/README.md).
- Koramangala asking price examples and source summaries: see `data/market/koramangala-asking-listings-2026-10.csv` and `data/market/koramangala-source-snapshots-2026-10.csv`. They are dated research snapshots, not verified lease outcomes or a production crawler feed.
- Additional current local references: [MyBharat Rent](https://mybharat.rent/rent-in/bengaluru/koramangala/2-bhk-for-rent), [Ghar4 Rent](https://www.ghar4.rent/areas/koramangala-bengaluru/2-bhk), and [Magicbricks listings](https://www.magicbricks.com/2-bhk-flats-for-rent-in-koramangala-bangalore-pppfr).
- Inflation assumptions: [MoSPI/PIB CPI release for September 2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2322244&lang=1&reg=3). It reports 4.88% year-over-year urban general CPI inflation and 2.22% for actual urban rental payments.
- Bengaluru rent trend scenario: [JLL Bengaluru Residential Market Dynamics Q2 2026](https://www.jll.com/en-in/insights/market-dynamics/bengaluru-residential), which reports rents rose 2.5% quarter over quarter in Q2 2026.
- Historical training dataset: [Kaggle House Rent Prediction Dataset](https://www.kaggle.com/datasets/iamsouravbanerjee/house-rent-prediction-dataset), attributed to Sourav Banerjee. It is not included in Git because redistribution terms were not established. See `data/README.md` before downloading or reusing it.

## Deploy a shareable app

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
2. Choose **Create app**, this repository, the `main` branch and `app.py`.
3. Deploy, then copy the generated `streamlit.app` URL into the **Live app** line above. Future commits to `main` can update the deployed app automatically.

## Explaining it to a mentor

- **Current output:** separate paid-rent benchmarks, asking-source ranges and (for one locality/configuration) a small comparable-listing sample.
- **Future output:** explicit compounding scenario with a selectable rate, not a machine-learning forecast.
- **Why no retraining:** the current observations are too small, too narrow and partly aggregated to support a reliable property-level model.
- **Next data milestone:** licensed, recent, property-level rent observations and a chronological evaluation split.

