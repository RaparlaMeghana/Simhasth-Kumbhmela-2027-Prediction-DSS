import numpy as np

# =============================
# 📍 KUND GEOMETRY (MAX CROWD MODEL)
# =============================

RAMKUND = {
    "name": "Ramkund",
    "lat": 19.9975,
    "lon": 73.7902,
    "area_m2": 18000
}

KUSHAVARTA = {
    "name": "Kushavarta",
    "lat": 19.8876,
    "lon": 73.7167,
    "area_m2": 6000
}

PEAK_DENSITY = 4  # persons per m2 (Shahi Snan condition)

MAX_REFERENCE_CAPACITY = 72000  # Ramkund max peak


# =============================
# 👥 MAX CROWD ESTIMATION
# =============================

def estimate_max_crowd(kund):
    crowd = kund["area_m2"] * PEAK_DENSITY
    return int(crowd)


# =============================
# 🌿 ENVIRONMENTAL SCORE (0–1)
# =============================

def calculate_environment_score(ndvi, ndwi):
    # Normalize NDVI and NDWI into 0–1 “goodness”
    ndvi_norm = (ndvi - 0.30) / (0.65 - 0.30)
    ndwi_norm = (ndwi - 0.05) / (0.45 - 0.05)

    ndvi_norm = np.clip(ndvi_norm, 0, 1)
    ndwi_norm = np.clip(ndwi_norm, 0, 1)

    env_score = (ndvi_norm * 0.5) + (ndwi_norm * 0.5)
    return float(np.clip(env_score, 0, 1))



# =============================
# 🏞️ MAIN ANALYSIS
# =============================
def analyze_kund(kund, ndvi, ndwi):
    crowd = estimate_max_crowd(kund)

    # Normalize crowd risk against worst-case Ramkund
    crowd_risk = crowd / MAX_REFERENCE_CAPACITY

    env_score = calculate_environment_score(ndvi, ndwi)

    # Human pressure factor
    crowd_factor = 1 - (crowd_risk * 0.6)

    # Bathing Suitability Index
    bsi = env_score * crowd_factor
    bsi = np.clip(bsi, 0.05, 1)

    return {
        "crowd": crowd,
        "environmental_risk_score": round(env_score, 3),  # 0–1 env quality
        "crowd_risk": round(crowd_risk, 3),
        "bathing_suitability_index": round(float(bsi), 3),
    }



# =============================
# 🔮 2027 PEAK PREDICTION
# =============================

def predict_2027():

    # Observed degradation trend (2016–2025)
    ndvi_decline = -0.015
    ndwi_decline = -0.02

    current_ndvi = 0.42
    current_ndwi = 0.28

    future_ndvi = current_ndvi + ndvi_decline
    future_ndwi = current_ndwi + ndwi_decline

    future_env = calculate_environment_score(
        future_ndvi,
        future_ndwi
    )

    return round(future_ndvi, 3), round(future_ndwi, 3), round(future_env, 3)