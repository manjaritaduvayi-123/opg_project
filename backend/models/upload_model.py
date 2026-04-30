from ultralytics import YOLO
import cv2

# Load YOLO model
model = YOLO("models/best.pt")

# Classes
classes = [
    "Caries", "Crown", "Filling", "Implant", "Malaligned",
    "Mandibular Canal", "Missing teeth", "Periapical lesion",
    "Retained root", "Root Canal Treatment", "Root Piece",
    "Impacted tooth", "Maxillary sinus", "Bone Loss",
    "Fracture teeth", "Permanent Teeth", "Supra Eruption",
    "TAD", "Abutment", "Attrition", "Bone defect",
    "Gingival former", "Metal band", "Orthodontic brackets",
    "Permanent retainer", "Post-core", "Plating", "Wire",
    "Cyst", "Root resorption", "Primary teeth"
]

# Descriptions
descriptions = {
    "Caries": "Tooth decay caused by bacteria.",
    "Bone Loss": "Loss of bone around teeth.",
    "Fracture teeth": "Cracked or broken tooth.",
    "Missing teeth": "One or more teeth missing.",
    "Implant": "Artificial tooth root.",
    "Cyst": "Fluid-filled sac in jaw.",
    "Partial Edentulous": "Some teeth are missing.",
    "Uncertain detection": "Model is not confident."
}

# Suggestions
suggestions = {
    "Caries": "Get a filling.",
    "Bone Loss": "Treat gum disease.",
    "Fracture teeth": "Repair or crown needed.",
    "Missing teeth": "Consider implants.",
    "Implant": "Regular checkups.",
    "Cyst": "Consult dentist.",
    "Partial Edentulous": "Dentures or implants.",
    "Uncertain detection": "Upload clearer image."
}


def predict_image(path):
    try:
        results = model(path)

        output = []

        # =========================
        # 🔍 DETECTION LOOP
        # =========================
        for r in results:
            if r.boxes is None:
                continue

            for box in r.boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])

                # ✅ LOWER FILTER (IMPORTANT FIX)
                if confidence < 0.3:
                    continue

                class_name = classes[cls_id] if cls_id < len(classes) else "Unknown"

                desc = descriptions.get(class_name, "Dental condition detected.")
                suggestion = suggestions.get(class_name, "Consult a dentist.")

                # ⚠️ Soft warning (NOT blocking)
                warning = ""
                if confidence < 0.5:
                    warning = "Low confidence prediction"

                output.append({
                    "class": class_name,
                    "confidence": round(confidence, 2),
                    "description": desc,
                    "suggestion": suggestion,
                    "warning": warning
                })

        # =========================
        # 🔥 REMOVE DUPLICATES
        # =========================
        unique = {}
        for item in output:
            cls = item["class"]
            if cls not in unique or item["confidence"] > unique[cls]["confidence"]:
                unique[cls] = item

        output = list(unique.values())

        # =========================
        # 🔥 SORT + LIMIT RESULTS
        # =========================
        output = sorted(output, key=lambda x: x["confidence"], reverse=True)
        output = output[:3]

        # =========================
        # 🔥 PARTIAL EDENTULOUS LOGIC
        # =========================
        missing_count = sum(1 for o in output if o["class"] == "Missing teeth")

        if missing_count >= 2:
            output.insert(0, {
                "class": "Partial Edentulous",
                "confidence": 0.9,
                "description": descriptions["Partial Edentulous"],
                "suggestion": suggestions["Partial Edentulous"],
                "warning": "Multiple teeth missing."
            })

        # =========================
        # 🔥 FALLBACK
        # =========================
        if len(output) == 0:
            return [{
                "class": "Uncertain detection",
                "confidence": 0,
                "description": "Model is not confident.",
                "suggestion": "Upload clearer image.",
                "warning": "Low confidence"
            }]

        return output

    except Exception as e:
        return [{"error": str(e)}]