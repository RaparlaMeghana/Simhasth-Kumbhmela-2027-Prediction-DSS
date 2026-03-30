import ee
from config import ROI

def get_latest_satellite():

    roi = ee.Geometry.Rectangle(ROI)

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR")
        .filterBounds(roi)
        .filterDate("2023-01-01", "2025-12-31")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .select(["B2","B3","B4","B8"])
    )

    # ALWAYS SAFE composite
    image = collection.first()

    ndvi = image.normalizedDifference(["B8","B4"]).rename("NDVI")
    ndwi = image.normalizedDifference(["B3","B8"]).rename("NDWI")

    return image.addBands([ndvi, ndwi])
