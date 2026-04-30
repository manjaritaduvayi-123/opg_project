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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "best.pt")
model = YOLO(MODEL_PATH)


CLASS_NAMES = [
    "Caries",
    "Crown",
    "Missing_teeth",
    "Root_Canal_Treatment",
    "Impacted_tooth"
]


SUGGESTIONS = {
    "Caries": "Tooth decay detected. Filling or root canal may be required.",
    "Crown": "Crown is present. Regular dental checkup recommended.",
    "Missing_teeth": "Missing teeth detected. Consider implants or bridges.",
    "Root_Canal_Treatment": "Previously treated tooth. Monitor condition regularly.",
    "Impacted_tooth": "Impacted tooth detected. Surgical evaluation may be required."
}



@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file received"}), 400

        file = request.files['file']
        email = request.form.get("email")

        
        filename = f"{int(time.time())}_{secure_filename(file.filename)}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        
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

        
        unique_results = {}
        for item in raw_output:
            cls = item["class"]
            if cls not in unique_results or item["confidence"] > unique_results[cls]["confidence"]:
                unique_results[cls] = item

        output = list(unique_results.values())
        output = sorted(output, key=lambda x: x["confidence"], reverse=True)

        
        top_defect = output[0]["class"] if output else "No Detection"

        
        reports.insert_one({
            "email": email,
            "file": filename,
            "result": output,
            "top_defect": top_defect
        })

        
        pdf_name = f"{filename.split('.')[0]}_report.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_name)
        generate_pdf(output, filepath, pdf_path)

        
        clean_name = f"det_{filename}"
        clean_path = os.path.join(UPLOAD_FOLDER, clean_name)

        for r in results:
            plotted = r.plot(labels=True, conf=False)
            cv2.imwrite(clean_path, plotted)

        return jsonify({
            "message": "Analysis complete",
            "file": filename,                     # 🔥 REQUIRED for frontend
            "image": f"uploads/{clean_name}",     # clean image
            "pdf": pdf_name,
            "predictions": output,
            "top_defect": top_defect
        })

    except Exception as e:
        print("❌ Upload Error:", str(e))
        return jsonify({"error": str(e)}), 500



@upload_bp.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)



@upload_bp.route("/share", methods=["POST"])
def share_report():
    try:
        data = request.json
        email = data.get("email")
        file_name = data.get("file")

        pdf_name = f"{file_name.split('.')[0]}_report.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_name)

        if not os.path.exists(pdf_path):
            return jsonify({"error": "Report not found"}), 400

        send_email(
            to_email=email,
            subject="Dental Report",
            body="Your dental report is attached.",
            attachment_path=pdf_path
        )

        return jsonify({"msg": "Email sent successfully"})

    except Exception as e:
        print("❌ Share Error:", str(e))
        return jsonify({"error": str(e)}), 500



@upload_bp.route("/history/<email>", methods=["GET"])
def history(email):
    try:
        data = list(reports.find({"email": email}, {"_id": 0}))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
