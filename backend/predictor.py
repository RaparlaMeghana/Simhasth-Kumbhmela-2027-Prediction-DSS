import numpy as np
from sklearn.ensemble import RandomForestRegressor
from database import fetch_data
from config import PREDICTION_YEAR
from config import init_gee
init_gee()


def predict_environment():

    data = fetch_data()

    years = np.array([d[0] for d in data]).reshape(-1,1)
    ndvi = np.array([d[1] for d in data])
    ndwi = np.array([d[2] for d in data])

    model1 = RandomForestRegressor().fit(years, ndvi)
    model2 = RandomForestRegressor().fit(years, ndwi)

    pred_ndvi = model1.predict([[PREDICTION_YEAR]])[0]
    pred_ndwi = model2.predict([[PREDICTION_YEAR]])[0]

    return pred_ndvi, pred_ndwi
