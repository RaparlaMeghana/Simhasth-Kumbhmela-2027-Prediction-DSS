def interpret_ndvi(value):
    if value > 0.6:
        return "Excellent vegetation health"
    elif value > 0.4:
        return "Healthy vegetation cover"
    elif value > 0.2:
        return "Moderate vegetation — signs of stress"
    else:
        return "Low vegetation — environmental degradation"

def interpret_ndwi(value):
    if value > 0.4:
        return "High water availability"
    elif value > 0.2:
        return "Moderate water levels"
    elif value > 0:
        return "Low water levels"
    else:
        return "Severe water stress"

def generate_insights(ndvi_trend, ndwi_trend):

    insights = []

    if ndvi_trend < 0:
        insights.append("Vegetation declining due to urban expansion and human pressure.")

    if ndwi_trend < 0:
        insights.append("Water levels decreasing — risk of water shortage during Kumbh.")

    if ndwi_trend < -0.05:
        insights.append("High flood vulnerability during monsoon due to unstable water balance.")

    return insights
