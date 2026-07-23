from flask import Flask, render_template, request,redirect

import sqlite3
import os
import schedule
import time
import threading


from datetime import datetime
from datetime import datetime, timedelta

from email_service import send_email
import os
from dotenv import load_dotenv
from google import genai
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


app = Flask(__name__)
import os

print("=" * 50)
print("RUNNING FILE:", os.path.abspath(__file__))
print("=" * 50)

# -----------------------------
# Upload Folder
# -----------------------------
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



# -----------------------------
# Database
# -----------------------------
def init_db():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_name TEXT,
        document_number TEXT,
        expiry_date TEXT,
        email TEXT,
        file_name TEXT,
        reminder_days INTEGER,
        last_reminder_date TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()



# -----------------------------
# Home
# -----------------------------
@app.route('/')
def home():
    return render_template("home.html")

# -----------------------------
# Add Document
# -----------------------------
@app.route('/add_document')
def add_document():

    return render_template("add_document.html")



# -----------------------------
# Save Document
# -----------------------------
@app.route('/save_document', methods=['POST'])
def save_document():

    document_name = request.form['document_name']

    document_number = request.form['document_number']

    expiry_date = request.form['expiry_date']

    email = request.form['email']

    reminder_days = request.form['reminder_days']


    file = request.files['document_file']

    filename = ""


    if file and file.filename != "":

        filename = file.filename

        file.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )



    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()


    cursor.execute("""
    INSERT INTO documents
    (document_name,
     document_number,
     expiry_date,
     email,
     file_name,
     reminder_days)

    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        document_name,
        document_number,
        expiry_date,
        email,
        filename,
        reminder_days
    ))


    conn.commit()

    conn.close()



    return """
<!DOCTYPE html>
<html>
<head>

<title>Success</title>

<style>

body{
    margin:0;
    font-family:Arial,sans-serif;
    background:linear-gradient(135deg,#d6ecff,#eef8ff);
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
}

.card{
    background:white;
    width:500px;
    text-align:center;
    padding:40px;
    border-radius:20px;
    box-shadow:0 10px 30px rgba(0,0,0,0.2);
}

.icon{
    font-size:80px;
    color:#28a745;
}

h1{
    color:#1565c0;
    margin-top:15px;
}

h3{
    color:#555;
    font-weight:normal;
}

.info{
    background:#e8f5e9;
    color:#2e7d32;
    padding:15px;
    border-radius:10px;
    margin:25px 0;
    font-size:18px;
}

.buttons{
    margin-top:30px;
}

.btn{
    display:inline-block;
    text-decoration:none;
    color:white;
    background:#1565c0;
    padding:12px 28px;
    border-radius:30px;
    margin:10px;
    font-weight:bold;
    transition:.3s;
}

.btn:hover{
    background:#0d47a1;
}

.btn2{
    background:#43a047;
}

.btn2:hover{
    background:#2e7d32;
}

</style>

</head>

<body>

<div class="card">

<div class="icon">✅</div>

<h1>Document Saved Successfully!</h1>

<h3>Your document has been stored securely.</h3>

<div class="info">

📧 AI Reminder Activated Successfully

<br><br>

You'll receive reminder emails before the expiry date.

</div>

<div class="buttons">

<a href="/" class="btn">🏠 Home</a>

<a href="/view_documents" class="btn btn2">📂 View Documents</a>

</div>

</div>

</body>

</html>
"""



# -----------------------------
# View Documents
# -----------------------------
@app.route('/view_documents')
def view_documents():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM documents")

    documents = cursor.fetchall()

    conn.close()


    return render_template(
        "view_documents.html",
        documents=documents
    )

@app.route('/delete/<int:id>')
def delete_document(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM documents WHERE id=?", (id,))
    conn.commit()

    conn.close()

    return redirect('/view_documents')


#--------------------
#Document status
#---------------------

@app.route("/document_status")
def document_status():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT document_name, expiry_date 
        FROM documents
    """)

    documents = cursor.fetchall()

    conn.close()


    today = datetime.today().date()

    active = 0
    expiring = 0
    expired = 0


    for doc in documents:

        expiry_date = datetime.strptime(
            doc[1],
            "%Y-%m-%d"
        ).date()


        if expiry_date < today:
            expired += 1

        elif expiry_date <= today + timedelta(days=30):
            expiring += 1

        else:
            active += 1


    return render_template(
        "document_status.html",
        active=active,
        expiring=expiring,
        expired=expired
    )


# -----------------------------
# AI Assistant
# -----------------------------
@app.route('/ai_assistant')
def ai_assistant():
    return render_template("ai_assistant.html")


@app.route('/ask_ai', methods=['POST'])
def ask_ai():

    question = request.form["question"].lower()

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Documents expiring soon
    if "expire soon" in question or "expiring" in question:

        cursor.execute("""
            SELECT document_name, expiry_date
            FROM documents
            WHERE date(expiry_date) <= date('now','+30 day')
            ORDER BY expiry_date
        """)

        docs = cursor.fetchall()

        if docs:

            answer = "📅 Documents Expiring Soon:\n\n"

            for doc in docs:
                answer += f"📄 {doc[0]} - Expiry Date: {doc[1]}\n"

        else:

            answer = "✅ No documents are expiring within the next 30 days."

    # Show saved documents
    elif "show my documents" in question or "my documents" in question:

        cursor.execute("""
            SELECT document_name, expiry_date
            FROM documents
            ORDER BY expiry_date
        """)

        docs = cursor.fetchall()

        if docs:

            answer = "📂 Your Saved Documents:\n\n"

            for doc in docs:
                answer += f"📄 {doc[0]} - Expiry Date: {doc[1]}\n"

        else:

            answer = "No documents found."

    # Greetings
    elif question in ["hi", "hello", "hey"]:

        answer = """
Hello 👋

I am your AI Document Renewal Assistant.

I can help you with:

• Show my documents
• Documents expiring soon
• Renewal guidance
• General AI questions
"""

    # Renewal Help
    elif "renew" in question:

        answer = """
Steps to renew a document:

1. Check the expiry date.
2. Visit the official renewal website.
3. Upload the required documents.
4. Complete the payment.
5. Download and save the renewed document.
"""

    # General AI Questions using Gemini
    else:

        try:

            prompt = f"""
You are a friendly AI Assistant for a Personal Document Renewal Reminder System.

You can answer:
- General knowledge
- Artificial Intelligence
- Python
- Flask
- Machine Learning
- Technology
- Education
- Passport
- Aadhaar
- PAN Card
- Driving License
- Insurance
- Document renewal

Give short, clear, and helpful answers.

User Question:
{question}
"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            answer = response.text

        except Exception as e:

            answer = f"AI Error: {str(e)}"

    conn.close()

    return render_template(
        "ai_assistant.html",
        question=question,
        answer=answer
    )
# -----------------------------
# Daily AI Expiry Checker
# -----------------------------
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
        expiry_date = datetime.strptime(
            doc[2],
            "%Y-%m-%d"
        ).date()

        email = doc[3]
        reminder_days = int(doc[4])
        last_reminder_date = doc[5]

        days_left = (expiry_date - today).days

        print(f"{document_name} | Days Left: {days_left}")

        # Send only one reminder per day
        if days_left == reminder_days and last_reminder_date != str(today):

            send_email(
                email,
                document_name,
                expiry_date
            )

            cursor.execute("""
            UPDATE documents
            SET last_reminder_date = ?
            WHERE id = ?
            """, (str(today), doc_id))

            conn.commit()

            print("✅ Reminder mail sent:", document_name)

        else:

            print("❌ No reminder:", document_name)

    conn.close()



# Check every day at 9 AM
# Run every minute
schedule.every(1).minutes.do(check_expiry_dates)

def run_scheduler():

    while True:

        schedule.run_pending()

        time.sleep(1)


if __name__ == "__main__":

    scheduler_thread = threading.Thread(
        target=run_scheduler,
        daemon=True
    )

    scheduler_thread.start()

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )