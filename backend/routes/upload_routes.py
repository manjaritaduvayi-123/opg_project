from flask import Blueprint, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from utils.pdf_utils import generate_pdf
from utils.email_utils import send_email
from db import reports
import time
import cv2
import numpy as np

upload_bp = Blueprint('upload', __name__)

# 🔥 SETUP DYNAMIC ABSOLUTE PATHS FOR UPLOADS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔥 MODEL SETUP
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")
model = YOLO(MODEL_PATH)

# 🔥 CLASSES
CLASS_NAMES = [
    "Caries",
    "Crown",
    "Missing_teeth",
    "Root_Canal_Treatment",
    "Impacted_tooth"
]

# 🔥 SUGGESTIONS
SUGGESTIONS = {
    "Caries": "Tooth decay detected. Filling or root canal may be required.",
    "Crown": "Crown is present. Regular dental checkup recommended.",
    "Missing_teeth": "Missing teeth detected. Consider implants or bridges.",
    "Root_Canal_Treatment": "Previously treated tooth. Monitor condition regularly.",
    "Impacted_tooth": "Impacted tooth detected. Surgical evaluation may be required."
}


# ------------------------------------------------
# 🔥 IMPROVED AI HEATMAP
# ------------------------------------------------
def create_heatmap(image_path, detections):
    image = cv2.imread(image_path)
    h, w = image.shape[:2]
    heatmap = np.zeros((h, w), dtype=np.float32)

    for det in detections:
        x1, y1, x2, y2 = map(int, det["bbox"])
        conf = float(det["confidence"])

        overlay = np.zeros((h, w), dtype=np.float32)

        # Center of detection
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        # Detection size
        axes = (
            max((x2 - x1) // 2, 10),
            max((y2 - y1) // 2, 10)
        )

        # Draw ellipse instead of full rectangle
        cv2.ellipse(
            overlay,
            (center_x, center_y),
            axes,
            0,
            0,
            360,
            conf * 255,
            -1
        )

        # Smaller blur for sharper hotspots
        overlay = cv2.GaussianBlur(
            overlay,
            (41, 41),
            0
        )

        heatmap += overlay

    heatmap = cv2.normalize(
        heatmap,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    heatmap = heatmap.astype(np.uint8)
    heatmap_color = cv2.applyColorMap(
        heatmap,
        cv2.COLORMAP_JET
    )

    result = cv2.addWeighted(
        image,
        0.8,
        heatmap_color,
        0.2,
        0
    )

    return result

# ------------------------------------------------
# 🔍 UPLOAD + ANALYZE
# ------------------------------------------------
@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({
                "error": "No file received"
            }), 400

        file = request.files['file']
        email = request.form.get("email")

        # 🔥 SAVE ORIGINAL IMAGE
        filename = (
            f"{int(time.time())}_"
            f"{secure_filename(file.filename)}"
        )

        filepath = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        file.save(filepath)

        # ------------------------------------------------
        # 🔥 YOLO PREDICTION
        # ------------------------------------------------
        results = model.predict(
            source=filepath,
            conf=0.25,
            iou=0.3,
            save=False
        )

        raw_output = []

        for r in results:
            if r.boxes is None:
                continue

            for box in r.boxes:
                cls_id = int(box.cls)

                if cls_id >= len(CLASS_NAMES):
                    continue

                class_name = CLASS_NAMES[cls_id]

                raw_output.append({
                    "class": class_name,
                    "confidence": float(box.conf),
                    "bbox": list(
                        map(float, box.xyxy[0])
                    ),
                    "suggestion": SUGGESTIONS.get(
                        class_name,
                        "Consult dentist"
                    )
                })

        # ------------------------------------------------
        # 🔥 REMOVE DUPLICATE CLASSES
        # Keep only highest confidence detection
        # ------------------------------------------------
        unique_classes = {}

        for det in raw_output:
            cls = det["class"]

            if cls not in unique_classes:
                unique_classes[cls] = det
            elif (
                det["confidence"]
                > unique_classes[cls]["confidence"]
            ):
                unique_classes[cls] = det

        output = list(
            unique_classes.values()
        )

        # 🔥 SORT BY CONFIDENCE
        output = sorted(
            output,
            key=lambda x: x["confidence"],
            reverse=True
        )
        
        # 🔥 TOP DEFECT
        top_defect = (
            output[0]["class"]
            if output
            else "No Detection"
        )

        # ------------------------------------------------
        # 💾 SAVE DATABASE
        # ------------------------------------------------
        reports.insert_one({
            "email": email,
            "file": filename,
            "result": output,
            "top_defect": top_defect
        })

        # ------------------------------------------------
        # 📄 GENERATE PDF (Fixed Name Truncation)
        # ------------------------------------------------
        base_name = os.path.splitext(filename)[0]
        pdf_name = f"{base_name}_report.pdf"

        pdf_path = os.path.join(
            UPLOAD_FOLDER,
            pdf_name
        )

        generate_pdf(
            output,
            filepath,
            pdf_path
        )

        # ------------------------------------------------
        # 🔥 DETECTION IMAGE
        # ------------------------------------------------
        detected_name = f"det_{filename}"

        detected_path = os.path.join(
            UPLOAD_FOLDER,
            detected_name
        )

        for r in results:
            plotted = r.plot(
                labels=True,
                conf=True
            )

            cv2.imwrite(
                detected_path,
                plotted
            )

        # ------------------------------------------------
        # 🔥 HEATMAP IMAGE
        # ------------------------------------------------
        heatmap_name = f"heatmap_{filename}"

        heatmap_path = os.path.join(
            UPLOAD_FOLDER,
            heatmap_name
        )

        heatmap_image = create_heatmap(
            filepath,
            raw_output
        )

        cv2.imwrite(
            heatmap_path,
            heatmap_image
        )

        print("🔥 Heatmap saved")

        # ------------------------------------------------
        # 🔥 RESPONSE
        # ------------------------------------------------
        return jsonify({
            "message": "Analysis complete",
            "file": filename,
            "image": detected_name,
            "heatmap": heatmap_name,
            "pdf": pdf_name,
            "predictions": output,
            "top_defect": top_defect
        })

    except Exception as e:
        print("❌ Upload Error:", str(e))
        return jsonify({
            "error": str(e)
        }), 500


# ------------------------------------------------
# 📂 SERVE FILES (Fixed Directory Context)
# ------------------------------------------------
@upload_bp.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(
        os.path.abspath(UPLOAD_FOLDER),
        filename
    )


# ------------------------------------------------
# 📧 SHARE REPORT
# ------------------------------------------------
@upload_bp.route("/share", methods=["POST"])
def share_report():
    try:
        data = request.get_json()

        email = data.get("email")
        file_name = data.get("file")

        if not email:
            return jsonify({
                "error": "Email required"
            }), 400

        if not file_name:
            return jsonify({
                "error": "File missing"
            }), 400

        base_name = os.path.splitext(file_name)[0]
        pdf_name = f"{base_name}_report.pdf"

        pdf_path = os.path.join(
            UPLOAD_FOLDER,
            pdf_name
        )

        if not os.path.exists(pdf_path):
            return jsonify({
                "error": f"PDF not found: {pdf_path}"
            }), 404

        send_email(
            to_email=email,
            subject="Dental AI Report",
            body="Your dental analysis report is attached.",
            attachment_path=pdf_path
        )

        return jsonify({
            "msg": "Email sent successfully"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# ------------------------------------------------
# 📜 HISTORY
# ------------------------------------------------
@upload_bp.route("/history/<email>", methods=["GET"])
def history(email):
    try:
        data = list(
            reports.find(
                {"email": email},
                {"_id": 0}
            )
        )
        return jsonify(data)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500