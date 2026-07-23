import smtplib
from email.mime.text import MIMEText

SENDER_EMAIL = "natarajanitha001@gmail.com"
APP_PASSWORD = "eocx ffib frfm jywd"

def send_email(receiver_email, document_name, expiry_date):

    subject = "Document Renewal Reminder"

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

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(SENDER_EMAIL, APP_PASSWORD)

    server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())

    server.quit()

    print("Email Sent Successfully")