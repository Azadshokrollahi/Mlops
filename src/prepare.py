from pathlib import Path
import pandas as pd

def main():
    df = pd.read_csv("data/raw/people_count.csv")
    assert list(df.columns) == ["co2_ppm", "pir_motion", "people_count"]
    assert len(df) == 10 and not df.isna().any().any()
    assert (df >= 0).all().all()
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df.iloc[:8].to_csv("data/processed/train.csv", index=False)
    df.iloc[8:].to_csv("data/processed/test.csv", index=False)
    print("Created train.csv (8 rows) and test.csv (2 rows)")

if __name__ == "__main__":
    main()
