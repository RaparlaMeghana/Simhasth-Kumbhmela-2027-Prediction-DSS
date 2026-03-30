import ee
import pandas as pd
from config import ROI, init_gee

init_gee()

roi = ee.Geometry.Rectangle(ROI)

def get_yearly_stats(year):

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR")
        .filterBounds(roi)
        .filterDate(f"{year}-01-01", f"{year}-12-31")
        .select(["B2","B3","B4","B8"])
    )

    img = collection.median().clip(roi)

    ndvi = img.normalizedDifference(["B8","B4"]).rename("NDVI")
    ndwi = img.normalizedDifference(["B3","B8"]).rename("NDWI")

    stats = ndvi.addBands(ndwi).reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=roi,
        scale=60,
        bestEffort=True
    ).getInfo()

    return stats["NDVI"], stats["NDWI"]


def fetch_historical_data():

    years = list(range(2016, 2026))
    ndvi_vals = []
    ndwi_vals = []

    for y in years:
        n1, n2 = get_yearly_stats(y)
        ndvi_vals.append(n1)
        ndwi_vals.append(n2)

    return pd.DataFrame({
        "year": years,
        "ndvi": ndvi_vals,
        "ndwi": ndwi_vals
    })
