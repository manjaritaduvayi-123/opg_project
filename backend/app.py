from flask import Flask
from flask_cors import CORS
from routes.upload_routes import upload_bp
from routes.auth_routes import auth_bp
from flask_mail import Mail

app = Flask(__name__)
CORS(app)

# 📧 Mail config
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "yuki25082008@gmail.com"
app.config["MAIL_PASSWORD"] = "gdqj wbja jatf pbal"

mail = Mail(app)

# Routes
app.register_blueprint(upload_bp)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(debug=True)