from pathlib import Path
import pandas as pd
import yaml
import joblib
from sklearn.ensemble import RandomForestRegressor

def main():
    df = pd.read_csv("data/processed/train.csv")
    with open("params.yaml", encoding="utf-8") as f:
        p = yaml.safe_load(f)["model"]
    model = RandomForestRegressor(n_estimators=p["n_estimators"], random_state=p["random_state"])
    model.fit(df[["co2_ppm", "pir_motion"]], df["people_count"])
    Path("models").mkdir(exist_ok=True)
    joblib.dump(model, "models/model.joblib")
    print("Saved models/model.joblib")

if __name__ == "__main__":
    main()
