

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# This needs a relative import to work correctly when run as a module
from backend.config import Config

class Alerter:

    def __init__(self):
        self.config = Config()
        # Check if all necessary SMTP settings are present in the .env file
        if not all([self.config.SMTP_SERVER, self.config.SMTP_PORT, self.config.SMTP_USER, self.config.SMTP_PASSWORD, self.config.ALERT_RECIPIENT_EMAIL]):
            print("SMTP configuration is incomplete. Alerts will be printed to console instead of being emailed.")
            self.email_enabled = False
        else:
            self.email_enabled = True

    def send_alert(self, subject: str, body: str):
        print("\n--- ALERT TRIGGERED ---")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        print("-----------------------\n")

        if not self.email_enabled:
            return

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = self.config.SMTP_USER
        msg['To'] = self.config.ALERT_RECIPIENT_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            # Connect to the SMTP server and send the email
            with smtplib.SMTP(self.config.SMTP_SERVER, int(self.config.SMTP_PORT)) as server:
                server.starttls()  # Secure the connection
                server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
                server.send_message(msg)
                print("Successfully sent email alert.")
        except Exception as e:
            print(f"Failed to send email alert: {e}")

