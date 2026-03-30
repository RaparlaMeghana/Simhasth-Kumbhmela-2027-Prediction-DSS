from fastapi import FastAPI
from prediction import predict_environment
from config import init_gee
init_gee()


app = FastAPI()

@app.get("/predict")
def get_prediction():
    ndvi, ndwi = predict_environment()

    risk = "LOW"
    if ndwi < 0.15:
        risk = "HIGH"
    elif ndwi < 0.25:
        risk = "MODERATE"

    return {
        "ndvi": ndvi,
        "ndwi": ndwi,
        "risk_level": risk
    }
