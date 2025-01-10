import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

def send_emails(csv_file, html_file, sender_email, sender_password, subject=""):
    df = pd.read_csv(csv_file)
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        for _, row in df.iterrows():
            recipient_email = row['Email']
            name = row.get('Name', 'User')
            personalized_html = html_content.replace("{name}", name)
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            # Attach the HTML content
            msg.attach(MIMEText(personalized_html, 'html'))
            try:
                server.sendmail(sender_email, recipient_email, msg.as_string())
                print(f"Email sent to {recipient_email}")
            except Exception as e:
                print(f"Failed to send email to {recipient_email}: {e}")

send_emails(
    csv_file="emails.csv",  # Updated to use a CSV file
    html_file="Template.html",  # The HTML file for the email template
    sender_email="",  # Your email
    sender_password="",  # Your app password
    subject="Selection at Full Stack Web Snacks"  # Custom subject line
)
