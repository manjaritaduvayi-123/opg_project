from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# 🔥 Descriptions
DESCRIPTIONS = {
    "Caries": "Tooth decay detected",
    "Crown": "Dental crown present",
    "Missing_teeth": "Missing teeth detected",
    "Root_Canal_Treatment": "Root canal treated tooth",
    "Impacted_tooth": "Impacted tooth detected"
}

# 🔥 Suggestions (NEW)
SUGGESTIONS = {
    "Caries": "Visit a dentist for filling or cleaning.",
    "Crown": "Check crown condition periodically.",
    "Missing_teeth": "Consider dental implant or bridge.",
    "Root_Canal_Treatment": "Monitor treated tooth for infection.",
    "Impacted_tooth": "Consult dentist for possible extraction."
}


def generate_pdf(results, image_path, output_path):
    doc = SimpleDocTemplate(output_path)
    styles = getSampleStyleSheet()

    content = []

    # 🧾 Title
    content.append(Paragraph("Dental Analysis Report", styles["Title"]))
    content.append(Spacer(1, 12))

    # 🖼️ Image
    try:
        img = Image(image_path, width=4 * inch, height=3 * inch)
        content.append(img)
        content.append(Spacer(1, 12))
    except:
        content.append(Paragraph("Image not available", styles["Normal"]))
        content.append(Spacer(1, 10))

    # ❌ No detections
    if not results or len(results) == 0:
        content.append(Paragraph("No dental issues detected.", styles["Normal"]))

    else:
        # 🔥 REMOVE DUPLICATES (important)
        unique_results = {}
        for r in results:
            cls = r["class"]
            if cls not in unique_results or r["confidence"] > unique_results[cls]["confidence"]:
                unique_results[cls] = r

        final_results = list(unique_results.values())

        # 🔥 Top defect
        top_defect = max(final_results, key=lambda x: x["confidence"])["class"]

        # 🔥 Summary (NEW)
        content.append(Paragraph(f"<b>Top Issue:</b> {top_defect}", styles["Heading2"]))
        content.append(Spacer(1, 10))

        content.append(Paragraph("<b>Detected Issues:</b>", styles["Heading2"]))
        content.append(Spacer(1, 10))

        # 🔍 Loop through results
        for r in final_results:
            class_name = r.get("class", "Unknown")
            confidence = round(r.get("confidence", 0) * 100, 2)

            description = DESCRIPTIONS.get(class_name, "No description available")
            suggestion = SUGGESTIONS.get(class_name, "Consult a dentist.")

            text = f"""
            <b>{class_name}</b><br/>
            Confidence: {confidence}%<br/>
            {description}<br/>
            <b>Suggestion:</b> {suggestion}
            """

            content.append(Paragraph(text, styles["Normal"]))
            content.append(Spacer(1, 12))

    doc.build(content)
    return output_path