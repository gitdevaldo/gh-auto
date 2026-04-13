import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OTP_DIR = os.path.join(BASE_DIR, "otp")


def send_report(to_email, username, card_data, address, app_type):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_from = os.getenv("SMTP_FROM", smtp_user)

    if not all([smtp_host, smtp_user, smtp_pass]):
        print("\n  [ERROR] SMTP not configured — skipping email report\n")
        return False

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    name = card_data.get("name", "N/A")
    school = card_data.get("schoolName", "N/A")
    city = address.get("city", "N/A")
    state = address.get("state_province", "N/A")

    subject = f"GitHub Education — Application Submitted ({username})"

    body = f"""GitHub Education Application Report
{'='*45}

Status     : Submitted Successfully
Date       : {now}
Username   : {username}
Type       : {app_type}

Card Details
{'-'*45}
Name       : {name}
School     : {school}

Billing Address
{'-'*45}
City       : {city}
State      : {state}
Country    : Indonesia

{'='*45}
This is an automated report.
"""

    msg = MIMEMultipart()
    msg["From"] = smtp_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    secret_path = os.path.join(OTP_DIR, username, "secret.txt")
    recovery_path = os.path.join(OTP_DIR, username, "recovery_codes.txt")

    _attach_file(msg, secret_path, f"{username}_totp_secret.txt")
    _attach_file(msg, recovery_path, f"{username}_recovery_codes.txt")

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_from, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"\n  [ERROR] Failed to send email — {e}\n")
        return False


def _attach_file(msg, file_path, filename):
    if not os.path.exists(file_path):
        return

    with open(file_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())

    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={filename}")
    msg.attach(part)
