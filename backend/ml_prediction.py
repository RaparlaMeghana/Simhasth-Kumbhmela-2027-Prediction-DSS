from sklearn.ensemble import RandomForestRegressor
import numpy as np

def predict_future(years, ndvi, ndwi):

    X = np.array(years).reshape(-1, 1)

    model_ndvi = RandomForestRegressor(n_estimators=200)
    model_ndwi = RandomForestRegressor(n_estimators=200)

    model_ndvi.fit(X, ndvi)
    model_ndwi.fit(X, ndwi)

    future_year = np.array([[2027]])

    pred_ndvi = model_ndvi.predict(future_year)[0]
    pred_ndwi = model_ndwi.predict(future_year)[0]

    return pred_ndvi, pred_ndwi
