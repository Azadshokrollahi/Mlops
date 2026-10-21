import math
from flask import Flask, jsonify, request
from src.predict import predict_people

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.post("/predict")
def predict():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="JSON object required"), 400
    try:
        co2, pir = float(data["co2_ppm"]), float(data["pir_motion"])
        if not (math.isfinite(co2) and math.isfinite(pir) and
                400 <= co2 <= 5000 and 0 <= pir <= 10000):
            raise ValueError("Invalid sensor values")
    except (KeyError, ValueError, TypeError):
        return jsonify(error="Invalid co2_ppm or pir_motion"), 400
    return jsonify(predicted_people=predict_people(co2, pir))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
