from functools import lru_cache
import pandas as pd
import joblib

@lru_cache(maxsize=1)
def get_model():
    return joblib.load("models/model.joblib")

def predict_people(co2_ppm, pir_motion):
    x = pd.DataFrame([{"co2_ppm": co2_ppm, "pir_motion": pir_motion}])
    return max(0, round(float(get_model().predict(x)[0])))

if __name__ == "__main__":
    print("Predicted people:", predict_people(760, 8))
