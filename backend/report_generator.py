from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf_report(ndvi, ndwi, risk, recs):

    file = "Kumbh_Report.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Kumbh 2027 Environmental Report", styles["Title"]))
    content.append(Paragraph(f"Predicted NDVI: {ndvi}", styles["BodyText"]))
    content.append(Paragraph(f"Predicted NDWI: {ndwi}", styles["BodyText"]))
    content.append(Paragraph(f"Risk Score: {risk}", styles["BodyText"]))

    content.append(Paragraph("Recommendations:", styles["Heading2"]))

    for r in recs:
        content.append(Paragraph(r, styles["BodyText"]))

    doc.build(content)

    return file
