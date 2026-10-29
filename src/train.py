"""Train and evaluate a Bengaluru-only monthly rent regression model."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "House_Rent_Dataset.csv"
MODEL_PATH = ROOT / "models" / "bengaluru_rent_model.joblib"
METRICS_PATH = ROOT / "models" / "metrics.json"

NUMERIC = ["BHK", "Size", "Bathroom"]
CATEGORICAL = ["Area Type", "Area Locality", "Furnishing Status", "Tenant Preferred"]
FEATURES = NUMERIC + CATEGORICAL
TARGET = "Rent"


def load_bengaluru_data(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = set(FEATURES + [TARGET, "City"])
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing columns: {sorted(missing)}")
    df = df.loc[df["City"].astype(str).str.strip().str.casefold().isin({"bangalore", "bengaluru"})].copy()
    for col in NUMERIC + [TARGET]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=[TARGET])
    df = df.loc[(df[TARGET] > 0) & (df["Size"] > 0) & (df["BHK"] > 0)]
    df["Area Locality"] = df["Area Locality"].fillna("Unknown").astype(str).str.strip()
    return df


def build_model() -> TransformedTargetRegressor:
    numeric_pipe = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    categorical_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore", min_frequency=3)),
    ])
    preprocess = ColumnTransformer([
        ("numeric", numeric_pipe, NUMERIC),
        ("categorical", categorical_pipe, CATEGORICAL),
    ])
    rent_model = Pipeline([
        ("preprocess", preprocess),
        ("regressor", RandomForestRegressor(
            n_estimators=400, min_samples_leaf=2, max_features=0.85,
            random_state=42, n_jobs=-1,
        )),
    ])
    # Rent is strongly right-skewed. Learn in log space and return rupees at inference.
    return TransformedTargetRegressor(regressor=rent_model, func=np.log1p, inverse_func=np.expm1)


def main() -> None:
    df = load_bengaluru_data()
    X, y = df[FEATURES], df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = build_model()
    model.fit(X_train, y_train)
    predictions = np.maximum(0, model.predict(X_test))
    metrics = {
        "city": "Bengaluru (source labels this city Bangalore)",
        "dataset_rows_after_cleaning": int(len(df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "test_mae_inr": round(float(mean_absolute_error(y_test, predictions)), 2),
        "test_rmse_inr": round(float(np.sqrt(mean_squared_error(y_test, predictions))), 2),
        "test_r2": round(float(r2_score(y_test, predictions)), 4),
        "split": "80/20 random holdout, random_state=42",
        "model": "RandomForestRegressor (400 trees; log1p target)",
        "features": FEATURES,
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    options = {
        "localities": sorted(df["Area Locality"].dropna().astype(str).unique().tolist()),
        "area_types": sorted(df["Area Type"].dropna().astype(str).unique().tolist()),
        "tenant_preferences": sorted(df["Tenant Preferred"].dropna().astype(str).unique().tolist()),
    }
    joblib.dump({"model": model, "features": FEATURES, "numeric": NUMERIC,
                 "categorical": CATEGORICAL, "options": options}, MODEL_PATH, compress=3)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

