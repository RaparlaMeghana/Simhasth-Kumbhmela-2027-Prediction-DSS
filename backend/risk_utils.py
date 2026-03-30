# risk_utils.py

def compute_environmental_risk(ndvi: float, ndwi: float, crowd_factor: float | None = None) -> float:
    # Softer NDVI thresholds:
    # 0 risk when NDVI >= 0.55, 1 risk when NDVI <= 0.25
    ndvi_risk = (0.55 - ndvi) / (0.55 - 0.25)
    ndvi_risk = max(0.0, min(1.0, ndvi_risk))

    # Softer NDWI thresholds:
    # 0 risk when NDWI >= 0.35, 1 risk when NDWI <= 0.05
    ndwi_risk = (0.35 - ndwi) / (0.35 - 0.05)
    ndwi_risk = max(0.0, min(1.0, ndwi_risk))

    if crowd_factor is None:
        combined = 0.5 * ndvi_risk + 0.5 * ndwi_risk
    else:
        crowd_risk = max(0.0, min(1.0, crowd_factor))
        combined = 0.4 * ndvi_risk + 0.4 * ndwi_risk + 0.2 * crowd_risk

    return round(combined * 100, 1)
