"""Reload the persisted pipeline and predict on a raw, unpreprocessed row."""

from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).parent / "models" / "best_pipeline.joblib"

pipeline = joblib.load(MODEL_PATH)

# A raw, single-row DataFrame -- exactly the shape of unprocessed input the
# pipeline would receive in production. No encoding, no scaling, no imputation
# done by hand here; the pipeline does all of that internally.
raw_row = pd.DataFrame([{
    "pclass": 1,
    "sex": "female",
    "age": 29.0,
    "sibsp": 0,
    "parch": 0,
    "fare": 100.0,
    "embarked": "S",
}])

prediction = pipeline.predict(raw_row)
probability = pipeline.predict_proba(raw_row)

print("Raw input:")
print(raw_row)
print(f"\nPrediction (0=did not survive, 1=survived): {prediction[0]}")
print(f"Predicted probabilities [P(0), P(1)]: {probability[0]}")
