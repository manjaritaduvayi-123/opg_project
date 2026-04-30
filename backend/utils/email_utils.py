from flask_mail import Message

def send_email(to_email, subject, body, attachment_path=None):
    from app import mail   # avoid circular import

    msg = Message(
        subject=subject,
        sender="yuki25082008@gmail.com",
        recipients=[to_email]
    )

    msg.body = body

    # 📎 Attach PDF
    if attachment_path:
        with open(attachment_path, "rb") as f:
            msg.attach(
                attachment_path,
                "application/pdf",
                f.read()
            )

    mail.send(msg)