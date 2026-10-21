import json
import os
from pathlib import Path

import pandas as pd
import joblib
import yaml
import mlflow

from sklearn.metrics import mean_absolute_error, mean_squared_error


def main():
    # 1. Load testing data
    df = pd.read_csv("data/processed/test.csv")

    # 2. Load the trained model
    model = joblib.load("models/model.joblib")

    # 3. Make predictions
    pred = model.predict(df[["co2_ppm", "pir_motion"]])
    actual = df["people_count"]

    # 4. Calculate evaluation metrics
    metrics = {
        "mae": float(mean_absolute_error(actual, pred)),
        "rmse": float(mean_squared_error(actual, pred) ** 0.5),
    }

    # 5. Save metrics to JSON
    Path("metrics").mkdir(exist_ok=True)

    Path("metrics/metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n"
    )

    # 6. Load model hyperparameters
    with open("params.yaml", encoding="utf-8") as f:
        params = yaml.safe_load(f)["model"]

    # 7. Configure MLflow with SQLite
    if not os.environ.get("MLFLOW_TRACKING_URI"):
        mlflow.set_tracking_uri("sqlite:///mlflow.db")

    # 8. Create or select MLflow experiment
    mlflow.set_experiment("people-counting-10-rows")

    # 9. Log experiment results
    with mlflow.start_run():
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        mlflow.log_artifact("metrics/metrics.json")
        mlflow.log_artifact("models/model.joblib")

    # 10. Display results
    print("Actual:", actual.tolist())
    print("Predicted:", pred.tolist())
    print("Metrics:", metrics)


if __name__ == "__main__":
    main()