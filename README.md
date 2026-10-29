# Bengaluru Rent Estimator

**Project on GitHub:** [Vin19842/bengaluru-rent-predictor](https://github.com/Vin19842/bengaluru-rent-predictor)  
**Trained model:** [Download the model file](https://github.com/Vin19842/bengaluru-rent-predictor/blob/main/models/bengaluru_rent_model.joblib)  
**Live app:** _Not deployed yet — add the Streamlit Community Cloud URL here after deployment._

An end-to-end beginner project that estimates a Bengaluru home's rent from its size, BHK, bathrooms, locality and listing characteristics. It includes the 2022 property model and a separate October 2026 neighborhood benchmark. The original Kaggle CSV is kept out of Git because its source listing does not state a redistribution license; see [`data/README.md`](data/README.md) for provenance and retraining notes.

## What the project does

1. Loads the original six-city rental CSV and keeps only Bengaluru listings (labelled `Bangalore` in the source).
2. Removes unusable rows and prepares numeric and categorical fields.
3. Splits data into train and test sets before fitting preprocessing.
4. One-hot encodes categories, imputes missing values, and trains a Random Forest regressor on log-transformed rent.
5. Reports MAE, RMSE and R² on the held-out test set.
6. Serves a form where a user enters home details and receives an estimate in rupees.

## Run the included model on Windows

Open PowerShell in this folder and run:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

The app uses the included trained model and saved category choices; it does not need the original CSV. To train again, download the CSV as described in [`data/README.md`](data/README.md), save it as `data/raw/House_Rent_Dataset.csv`, then run `python src/train.py`.

## First training run

The model was trained on 886 Bengaluru listings (708 train, 178 test) using a fixed 80/20 split. It scored **₹7,528 MAE**, **₹17,657 RMSE**, and **0.6665 R²** on that holdout. These results describe this historical sample; they do not guarantee accuracy on today's market. Re-run `python src\train.py` to reproduce the evaluation and model after downloading the CSV.

## Why the app shows two numbers

The property model predicts **₹17,222** for the 2 BHK, 1,000 sq ft Koramangala example because it learned from 2022 listings; the full Bengaluru test-set RMSE is about ₹17,657. The October 2026 index gives a **₹25,000** median paid rent for a Koramangala 2 BHK, based on 22 tenant reports in the latest 90-day window. The app shows both separately: the old model is property-feature-based, while the recent figure is a neighborhood/BHK median that ignores size, bathrooms and furnishing.

The 2026 CSV contains 31 neighborhood/BHK aggregates, not individual property records. It is valuable for a fresh market reference but too small and too coarse to retrain the property model. A proper retrain needs recent individual rental records with rent date, BHK, area, locality, bathrooms, furnishing and rent, along with permission to reuse the data. For now, the app surfaces the current benchmark and clearly labels the 2022 model's age and uncertainty.

## Project layout

```text
app.py                         Interactive prediction form
src/train.py                   Cleaning, training and evaluation
data/README.md                 Data source and download notes
models/                        Saved model and holdout metrics
```

## How to explain it to your mentor

- **Problem:** Estimate monthly residential rent in Bengaluru from listing details.
- **ML task:** Supervised regression; the target is `Rent` in Indian rupees.
- **Inputs:** BHK, size, bathroom count, area type, locality, furnishing and tenant preference.
- **Model:** Random Forest. Rent has a long right tail, so training uses `log1p` and predictions are converted back to rupees.
- **Evaluation:** A reproducible 80/20 random holdout. MAE is the typical absolute error in rupees; RMSE penalizes large mistakes; R² measures how much variation is explained.
- **Preprocessing:** Numeric medians and categorical most-frequent values are learned from training data within a pipeline. Unknown categories are tolerated at prediction time.
- **Limitations:** The dataset is small for Bengaluru, historical (April–July 2022), based on advertised listings, and does not cover amenities, deposit, building age, exact coordinates, or current market changes. The random holdout score should not be presented as a guarantee of future accuracy.

## Data and attribution

The dataset is the House Rent Prediction Dataset attributed to Sourav Banerjee on Kaggle, with a public GitHub mirror used for this project. See [`data/README.md`](data/README.md) for provenance and terms notes. Check the original Kaggle terms before redistributing or using commercially.

## Publish the live app

1. Push this project to a GitHub repository. Keep it public if you want anyone with the link to open the app.
2. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub and choose **Create app**.
3. Select your repository, the `main` branch, and `app.py` as the app file, then deploy.
4. Copy the URL Streamlit gives you into this README so your mentor can open the live app directly.

The deployed app uses the saved model; it does not need the raw CSV. Streamlit assigns a shareable `streamlit.app` URL after deployment. See the [official deploy guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

## Before presenting

Run the app once and try a few combinations. Be ready to explain why the current neighborhood benchmark is shown separately from the property-level prediction, why data is split before fitting preprocessing, and what MAE means in rupees.

