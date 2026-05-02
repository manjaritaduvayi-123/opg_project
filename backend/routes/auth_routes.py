from flask import Blueprint, request, jsonify
from db import users
import bcrypt
import smtplib
from email.message import EmailMessage
import os

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.json

    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ["name", "age", "email", "password"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    email = data["email"].strip().lower()

    if users.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    hashed_pw = bcrypt.hashpw(
        data["password"].encode(), bcrypt.gensalt()
    ).decode("utf-8")

    users.insert_one({
        "name": data["name"],
        "age": data["age"],
        "email": email,
        "password": hashed_pw
    })

    print("✅ User registered:", email)
    return jsonify({"msg": "User registered successfully"})

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.json

    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    print("🔐 Login attempt:", email)

    user = users.find_one({"email": email})

    if not user:
        print("❌ User not found")
        return jsonify({"error": "User not found"}), 404

    try:
        if bcrypt.checkpw(password.encode(), user["password"].encode()):
            print("✅ Login success")
            return jsonify({"msg": "Login success"})
        else:
            print("❌ Invalid password")
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        print("Login error:", e)
        return jsonify({"error": "Login failed"}), 500
def send_email(receiver_email, report_path):
    sender_email = "taduvayi.manjari@gmail.com"
    app_password = "YOUR_APP_PASSWORD"   # 🔥 replace with Gmail App Password

    msg = EmailMessage()
    msg['Subject'] = 'OPG Dental Report'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content("Your OPG report is attached.")

    if not os.path.exists(report_path):
        raise Exception(f"Report file not found at {report_path}")

    with open(report_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="image",
            subtype="jpeg",
            filename=os.path.basename(report_path)
        )

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(msg)

    print("📧 Email sent to:", receiver_email)


@auth_bp.route("/share", methods=["POST"])
def share_report():
    data = request.json
    print("🔥 Incoming data:", data)

    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email", "").strip()
    image_path = data.get("image_path")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    if not image_path:
        return jsonify({"error": "Image path missing"}), 400

    try:
        # ✅ FIX: convert to absolute path
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(BASE_DIR, "..", image_path)
        full_path = os.path.abspath(full_path)

        print("📂 Full path:", full_path)

        if not os.path.exists(full_path):
            return jsonify({"error": f"File not found: {full_path}"}), 400

        send_email(email, full_path)

        return jsonify({"msg": "Report sent successfully"})

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500
