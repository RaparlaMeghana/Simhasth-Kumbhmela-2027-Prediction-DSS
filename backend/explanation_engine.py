def explain_kunds(ram_area, kush_area):

    text = []

    # -----------------------
    # Total Kund Capacities (realistic estimates)
    # -----------------------
    RAM_TOTAL = 32000
    KUSH_TOTAL = 25000

    ram_percent = (ram_area / RAM_TOTAL) * 100
    kush_percent = (kush_area / KUSH_TOTAL) * 100

    # =========================
    # RAMKUND ANALYSIS
    # =========================
    if ram_percent < 30:
        text.append(
            f"🚨 Ramkund critically low: Only 0.30 water available. "
            "High risk of drying during Kumbh."
        )

        text.append(
            "Recommended: Immediate water replenishment from Godavari canal and pollution control measures."
        )

    elif ram_percent < 60:
        text.append(
            f"⚠️ Ramkund moderate level: 0.30 capacity. "
            "Crowd pressure may reduce water quality."
        )

    else:
        text.append(
            f"✅ Ramkund healthy: {ram_percent:.1f}% water capacity."
        )

    # =========================
    # KUSHAVARTA ANALYSIS
    # =========================
    if kush_percent < 30:
        text.append(
            f"🚨 Kushavarta critically low: Only 0.10 water present."
        )

        text.append(
            "Action needed: Desilting, groundwater recharge, and controlled usage."
        )

    elif kush_percent < 60:
        text.append(
            f"⚠️ Kushavarta moderate level: 0.10 water."
        )

    else:
        text.append(
            f"✅ Kushavarta stable: {kush_percent:.1f}% water capacity."
        )

    # =========================
    # ENVIRONMENTAL IMPACT
    # =========================
    avg = (ram_percent + kush_percent) / 2

    if avg < 40:
        text.append(
            "🌍 Overall environmental risk HIGH — Water shortage likely during Kumbh 2027."
        )
    elif avg < 70:
        text.append(
            "🌍 Moderate environmental risk — Proper management required."
        )
    else:
        text.append(
            "🌍 Environmental condition stable."
        )

    # =========================
    # GOVERNMENT ACTIONS
    # =========================
    text.append(
        "🏛️ Government should ensure continuous water inflow, install floating waste collectors, and monitor NDWI weekly."
    )
    text.append("📍 Nearby upstream Godavari stretches show relatively higher NDWI=0.31 and stable NDVI=0.36." )
    text.append("indicating better water availability and bathing suitability index=0.11 cleaner conditions")
    text.append("—these zones can be considered as supplementary bathing areas to reduce crowd pressure on Ramkund during peak Kumbh days.")
    
    text.append("✅ Recommendation: Identify and develop upstream Godavari zones with higher water presence (NDWI=0.31) as alternative bathing ghats ")
    text.append("To safely distribute peak Kumbh crowd load where Crowd Factor= 0.25 from Ramkund.")

    text.append(
        "💧 Implement water conservation measures in the area to enhance groundwater recharge and maintain sustainable water levels in both kunds."
    )

    

    # =========================
    # PUBLIC ACTIONS
    # =========================
    text.append(
        "👥 Public must avoid soap usage, plastic disposal, and overcrowding near kund edges."
    )

    return text
