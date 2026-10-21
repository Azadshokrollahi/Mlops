import pandas as pd
from app import app

def test_ten_rows():
    assert len(pd.read_csv("data/raw/people_count.csv")) == 10

def test_columns():
    assert list(pd.read_csv("data/raw/people_count.csv").columns) == [
        "co2_ppm", "pir_motion", "people_count"
    ]

def test_nonnegative():
    assert (pd.read_csv("data/raw/people_count.csv")["people_count"] >= 0).all()

def test_health():
    r = app.test_client().get("/health")
    assert r.status_code == 200 and r.json == {"status": "ok"}

def test_bad_request():
    assert app.test_client().post("/predict", json={"co2_ppm": "bad"}).status_code == 400
