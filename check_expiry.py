import sqlite3
from datetime import datetime
from email_reminder import send_email


def check_expiry_dates():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id,
           document_name,
           expiry_date,
           email,
           reminder_days,
           last_reminder_date
    FROM documents
    """)

    documents = cursor.fetchall()

    today = datetime.today().date()

    print("Checking expiry dates...")

    for doc in documents:

        doc_id = doc[0]
        document_name = doc[1]
        expiry_date = datetime.strptime(doc[2], "%Y-%m-%d").date()
        email = doc[3]
        reminder_days = doc[4]
        last_reminder_date = doc[5]
        
        days_left = (expiry_date - today).days

        print(f"{document_name} | Days Left: {days_left} | Reminder Days: {reminder_days}")

        # Mail based on reminder days
        if days_left <= reminder_days and days_left >= 0:

            if last_reminder_date != str(today):

                print("Sending email:", document_name)

                send_email(
                    email,
                    document_name,
                    str(expiry_date)
                )


                cursor.execute("""
                UPDATE documents
                SET last_reminder_date = ?
                WHERE id = ?
                """, (str(today), doc_id))


                conn.commit()

                print("✅ Reminder sent")

            else:
                print("⚠️ Already sent today")


        else:
            print("❌ No reminder")


    conn.close()



if __name__ == "__main__":
    check_expiry_dates()
