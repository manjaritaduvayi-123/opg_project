from flask import Blueprint, request, jsonify
from db import users
import bcrypt
import smtplib
from email.message import EmailMessage
import os
from predict import run_prediction

auth_bp = Blueprint("auth", __name__)

# -------------------------------
# 🔐 REGISTER
# -------------------------------
@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.json

    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ["name", "age", "email", "password"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    # normalize email (important fix)
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

    return jsonify({"msg": "User registered successfully"})


# -------------------------------
# 🔐 LOGIN (FIXED + DEBUG)
# -------------------------------
@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.json

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    print("Entered email:", email)
    print("Entered password:", password)

    user = users.find_one({"email": email})
    print("User from DB:", user)

    if not user:
        print("❌ User not found")
        return jsonify({"error": "User not found"}), 404

    print("Stored hash:", user["password"])

    result = bcrypt.checkpw(password.encode(), user["password"].encode())
    print("Password match:", result)

    if result:
        return jsonify({"msg": "Login success"})

    print("❌ Invalid password")
    return jsonify({"error": "Invalid credentials"}), 401


# -------------------------------
# 📧 EMAIL FUNCTION
# -------------------------------
def send_email(receiver_email, report_path):
    sender_email = "your_email@gmail.com"
    app_password = "your_app_password"  # ⚠️ App password only

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


# -------------------------------
# 📤 SEND REPORT ROUTE
# -------------------------------
@auth_bp.route("/send-report", methods=["POST"])
def send_report():
    data = request.json

    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email", "").strip()

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        print("Running prediction...")

        # 🔥 Run YOLO prediction
        output_image = run_prediction("test.jpg")

        print("Prediction saved at:", output_image)

        # 🔥 Send email
        send_email(email, output_image)
        print("Incoming data:", data)

        return jsonify({"msg": "Report sent successfully"})

    except Exception as e:
        print("Error in send_report:", e)
        return jsonify({"error": str(e)}), 500