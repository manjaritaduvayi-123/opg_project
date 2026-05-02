from flask import Blueprint, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from utils.pdf_utils import generate_pdf
from utils.email_utils import send_email
from db import reports
import time
import cv2

upload_bp = Blueprint('upload', __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

<<<<<<< HEAD
=======
# 🔥 MODEL
>>>>>>> 24ab891 (Updated dashboard UI, added loader, fixed email sharing)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "best.pt")
model = YOLO(MODEL_PATH)

<<<<<<< HEAD

=======
# 🔥 CLASSES
>>>>>>> 24ab891 (Updated dashboard UI, added loader, fixed email sharing)
CLASS_NAMES = [
    "Caries",
    "Crown",
    "Missing_teeth",
    "Root_Canal_Treatment",
    "Impacted_tooth"
]

<<<<<<< HEAD

=======
# 🔥 SUGGESTIONS
>>>>>>> 24ab891 (Updated dashboard UI, added loader, fixed email sharing)
SUGGESTIONS = {
    "Caries": "Tooth decay detected. Filling or root canal may be required.",
    "Crown": "Crown is present. Regular dental checkup recommended.",
    "Missing_teeth": "Missing teeth detected. Consider implants or bridges.",
    "Root_Canal_Treatment": "Previously treated tooth. Monitor condition regularly.",
    "Impacted_tooth": "Impacted tooth detected. Surgical evaluation may be required."
}


<<<<<<< HEAD

=======
# -------------------------------
# 🔍 UPLOAD + ANALYZE
# -------------------------------
>>>>>>> 24ab891 (Updated dashboard UI, added loader, fixed email sharing)
@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file received"}), 400

        file = request.files['file']
        email = request.form.get("email")

<<<<<<< HEAD
        
=======
        # 📁 Save original
>>>>>>> 24ab891 (Updated dashboard UI, added loader, fixed email sharing)
        filename = f"{int(time.time())}_{secure_filename(file.filename)}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

<<<<<<< HEAD
        
=======
        # 🔥 YOLO PREDICTION
>>>>>>> 24ab891 (Updated dashboard UI, added loader, fixed email sharing)
        results = model.predict(
            source=filepath,
            conf=0.5,
            iou=0.5,
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
                    "bbox": list(map(float, box.xyxy[0])),
                    "suggestion": SUGGESTIONS.get(class_name, "Consult a dentist")
                })

<<<<<<< HEAD
        
=======
        # 🔥 REMOVE DUPLICATES
>>>>>>> 24ab891 (Updated dashboard UI, added loader, fixed email sharing)
        unique_results = {}
        for item in raw_output:
            cls = item["class"]
            if cls not in unique_results or item["confidence"] > unique_results[cls]["confidence"]:
                unique_results[cls] = item

        output = list(unique_results.values())
        output = sorted(output, key=lambda x: x["confidence"], reverse=True)

<<<<<<< HEAD
        
        top_defect = output[0]["class"] if output else "No Detection"

        
=======
        # 🔥 TOP DEFECT
        top_defect = output[0]["class"] if output else "No Detection"

        # 💾 SAVE TO DB
>>>>>>> 24ab891 (Updated dashboard UI, added loader, fixed email sharing)
        reports.insert_one({
            "email": email,
            "file": filename,
            "result": output,
            "top_defect": top_defect
        })

<<<<<<< HEAD
        
=======
        # 📄 GENERATE PDF
>>>>>>> 24ab891 (Updated dashboard UI, added loader, fixed email sharing)
        pdf_name = f"{filename.split('.')[0]}_report.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_name)
        generate_pdf(output, filepath, pdf_path)

<<<<<<< HEAD
        
=======
        # 🔥 CREATE YOLO OUTPUT IMAGE
>>>>>>> 24ab891 (Updated dashboard UI, added loader, fixed email sharing)
        clean_name = f"det_{filename}"
        clean_path = os.path.join(UPLOAD_FOLDER, clean_name)

        for r in results:
            plotted = r.plot(labels=True, conf=False)
            cv2.imwrite(clean_path, plotted)

<<<<<<< HEAD
=======
        print("✅ Saved YOLO image:", clean_path)

        # ✅ FINAL RESPONSE (FIXED)
>>>>>>> 24ab891 (Updated dashboard UI, added loader, fixed email sharing)
        return jsonify({
            "message": "Analysis complete",
            "file": filename,
            "image": clean_name,   # 🔥 FIXED (no uploads/)
            "pdf": pdf_name,
            "predictions": output,
            "top_defect": top_defect
        })

    except Exception as e:
        print("❌ Upload Error:", str(e))
        return jsonify({"error": str(e)}), 500


<<<<<<< HEAD

=======
# -------------------------------
# 📂 SERVE IMAGES
# -------------------------------
>>>>>>> 24ab891 (Updated dashboard UI, added loader, fixed email sharing)
@upload_bp.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


<<<<<<< HEAD

=======
# -------------------------------
# 📧 SHARE REPORT
# -------------------------------
>>>>>>> 24ab891 (Updated dashboard UI, added loader, fixed email sharing)
@upload_bp.route("/share", methods=["POST"])
def share_report():
    try:
        data = request.json
        print("🔥 Incoming data:", data)  # DEBUG

        email = data.get("email")
        file_name = data.get("file")

        # ✅ VALIDATIONS
        if not email:
            return jsonify({"error": "Email is required"}), 400

        if not file_name:
            return jsonify({"error": "File name missing"}), 400

        # ✅ BUILD PDF NAME
        base_name = os.path.splitext(file_name)[0]   # 🔥 safer than split
        pdf_name = f"{base_name}_report.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_name)

        print("📄 PDF path:", pdf_path)

        if not os.path.exists(pdf_path):
            return jsonify({"error": f"Report not found: {pdf_name}"}), 400

        # ✅ SEND EMAIL
        send_email(
            to_email=email,
            subject="Dental Report",
            body="Your dental report is attached.",
            attachment_path=pdf_path
        )

        print("📧 Email sent to:", email)

        return jsonify({"msg": "Email sent successfully"})

    except Exception as e:
        print("❌ Share Error:", str(e))
        return jsonify({"error": str(e)}), 500

<<<<<<< HEAD


=======
# -------------------------------
# 📜 HISTORY
# -------------------------------
>>>>>>> 24ab891 (Updated dashboard UI, added loader, fixed email sharing)
@upload_bp.route("/history/<email>", methods=["GET"])
def history(email):
    try:
        data = list(reports.find({"email": email}, {"_id": 0}))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
