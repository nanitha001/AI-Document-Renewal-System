import smtplib
from email.mime.text import MIMEText

SENDER_EMAIL = "natarajanitha001@gmail.com"
APP_PASSWORD = "thiy eoye pyde gwil"


def send_email(receiver_email, document_name, expiry_date):

    subject = f"Reminder: {document_name} expires on {expiry_date}"

    body = f"""
Hello,

This is a reminder that your document

Document Name : {document_name}

will expire on {expiry_date}.

Please renew it before the expiry date.

Thank You.
"""

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(
            SENDER_EMAIL,
            receiver_email,
            msg.as_string()
        )

    print(f"Email Sent Successfully -> {document_name}")
