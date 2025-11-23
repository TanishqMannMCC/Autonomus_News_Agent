import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 1. Import core functions
try:
    from main import fetch_news_articles, get_summary, GEMINI_INITIALIZED
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import from main.py. {e}")
    exit()

CONFIG_FILE = 'users_config.json'

# --- EMAIL CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com" # Example for Gmail
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return []

def send_email(to_email, subject, body):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("Skipping email: SENDER_EMAIL or SENDER_PASSWORD not set.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, to_email, text)
        server.quit()
        print(f"  -> Email sent successfully to {to_email}")
    except Exception as e:
        print(f"  -> Failed to send email: {e}")

def format_news_for_email(topic, articles):
    """Creates a clean text body for the email."""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    body = f"Here is your autonomous news briefing for {timestamp}.\n\n"
    body += f"TOPIC: {topic}\n"
    body += "="*30 + "\n\n"

    if not articles:
        body += "No new articles found today.\n"
        return body

    for i, article in enumerate(articles):
        title = article.get('title', 'No Title')
        source = article.get('source', {}).get('name', 'Unknown')
        url = article.get('url', '#')
        desc = article.get('description')
        summary = get_summary(desc)

        body += f"{i+1}. {title}\n"
        body += f"   Source: {source}\n"
        body += f"   Summary: {summary}\n"
        body += f"   Link: {url}\n\n"
        body += "-"*30 + "\n\n"
    
    return body

def run_agent_job():
    print(f"\n--- Starting Scheduled Agent Run at {datetime.now()} ---")
    
    if not GEMINI_INITIALIZED:
        print("Error: Gemini model not initialized.")
        return

    users = load_config()
    for user in users:
        user_id = user.get('user_id')
        topic = user.get('topic')
        email = user.get('email')

        print(f"Processing task for: {user_id} (Topic: {topic})...")

        result = fetch_news_articles(topic)

        if result['status'] == 'ok':
            articles = result.get('articles', [])
            # Format email body
            email_body = format_news_for_email(topic, articles)
            # Send email if address exists
            if email:
                send_email(email, f"Daily News: {topic}", email_body)
            else:
                print("  -> No email address configured for this user.")
                
            # You can still log to file if you want (omitted here for brevity)
        else:
            print(f"  -> API Error: {result.get('message')}")

    print("--- Run Complete ---\n")

if __name__ == "__main__":
    run_agent_job()