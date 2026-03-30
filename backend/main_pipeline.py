# Main satellite processing pipeline placeholder
import ee
import geemap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from config import init_gee
init_gee()
# Initialize Earth Engine
ee.Initialize()

# -----------------------------
# 1. DEFINE NASHIK ROI
# -----------------------------
roi = ee.Geometry.Rectangle([73.60, 19.85, 73.90, 20.05])

print("ROI Loaded Successfully")

# -----------------------------
# 2. LOAD SENTINEL DATA
# -----------------------------
def get_satellite_data(start, end):

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR")
        .filterBounds(roi)
        .filterDate(start, end)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        .median()
        .clip(roi)
    )

    return collection

image = get_satellite_data('2023-01-01', '2023-12-31')

print("Satellite Data Loaded")

# -----------------------------
# 3. CALCULATE INDICES
# -----------------------------
def calculate_indices(img):

    ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')
    ndwi = img.normalizedDifference(['B3', 'B8']).rename('NDWI')
    ndbi = img.normalizedDifference(['B11', 'B8']).rename('NDBI')

    return img.addBands([ndvi, ndwi, ndbi])

image = calculate_indices(image)

print("Indices Calculated")

# -----------------------------
# 4. EXTRACT MEAN VALUES
# -----------------------------
stats = image.reduceRegion(
    reducer=ee.Reducer.mean(),
    geometry=roi,
    scale=30,
    maxPixels=1e13
)

stats_dict = stats.getInfo()

print("Extracted Stats:", stats_dict)

# -----------------------------
# 5. VISUALIZE MAP
# -----------------------------
Map = geemap.Map(center=[19.95, 73.75], zoom=11)

Map.addLayer(image.select('NDVI'),
             {'min': 0, 'max': 1, 'palette': ['brown', 'green']},
             'Vegetation')

Map.addLayer(image.select('NDWI'),
             {'min': -1, 'max': 1, 'palette': ['white', 'blue']},
             'Water')

Map.addLayer(image.select('NDBI'),
             {'min': -1, 'max': 1, 'palette': ['green', 'red']},
             'Built-up')

Map
