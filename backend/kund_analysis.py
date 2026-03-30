import ee

# =========================================================
# Initialize Earth Engine
# =========================================================
try:
    ee.Initialize()
except:
    ee.Authenticate()
    ee.Initialize()


# =========================================================
# 1️⃣ ULTRA-SPECIFIC KUND POLYGONS (TIGHT BOUNDARY)
# =========================================================

# Ramkund – Panchavati, Nashik
RAMKUND = ee.Geometry.Polygon([
    [
        [73.79195, 20.00625],
        [73.79230, 20.00625],
        [73.79230, 20.00580],
        [73.79195, 20.00580]
    ]
])

# Kushavarta Kund – Trimbakeshwar
KUSHAVARTA = ee.Geometry.Polygon([
    [
        [73.53060, 19.93235],
        [73.53105, 19.93235],
        [73.53105, 19.93195],
        [73.53060, 19.93195]
    ]
])

ROI = RAMKUND.union(KUSHAVARTA)


# =========================================================
# 2️⃣ CLOUD MASK FUNCTION
# =========================================================

def mask_s2_clouds(image):
    qa = image.select('QA60')

    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11

    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
           qa.bitwiseAnd(cirrus_bit_mask).eq(0))

    return image.updateMask(mask).divide(10000)


# =========================================================
# 3️⃣ GET STABLE MNDWI IMAGE
# =========================================================

def get_stable_mndwi():

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(ROI)
        .filterDate("2024-01-01", "2024-12-31")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
        .map(mask_s2_clouds)
    )

    median_img = collection.median().clip(ROI)

    # MNDWI = (Green - SWIR) / (Green + SWIR)
    mndwi = median_img.normalizedDifference(['B3', 'B11']).rename('MNDWI')

    return mndwi


# =========================================================
# 4️⃣ COMPUTE CLEAN WATER MASK
# =========================================================

def compute_water_mask(mndwi, geometry):

    stats = mndwi.reduceRegion(
        reducer=ee.Reducer.mean().combine(
            reducer2=ee.Reducer.stdDev(),
            sharedInputs=True
        ),
        geometry=geometry,
        scale=10,
        maxPixels=1e9
    )

    mean = ee.Number(stats.get('MNDWI_mean'))
    std = ee.Number(stats.get('MNDWI_stdDev'))

    threshold = mean.add(std)

    water_mask = mndwi.gt(threshold)

    # Morphological cleaning
    clean_mask = (
        water_mask
        .focal_min(1)
        .focal_max(2)
        .selfMask()
    )

    return clean_mask


# =========================================================
# 5️⃣ CALCULATE AREA (HECTARES)
# =========================================================

def calculate_area(water_mask, geometry):

    area = water_mask.multiply(ee.Image.pixelArea()).reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=10,
        maxPixels=1e13
    )

    area_sqm = ee.Number(area.get('MNDWI'))

    return area_sqm.divide(10000)


# =========================================================
# 6️⃣ FLOOD BUFFER ANALYSIS
# =========================================================

def generate_flood_risk_zone(water_mask, geometry, buffer_pixels=5):

    flood_buffer = water_mask.focal_max(buffer_pixels)

    flood_area = flood_buffer.multiply(ee.Image.pixelArea()).reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=10,
        maxPixels=1e13
    )

    flood_sqm = ee.Number(flood_area.get('MNDWI'))

    return flood_sqm.divide(10000)


# =========================================================
# 7️⃣ SAFE CROWD CAPACITY
# =========================================================

def estimate_safe_crowd_capacity(area_hectares):

    area_sqm = area_hectares * 10000

    # 2 sq.m per person safety standard
    capacity = area_sqm / 2

    return int(capacity)


# =========================================================
# 8️⃣ MASTER ANALYSIS FUNCTION
# =========================================================

def analyze_kund(geometry):

    mndwi = get_stable_mndwi()

    water_mask = compute_water_mask(mndwi, geometry)

    water_area = calculate_area(water_mask, geometry)
    flood_area = generate_flood_risk_zone(water_mask, geometry)

    water_val = water_area.getInfo()
    flood_val = flood_area.getInfo()

    safe_capacity = estimate_safe_crowd_capacity(water_val)

    return {
        "water_area_hectares": round(water_val, 6),
        "flood_risk_hectares": round(flood_val, 6),
        "safe_crowd_capacity": safe_capacity
    }


# =========================================================
# 9️⃣ STREAMLIT FUNCTION
# =========================================================

def get_kund_stats():

    ram_stats = analyze_kund(RAMKUND)
    kush_stats = analyze_kund(KUSHAVARTA)

    return {
        "Ramkund": ram_stats,
        "Kushavarta": kush_stats
    }


# =========================================================
# TEST RUN
# =========================================================

if __name__ == "__main__":

    results = get_kund_stats()

    print("\n🏞 Ultra-Accurate Kund Planning Analysis")
    print("----------------------------------------")
    print("Ramkund:", results["Ramkund"])
    print("Kushavarta:", results["Kushavarta"])