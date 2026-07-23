import sqlite3
import os
from datetime import datetime
from email_service import send_email

print("Database Path:", os.path.abspath("database.db"))

def check_expiry_dates():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT document_name,
           expiry_date,
           email,
           reminder_days
    FROM documents
    """)

    documents = cursor.fetchall()

    print("Documents in database:", documents)

    today = datetime.today().date()

    for doc in documents:

        document_name = doc[0]
        expiry_date = datetime.strptime(doc[1], "%Y-%m-%d").date()
        email = doc[2]
        reminder_days = int(doc[3])

        days_left = (expiry_date - today).days

        print(f"{document_name} | Days Left: {days_left}")

        if days_left == reminder_days:

            send_email(
                email,
                document_name,
                expiry_date
            )

            print("Reminder mail sent:", document_name)

        else:
            print("No reminder:", document_name)

    conn.close()

check_expiry_dates()