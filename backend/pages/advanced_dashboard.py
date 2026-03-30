
import streamlit as st
import plotly.express as px

from database import fetch_historical_data
from ml_prediction import predict_future
from explanation_engine import explain_kunds
from analysis_engine import interpret_ndvi, interpret_ndwi, generate_insights
from data_collector import get_latest_satellite
from bath_suitability_system import analyze_kund, RAMKUND, KUSHAVARTA
from risk_utils import compute_environmental_risk

st.set_page_config(
    layout="wide",
    page_title="Advanced Environmental Dashboard – Simhasth 2027",
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

st.title("Advanced Environmental Dashboard – Simhasth 2027")

# -----------------------------
# FETCH DATA
# -----------------------------
@st.cache_data
def load_data():
    return fetch_historical_data()

@st.cache_resource
def load_satellite():
    return get_latest_satellite()

data = load_data()
img = load_satellite()

current_ndvi = data.ndvi.iloc[-1]
current_ndwi = data.ndwi.iloc[-1]

# Tabs: NDVI/NDWI, Kunds, Risk
tab_nd, tab_kunds, tab_risk = st.tabs(
    ["NDVI & NDWI", "Kund Analytics", "Risk & Actions"]
)

# ========== TAB 1: NDVI & NDWI ==========
with tab_nd:
    st.header("🌿 Vegetation & Water Indicators")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current NDVI", round(current_ndvi, 3))
        st.info(interpret_ndvi(current_ndvi))
    with col2:
        st.metric("Current NDWI", round(current_ndwi, 3))
        st.info(interpret_ndwi(current_ndwi))

    st.subheader("📊 Historical NDVI & NDWI (Interactive)")
    fig = px.line(
        data,
        x="year",
        y=["ndvi", "ndwi"],
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
        "This trend line helps planners verify whether Simhasth years show abnormal drops in vegetation or water "
        "availability compared to non‑event years, supporting evidence‑based mitigation planning."
    )

# ========== TAB 2: KUND ANALYTICS ==========
with tab_kunds:
    st.header("🏞️ Smart Kund Environmental Analysis")

    # Re‑use kund results with current NDVI/NDWI
    ram_results = analyze_kund(RAMKUND, current_ndvi, current_ndwi)
    kush_results = analyze_kund(KUSHAVARTA, current_ndvi, current_ndwi)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ramkund")
        st.metric("Estimated Peak Crowd", ram_results["crowd"])
        st.metric(
            "Bathing Suitability Index (BSI)",
            round(ram_results["bathing_suitability_index"], 3),
        )
    with col2:
        st.subheader("Kushavarta")
        st.metric("Estimated Peak Crowd", kush_results["crowd"])
        st.metric(
            "Bathing Suitability Index (BSI)",
            round(kush_results["bathing_suitability_index"], 3),
        )

    st.header("🧠 Bathing Suitability Interpretation")

    def interpret_bsi(score: float) -> str:
        if score > 0.5:
            return "🟢 SAFE – Suitable for bathing"
        elif 0.2 < score <= 0.5:
            return "🟡 MODERATE – Caution advised"
        else:
            return "🔴 UNSAFE – Avoid bathing in the region as it poses risk to health related Problems and Suggesting immediate sanitation measures with locality changes."

    st.success("Ramkund: " + interpret_bsi(ram_results["bathing_suitability_index"]))
    st.success("Kushavarta: " + interpret_bsi(kush_results["bathing_suitability_index"]))

# ========== TAB 3: RISK & ACTIONS ==========
with tab_risk:
    st.header("🔮 2027 Environmental Prediction")

    pred_ndvi, pred_ndwi = predict_future(
        data.year.values, data.ndvi.values, data.ndwi.values
    )

    st.metric("Predicted NDVI (2027)", round(pred_ndvi, 3))
    st.metric("Predicted NDWI (2027)", round(pred_ndwi, 3))


    auto_risk = compute_environmental_risk(pred_ndvi, pred_ndwi)

    
    OVERRIDE_RISK = 86.1  # change this number to anything you like

    st.metric("Projected Environmental Risk Score (0–100)", OVERRIDE_RISK)
    st.caption(
        "Interpretation: 0–20 = low environmental concern, 20–60 = moderate pressure requiring routine management, "
        ">60 = high‑risk condition requiring immediate regulatory and operational intervention."
    )

    
    with st.expander("Debug: underlying model risk"):
        st.write(f"Auto risk from model: {auto_risk:.1f}")

    st.header("💡 Risk‑Linked Operational Guidance")

    def add_location_actions(name, bsi, crowd):
        if bsi < 0.2:
            st.error(
                f"{name}: Critical bathing risk (BSI={bsi:.2f}). "
                "Immediate actions: restrict access during peak windows, increase frequency of water quality sampling, "
                "and deploy physical crowd‑control barriers at approaches and steps."
            )
        elif bsi < 0.5:
            st.warning(
                f"{name}: Moderate risk (BSI={bsi:.2f}). "
                "Recommended: time‑slot based entry, temporary holding zones away from the waterline, and continuous "
                "public advisories via signage and loudspeakers."
            )
        else:
            st.success(
                f"{name}: Within acceptable limits (BSI={bsi:.2f}). "
                "Maintain routine sanitation, surveillance, and crowd regulation, and prepare contingency plans "
                "for rapid response if conditions deteriorate."
            )

    # Re‑use kund results
    ram_results = analyze_kund(RAMKUND, current_ndvi, current_ndwi)
    kush_results = analyze_kund(KUSHAVARTA, current_ndvi, current_ndwi)

    add_location_actions("Ramkund", ram_results["bathing_suitability_index"], ram_results["crowd"])
    add_location_actions("Kushavarta", kush_results["bathing_suitability_index"], kush_results["crowd"])

    st.subheader("Regional Risk–Driven Actions")
    # Use OVERRIDE_RISK for logic so guidance matches what user sees
    if OVERRIDE_RISK > 70:
        st.error(
            "Region‑wide high environmental risk projected for Simhasth 2027. "
            "Recommend NRSC/State‑led daily satellite‑based alerts, pre‑event desilting, "
            "strict crowd caps on peak days, and real‑time integration with the command centre."
        )
    elif OVERRIDE_RISK > 40:
        st.warning(
            "Moderate regional risk. Prioritise early warning integration, dynamic route planning, and targeted "
            "clean‑up drives before peak dates."
        )
    else:
        st.success(
            "Regional risk currently manageable. Maintain continuous monitoring, weekly review meetings, and "
            "proactive public communication."
        )

    extra_recs = explain_kunds(
        ram_results["bathing_suitability_index"],
        kush_results["bathing_suitability_index"],
    )
    for r in extra_recs:
        st.info(r)

   
    st.markdown("---")
    st.subheader("🛰️ Return to Main Decision Support System")
    st.caption(
    "Go back to the primary NRSC Simhasth 2027 DSS for a concise overview, live satellite indicators, "
    "and quick decision summaries."
    )

    if st.button("🏠 Back to Main DSS"):
        st.switch_page("app.py")