# Bengaluru Rent Estimator

**Project on GitHub:** [Vin19842/bengaluru-rent-predictor](https://github.com/Vin19842/bengaluru-rent-predictor)  
**Live app:** _Add the Streamlit Community Cloud URL after deployment._

An educational project for exploring current neighborhood rent benchmarks and transparent future-year scenarios in Bengaluru. The current estimate is anchored to recent tenant-reported median rent by locality and BHK. A separate 2022 property-level model is retained for learning and comparison, but it is not used as today's estimate because its predictions were materially stale.

## Run on Windows

Open PowerShell in this folder:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

If `python` is not recognized, install Python from [python.org](https://www.python.org/downloads/windows/) and select **Add python.exe to PATH** during setup. Then reopen PowerShell.

## How the current estimate works

1. Select a locality and BHK with a recent market-index row.
2. The 2026 estimate starts from the area's reported median rent.
3. For 2027–2029, the app compounds the selected annual growth assumption: `current median × (1 + growth rate)^years`.
4. An optional agent-involved asking premium can be added as a user-controlled scenario. It defaults to 0%; it is not inferred from the data. One-time brokerage is normally separate from monthly rent.

Available growth assumptions include official September 2026 urban CPI actual rent inflation (2.22%), general urban CPI inflation (4.88%), a Bengaluru residential rent trend scenario (10.4% annualized from JLL's reported 2.5% Q2 2026 quarter-over-quarter rise), and a custom rate. These are scenario choices, not a fitted three-year forecast. Rent can move differently from CPI, and an annualized single quarter can overstate or understate future growth.

The current index has locality/BHK-level medians, not individual listings with size, bathrooms, furnishing, building age, or amenities. The app displays area as reference only and does not adjust the benchmark for it. This is more honest than pretending the aggregate table can train a property-specific model. Low report counts also make a locality median less stable.

## Why the old machine-learning estimate was wrong

The original Random Forest learned from 886 Bengaluru listings posted in April–July 2022. On the screenshot example it predicted ₹17,222, while the October 2026 Koramangala 2 BHK tenant-reported median was ₹25,000. Its random-holdout MAE was ₹7,528, but that evaluation did not test today's market. The model remains in `models/` as a historical educational artifact and is not used for current app results.

The recent index contains 31 aggregate rows, based on 2,220 tenant reports across neighborhoods. It is suitable for current area/BHK comparisons, but not for retraining the old property-level model. Do not manufacture synthetic property records and mix them into model training; that would create false accuracy. To build a stronger property model, collect permitted recent individual listing or signed-lease records with at least rent date, rent, BHK, floor area, locality, furnishing, bathrooms and listing/lease status. Evaluate with a time-based holdout and report locality-specific sample counts and errors.

## Data and sources

- Recent neighborhood medians: [Bengaluru Rent Index](https://bengaluru.rent/bengaluru-rent-index), October 2026 edition. It summarizes tenant-reported rents in the 90 days ending 6 October 2026 and permits reuse with attribution. Details and limits: [`data/README.md`](data/README.md).
- Inflation assumptions: [MoSPI/PIB CPI release for September 2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2322244&lang=1&reg=3). It reports 4.88% year-over-year urban general CPI inflation and 2.22% for actual urban rental payments.
- Bengaluru rent trend scenario: [JLL Bengaluru Residential Market Dynamics Q2 2026](https://www.jll.com/en-in/insights/market-dynamics/bengaluru-residential), which reports rents rose 2.5% quarter over quarter in Q2 2026.
- Historical training dataset: [Kaggle House Rent Prediction Dataset](https://www.kaggle.com/datasets/iamsouravbanerjee/house-rent-prediction-dataset), attributed to Sourav Banerjee. It is not included in Git because redistribution terms were not established. See `data/README.md` before downloading or reusing it.

## Deploy a shareable app

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
2. Choose **Create app**, this repository, the `main` branch and `app.py`.
3. Deploy, then copy the generated `streamlit.app` URL into the **Live app** line above. Future commits to `main` can update the deployed app automatically.

## Explaining it to a mentor

- **Current output:** observed neighborhood/BHK median from a recent tenant-report index.
- **Future output:** explicit compounding scenario with a selectable rate, not a machine-learning forecast.
- **Why no retraining:** new data is aggregated by locality and BHK, without property-level features or labels.
- **Next data milestone:** licensed, recent, property-level rent observations and a chronological evaluation split.

