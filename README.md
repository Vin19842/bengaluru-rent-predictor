# Bengaluru Rent Estimator

**Live app:** _Not deployed yet — add the Streamlit Community Cloud URL here after deployment._

An end-to-end beginner project that predicts a Bengaluru home's monthly advertised rent from its size, BHK, bathrooms, locality and listing characteristics. It includes a repeatable training script, a saved trained model, evaluation metrics and an interactive Streamlit app. The original CSV is kept out of Git because its source listing does not state a redistribution license; see [`data/README.md`](data/README.md) for how to obtain it for retraining.

## What the project does

1. Loads the original six-city rental CSV and keeps only Bengaluru listings (labelled `Bangalore` in the source).
2. Removes unusable rows and prepares numeric and categorical fields.
3. Splits data into train and test sets before fitting preprocessing.
4. One-hot encodes categories, imputes missing values, and trains a Random Forest regressor on log-transformed rent.
5. Reports MAE, RMSE and R² on the held-out test set.
6. Serves a form where a user enters home details and receives an estimate in rupees.

## Run it on Windows

Open PowerShell in this folder and run:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src\train.py
streamlit run app.py
```

The included trained model and saved category choices let the app run without the original CSV. To retrain, first download the CSV as described in [`data/README.md`](data/README.md). After training, see `models/metrics.json` for the evaluation and `models/bengaluru_rent_model.joblib` for the trained pipeline.

## First training run

Using the included data and the fixed 80/20 split, the training script kept 886 Bengaluru listings (708 train, 178 test). The saved run scored **₹7,528 MAE**, **₹17,657 RMSE**, and **0.6665 R²** on that holdout. These are reproducibility results for this historical sample; they do not guarantee accuracy on today's market. Re-run `python src\train.py` to reproduce the evaluation and model with the pinned scikit-learn version.

## Project layout

```text
app.py                         Interactive prediction form
src/train.py                   Cleaning, training and evaluation
data/raw/House_Rent_Dataset.csv Source listings
data/README.md                 Provenance and use limitations
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

Run the app once and try a few combinations. Be ready to explain why data is split before fitting preprocessing, what MAE means in rupees, and why the estimate is only a prototype due to the dataset's age and size.

