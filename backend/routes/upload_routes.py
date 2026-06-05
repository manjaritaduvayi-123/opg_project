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

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔥 MODEL
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "..",
    "best.pt"
)

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

        conf = det["confidence"]

        # 🔥 CENTER
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        # 🔥 RADIUS
        radius = max(
            (x2 - x1),
            (y2 - y1)
        ) // 2

        # 🔥 TEMP OVERLAY
        overlay = np.zeros((h, w), dtype=np.float32)

        # 🔥 DRAW GLOW
        cv2.circle(
            overlay,
            (center_x, center_y),
            radius,
            conf * 255,
            -1
        )

        # 🔥 BLUR
        overlay = cv2.GaussianBlur(
            overlay,
            (151, 151),
            0
        )

        heatmap += overlay

    # 🔥 NORMALIZE
    heatmap = np.clip(
        heatmap,
        0,
        255
    ).astype(np.uint8)

    # 🔥 APPLY COLOR
    heatmap_color = cv2.applyColorMap(
        heatmap,
        cv2.COLORMAP_TURBO
    )

    # 🔥 BLEND
    overlay_image = cv2.addWeighted(
        image,
        0.7,
        heatmap_color,
        0.5,
        0
    )

    return overlay_image


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
        # 🔥 KEEP ALL DETECTIONS
        # ------------------------------------------------
        output = raw_output

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
        # 📄 GENERATE PDF
        # ------------------------------------------------
        pdf_name = (
            f"{filename.split('.')[0]}"
            f"_report.pdf"
        )

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
            output
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
# 📂 SERVE FILES
# ------------------------------------------------
@upload_bp.route('/uploads/<path:filename>')
def serve_upload(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# ------------------------------------------------
# 📧 SHARE REPORT
# ------------------------------------------------
@upload_bp.route("/share", methods=["POST"])
def share_report():

    try:

        data = request.json

        email = data.get("email")

        file_name = data.get("file")

        if not email:

            return jsonify({
                "error": "Email is required"
            }), 400

        if not file_name:

            return jsonify({
                "error": "File missing"
            }), 400

        base_name = os.path.splitext(
            file_name
        )[0]

        pdf_name = f"{base_name}_report.pdf"

        pdf_path = os.path.join(
            UPLOAD_FOLDER,
            pdf_name
        )

        if not os.path.exists(pdf_path):

            return jsonify({
                "error": "PDF not found"
            }), 400

        send_email(
            to_email=email,
            subject="Dental Report",
            body="Your dental report is attached.",
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