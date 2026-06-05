from flask_mail import Message
import os


def send_email(
    to_email,
    subject,
    body,
    attachment_path=None
):
    try:
        from app import mail

        msg = Message(
            subject=subject,
            sender="yuki25082008@gmail.com",
            recipients=[to_email]
        )

        msg.body = body

        if attachment_path:

            if not os.path.exists(attachment_path):
                raise Exception(
                    f"Attachment not found: {attachment_path}"
                )

            with open(
                attachment_path,
                "rb"
            ) as f:

                msg.attach(
                    filename=os.path.basename(
                        attachment_path
                    ),
                    content_type="application/pdf",
                    data=f.read()
                )

        mail.send(msg)

        print(
            f"Email sent successfully to {to_email}"
        )

        return True

    except Exception as e:

        print(
            "EMAIL ERROR:",
            str(e)
        )

        raise e