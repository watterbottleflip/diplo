import smtplib
from email.mime.text import MIMEText
import os
from utils import get_participant


def send_email(subject_id, message):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")

    if not sender or not password:
        return "Sender email or password is not set."

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)

        participant = get_participant(subject_id)
        if participant:
            recipient = participant.contact
        else:
            return "Неправильный id пользователя"

        fixed_msg = MIMEText(message)
        fixed_msg["Subject"] = "Important Message"
        fixed_msg["From"] = sender
        fixed_msg["To"] = recipient

        server.sendmail(sender, recipient, fixed_msg.as_string())

        return "The message was sent successfully!"

    except smtplib.SMTPException as ex:
        return f"{ex}\nCheck your login or password please"

    finally:
        server.quit()
