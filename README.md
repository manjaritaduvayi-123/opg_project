🦷 Dental AI – Automated OPG Scan Analysis System

📌 Overview

This project presents an automated system for analyzing Orthopantomogram (OPG) dental X-ray images using deep learning. The system allows users to upload dental images, detects key dental conditions, and generates a visual output highlighting affected regions. Users can also share the analyzed report via email.


🚀 Features

* 📤 Upload dental X-ray (OPG) images
* 🔍 Detect dental conditions using YOLO model
* 🧠 Supports multiple classes (currently 5, expandable)
* 🖼️ Visual output with bounding boxes
* 📧 Share report via email
* 🔐 User authentication (Login/Register)
* 📊 History of uploaded reports

🏷️ Detected Classes (Current)

* Caries
* Crown
* Missing Teeth
* Root Canal Treatment
* Impacted Tooth

👉 The system is designed to scale to more classes in future.

---

🛠️ Tech Stack

🔹 Frontend

* React.js
* Axios

🔹 Backend

* Flask
* Python

🔹 Machine Learning

* YOLOv8 (Ultralytics)

🔹 Database

* MongoDB

🔹 Other Tools

* OpenCV
* SMTP (Email Service)

📂 Project Structure

opg_project/
│
├── backend/
│   ├── app.py
│   ├── auth_routes.py
│   ├── predict.py
│   ├── db.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.js
│   │   │   ├── Register.js
│   │   │   └── Dashboard.js
│   │   └── App.js
│
├── train_model.py
├── test_model.py
├── dataset.yaml
└── README.md

⚙️ How to Run the Project

🔹 Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```
🔹 Frontend Setup
```bash
cd frontend
npm install
npm start
```
📧 Email Feature Setup
* Enable **App Password** in Gmail
* Replace credentials in backend:
python
sender_email = "your_email@gmail.com"
app_password = "your_app_password"

📸 Working Flow
1. User logs in
2. Uploads dental image
3. Model detects abnormalities
4. Result displayed on dashboard
5. User enters email
6. Report is sent via email

🔮 Future Enhancements

* Increase number of detectable classes
* Improve model accuracy
* Deploy system on cloud
* Real-time image processing
* Direct mouth image capture using camera
* Integration with advanced AI models
⚠️ Note

* Dataset is not included in this repository due to size constraints
* Model weights may be stored separately

👩‍💻 Author

Manjari Taduvayi

⭐ Acknowledgement

This project was developed as part of academic work in Computer Science Engineering with a focus on Data Science.
