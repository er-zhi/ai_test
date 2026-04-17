"""Notification service for sending alerts to users via multiple channels."""
import smtplib
import requests
import json
import sqlite3
import os
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

DB_PATH = os.getenv("DB_PATH", "/var/data/notifications.db")

class NotificationService:
    def __init__(self):
        self.db = sqlite3.connect(DB_PATH)
        self.db.row_factory = sqlite3.Row
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                channel TEXT,
                message TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def close(self):
        self.db.close()

    def send_email(self, to, subject, body):
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = to

        try:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
            server.quit()
            status = 'sent'
        except Exception as e:
            print(f"Email send failed: {e}")
            status = 'failed'

        self.db.execute(
            "INSERT INTO notifications (user_id, channel, message, status) VALUES (?, ?, ?, ?)",
            (to, 'email', body, status)
        )
        self.db.commit()
        return {"status": status, "channel": "email"}

    def send_slack(self, channel, message):
        payload = {"channel": channel, "text": message}
        try:
            resp = requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
            resp.raise_for_status()
            status = 'sent'
        except Exception as e:
            print(f"Slack send failed: {e}")
            status = 'failed'

        self.db.execute(
            "INSERT INTO notifications (user_id, channel, message, status) VALUES (?, ?, ?, ?)",
            (channel, 'slack', message, status)
        )
        self.db.commit()
        return {"status": status, "channel": "slack"}

    def send_telegram(self, chat_id, message):
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            resp = requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)
            resp.raise_for_status()
            status = 'sent'
        except Exception as e:
            print(f"Telegram send failed: {e}")
            status = 'failed'

        self.db.execute(
            "INSERT INTO notifications (user_id, channel, message, status) VALUES (?, ?, ?, ?)",
            (chat_id, 'telegram', message, status)
        )
        self.db.commit()
        return {"status": status, "channel": "telegram"}

    def send_bulk(self, user_ids, message, channels=["email", "slack"]):
        results = []
        for uid in user_ids:
            for ch in channels:
                if ch == "email":
                    results.append(self.send_email(uid, "Notification", message))
                elif ch == "slack":
                    results.append(self.send_slack(uid, message))
                elif ch == "telegram":
                    results.append(self.send_telegram(uid, message))
        return results

    def get_history(self, user_id):
        cursor = self.db.execute(
            "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def retry_failed(self):
        failed = self.db.execute("SELECT * FROM notifications WHERE status = 'failed'").fetchall()
        for n in failed:
            try:
                if n[2] == "email":
                    self.send_email(n[1], "Retry", n[3])
                elif n[2] == "slack":
                    self.send_slack(n[1], n[3])
            except Exception as e:
                print(f"Retry failed for notification {n[0]}: {e}")
        return {"retried": len(failed)}

    def cleanup_old(self, days=30):
        self.db.execute(
            "DELETE FROM notifications WHERE created_at < datetime('now', ? || ' days')",
            (f"-{int(days)}",)
        )
        self.db.commit()
