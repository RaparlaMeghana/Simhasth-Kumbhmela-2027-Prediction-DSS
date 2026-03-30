import random
from kund_analysis import get_kund_stats


# =====================================================
# 1️⃣ SIMULATED REAL-TIME CROWD DATA
# (Later replace with telecom API / IoT feed)
# =====================================================

def simulate_crowd(min_people=500, max_people=20000):
    return random.randint(min_people, max_people)


# =====================================================
# 2️⃣ CALCULATE CROWD METRICS
# =====================================================

def calculate_crowd_metrics(current_crowd, safe_capacity):

    if safe_capacity == 0:
        return {
            "density": 0,
            "congestion_index": 0,
            "risk_level": "NO WATER AREA"
        }

    congestion_index = current_crowd / safe_capacity

    # Density approximation (assuming 2 sq.m safety norm)
    density = current_crowd / (safe_capacity * 2)

    # Risk classification
    if congestion_index < 0.6:
        risk = "LOW"
    elif 0.6 <= congestion_index < 1:
        risk = "MODERATE"
    elif 1 <= congestion_index < 1.3:
        risk = "HIGH"
    else:
        risk = "CRITICAL"

    return {
        "density": round(density, 2),
        "congestion_index": round(congestion_index, 2),
        "risk_level": risk
    }


# =====================================================
# 3️⃣ MASTER CROWD ANALYSIS FUNCTION
# =====================================================

def analyze_crowd():

    kund_data = get_kund_stats()

    results = {}

    for kund_name, stats in kund_data.items():

        safe_capacity = stats["safe_crowd_capacity"]

        current_crowd = simulate_crowd()

        crowd_metrics = calculate_crowd_metrics(
            current_crowd,
            safe_capacity
        )

        results[kund_name] = {
            "current_crowd": current_crowd,
            "safe_capacity": safe_capacity,
            "density": crowd_metrics["density"],
            "congestion_index": crowd_metrics["congestion_index"],
            "risk_level": crowd_metrics["risk_level"]
        }

    return results


# =====================================================
# TEST RUN
# =====================================================

if __name__ == "__main__":

    crowd_results = analyze_crowd()

    print("\n👥 Crowd Steering Analysis")
    print("--------------------------------")

    for kund, data in crowd_results.items():
        print(f"\n📍 {kund}")
        print("Current Crowd:", data["current_crowd"])
        print("Safe Capacity:", data["safe_capacity"])
        print("Density:", data["density"])
        print("Congestion Index:", data["congestion_index"])
        print("Risk Level:", data["risk_level"])