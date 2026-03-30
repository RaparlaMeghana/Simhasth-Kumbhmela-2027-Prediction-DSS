import streamlit as st
import ee
import geemap.foliumap as geemap
import pandas as pd
import datetime
import plotly.express as px

from ml_prediction import predict_future
from risk_utils import compute_environmental_risk

# --------------------------------------------------
# SAFE EARTH ENGINE INITIALIZATION
# --------------------------------------------------
if "ee_initialized" not in st.session_state:
    try:
        ee.Initialize()
    except:
        ee.Authenticate()
        ee.Initialize()
    st.session_state.ee_initialized = True

st.set_page_config(
    layout="wide",
    page_title="NRSC – Simhasth 2027 Environmental DSS",
)

# ---------------- MODERN DARK / GLASS UI ----------------
DARK_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background: radial-gradient(circle at top, #020617 0, #020617 40%, #02010f 100%);
    color: #e5e7eb;
}

/* Main container */
.block-container {
    padding-top: 0.8rem;
    padding-bottom: 1rem;
    max-width: 1200px;
}

/* Headings */
h1, h2, h3, h4 {
    color: #fefce8 !important;
    letter-spacing: 0.03em;
}

/* Glass cards (metrics & alerts) */
div.stMetric, .stAlert {
    background: radial-gradient(circle at top left, rgba(56,189,248,0.22), rgba(15,23,42,0.96));
    border-radius: 18px;
    border: 1px solid rgba(129,140,248,0.7);
    box-shadow: 0 18px 45px rgba(15,23,42,0.75);
    backdrop-filter: blur(18px);
}

/* Metric labels and values */
[data-testid="stMetricLabel"] {
    color: #e5e7eb;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.09em;
}
[data-testid="stMetricValue"] {
    color: #f97316;
    font-weight: 700;
    font-size: 1.35rem;
}

/* Alerts text colors */
.stAlert p {
    color: #fefce8;
}

/* Section headers underline */
h2, h3 {
    border-bottom: 1px solid rgba(55,65,81,0.9);
    padding-bottom: 0.25rem;
    margin-bottom: 0.6rem;
}

/* Buttons / links */
a, .stButton > button {
    border-radius: 999px;
    font-size: 0.9rem;
    transition: all 0.18s ease-out;
    color: #e0f2fe !important;
}
a:hover, .stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 30px rgba(56,189,248,0.55);
}

/* Map iframe border */
iframe {
    border-radius: 20px !important;
    border: 1px solid rgba(148,163,184,0.45);
}

/* Captions */
.small-caption, .stCaption {
    color: #e5e7eb;
    font-size: 0.8rem;
    opacity: 0.95;
}

/* Horizontal rule styling */
hr {
    border-color: rgba(55,65,81,0.8);
}
</style>
"""
st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("NRSC – Simhasth 2027 Environmental DSS")

# --------------------------------------------------
# CORRECT KUND LOCATIONS
# --------------------------------------------------

# Nashik Ramkund
RAMKUND = ee.Geometry.Polygon([
    [[73.79195,20.00625],
     [73.79230,20.00625],
     [73.79230,20.00580],
     [73.79195,20.00580]]
])

# Trimbakeshwar Kushavarta
KUSHAVARTA = ee.Geometry.Polygon([
    [[73.53060,19.93235],
     [73.53105,19.93235],
     [73.53105,19.93195],
     [73.53060,19.93195]]
])

roi = RAMKUND.union(KUSHAVARTA).buffer(2000)

# --------------------------------------------------
# MANUAL CALIBRATED WATER SPREAD (HECTARES)
# --------------------------------------------------
RAMKUND_AREA_HA = 0.30
KUSHAVARTA_AREA_HA = 0.10

# --------------------------------------------------
# GET SATELLITE DATA
# --------------------------------------------------
def get_latest_satellite():
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(roi)
        .filterDate("2024-01-01", "2024-12-31")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .select(["B3", "B4", "B8"])
    )

    if collection.size().getInfo() == 0:
        return None

    img = collection.median().clip(roi)

    ndvi = img.normalizedDifference(["B8", "B4"]).rename("NDVI")
    ndwi = img.normalizedDifference(["B3", "B8"]).rename("NDWI")

    return img.addBands([ndvi, ndwi])

latest_img = get_latest_satellite()

if latest_img is None:
    st.error("No satellite data found.")
    st.stop()

# --------------------------------------------------
# LIVE METRICS
# --------------------------------------------------
def get_live_stats(image):
    stats = image.select(["NDVI", "NDWI"]).reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=roi,
        scale=30,
        bestEffort=True,
        maxPixels=1e9
    ).getInfo()
    return stats if stats else {}

stats = get_live_stats(latest_img)
ndvi_live = stats.get("NDVI", 0)
ndwi_live = stats.get("NDWI", 0)

# --------------------------------------------------
# HISTORICAL DATA
# --------------------------------------------------
def fetch_historical_data():
    years = list(range(2016, datetime.datetime.now().year + 1))
    ndvi_vals = []
    ndwi_vals = []

    for y in years:
        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(roi)
            .filterDate(f"{y}-01-01", f"{y}-12-31")
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30))
            .select(["B3", "B4", "B8"])
        )

        if collection.size().getInfo() == 0:
            ndvi_vals.append(0)
            ndwi_vals.append(0)
            continue

        img = collection.median().clip(roi)
        ndvi = img.normalizedDifference(["B8", "B4"]).rename("NDVI")
        ndwi = img.normalizedDifference(["B3", "B8"]).rename("NDWI")

        stats = ndvi.addBands(ndwi).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=40,
            bestEffort=True,
            maxPixels=1e9
        ).getInfo()

        ndvi_vals.append(stats.get("NDVI", 0))
        ndwi_vals.append(stats.get("NDWI", 0))

    return pd.DataFrame({"Year": years, "NDVI": ndvi_vals, "NDWI": ndwi_vals})

data = fetch_historical_data()

# --------------------------------------------------
# TABS: OVERVIEW / KUNDS / RISK
# --------------------------------------------------
tab_overview, tab_kunds, tab_risk = st.tabs(
    ["Overview", "Kunds", "Risk & Forecasts"]
)

# ========= OVERVIEW TAB =========
with tab_overview:
    st.header("🌍 High Resolution Environmental Mapping")

    Map = geemap.Map(center=[20.006, 73.792], zoom=15)
    Map.addLayer(
        latest_img,
        {"bands": ["B4", "B3", "B8"], "min": 0, "max": 3000},
        "Satellite"
    )
    Map.addLayer(
        latest_img.select("NDVI").gt(0.4).selfMask(),
        {"palette": ["00FF00"]},
        "Dense Vegetation"
    )
    Map.addLayer(
        latest_img.select("NDWI").gt(0.15).selfMask(),
        {"palette": ["0000FF"]},
        "Water Bodies"
    )
    Map.addLayer(RAMKUND, {"color": "red"}, "Ramkund (Nashik)")
    Map.addLayer(KUSHAVARTA, {"color": "yellow"}, "Kushavarta (Trimbak)")
    Map.to_streamlit(height=600)

    st.subheader("📡 Live Environmental Indicators")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Vegetation Health (NDVI)", round(ndvi_live, 3))
    with col2:
        st.metric("Water Availability (NDWI)", round(ndwi_live, 3))

    st.caption(
        "Operational thresholds: NDVI above 0.4 indicates broadly healthy green cover, while NDWI above 0.3 "
        "indicates adequate surface water presence in the monitored corridor."
    )

# ========= KUNDS TAB =========
with tab_kunds:
    st.header("🏞️ Kund Water Spread Analysis")

    col3, col4 = st.columns(2)
    col3.metric("Ramkund Water Spread (Ha)", f"{RAMKUND_AREA_HA:.2f}")
    col4.metric("Kushavarta Water Spread (Ha)", f"{KUSHAVARTA_AREA_HA:.2f}")

    st.subheader("📊 Historical NDVI & NDWI ")
    fig = px.line(
        data,
        x="Year",
        y=["NDVI", "NDWI"],
        markers=True,
        template="plotly_dark",
        labels={"value": "Index value", "variable": "Indicator"},
    )
    fig.update_layout(
        height=400,
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig, width='stretch')

    st.caption(
        "This combined view allows planners to see whether Simhasth years correspond to abnormal depressions in "
        "vegetation or water availability relative to non‑event years."
    )

# ========= RISK & FORECAST TAB =========
with tab_risk:
    st.header("🔮 Kumbh 2027 Environmental Forecast")

    pred_ndvi, pred_ndwi = predict_future(
        data["Year"].values, data["NDVI"].values, data["NDWI"].values
    )

    col5, col6, col7 = st.columns(3)
    col5.metric("Predicted NDVI (2027)", round(pred_ndvi, 3))
    col6.metric("Predicted NDWI (2027)", round(pred_ndwi, 3))

    # SAME RISK LOGIC AS ADVANCED DASHBOARD
    risk_score = compute_environmental_risk(pred_ndvi, pred_ndwi)
    col7.metric("Environmental Risk Score (0–100)", risk_score)

    st.caption(
        "Interpretation: 0–20 = low environmental concern, 20–60 = moderate pressure requiring routine management, "
        ">60 = high‑risk condition requiring immediate regulatory and operational intervention."
    )

    st.subheader("Priority Environmental Management Actions")

    st.markdown(
        """
- **Crowd Management:** Implement dynamic crowd caps at Ramkund and Kushavarta during peak snan days, using real‑time satellite indicators and on‑ground counts.  
- **Kund Health:** Plan pre‑event and mid‑event desilting of both kunds, with a focus on maintaining minimum functional water spread and safe access routes.  
- **Riverfront Cleanliness:** Enforce strict controls on single‑use plastics, ritual waste, and open dumping along the riverfront, supported by dedicated cleaning teams and clear signage.  
- **Green Buffer Restoration:** Protect and restore riparian vegetation belts to stabilize banks, improve water quality, and reduce heat stress for pilgrims.  
- **Continuous Monitoring:** Establish a small NRSC–State control cell to review satellite‑based NDVI/NDWI trends and risk scores at least once per week in the 3–4 months around the event.
- **Government Implementation:** Ensuring water sprays along the riverfront, especially near kunds, to improve air quality and provide relief to pilgrims while also helping to maintain surface moisture levels of the bathing areas.   
"""
    )

    st.markdown("---")
    st.subheader("🔍 Advanced Environmental Analytics")
    st.caption(
        "Open the advanced dashboard to explore detailed Bathing Suitability Index (BSI), "
        "historical trends, and AI‑based forecasts for Ramkund and Kushavarta."
    )
   
    if st.button("📊 Open Advanced Dashboard"):
        st.switch_page("pages/advanced_dashboard.py")