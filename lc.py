import requests
import datetime
import smtplib
from email.mime.text import MIMEText
import os

# ========== CONFIG ==========


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
LEETCODE_USERNAME = os.getenv("LEETCODE_USERNAME")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")


# ============================

def solved_today():
    today = datetime.datetime.utcnow().date()

    url = "https://leetcode.com/graphql"
    payload = {
        "query": """
        query recentSubmissions($username: String!) {
          recentSubmissionList(username: $username, limit: 20) {
            timestamp
            statusDisplay
          }
        }
        """,
        "variables": {"username": LEETCODE_USERNAME}
    }

    r = requests.post(url, json=payload)
    data = r.json()

    submissions = data["data"]["recentSubmissionList"]
    print(submissions)

    for s in submissions:
        if s["statusDisplay"] == "Accepted":
            sub_date = datetime.datetime.utcfromtimestamp(
                int(s["timestamp"])
            ).date()
            if sub_date == today:
                return True

    return False

def send_email():
    msg = MIMEText(
        "⚠️ You have NOT solved any LeetCode problem today.\n\n"
        "Your streak is at risk. Solve one NOW!"
    )
    msg["Subject"] = "⚠️ LeetCode streak reminder"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    }
    requests.post(url, json=payload)


if __name__ == "__main__":
    now = datetime.datetime.now().hour

    if not solved_today():
        send_email()

        if now >= 12:  # after 12 PM
            send_telegram(
                "🚨 LEETCODE ALERT 🚨\n\n"
                "You have NOT solved a problem today.\n"
                "Your streak is at risk.\n\n"
                "DO ONE NOW."
            )

