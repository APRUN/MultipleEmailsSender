import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import streamlit as st

def send_emails(df, email_content, is_html, sender_email, sender_password, subject=""):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            try:
                server.login(sender_email, sender_password)
            except smtplib.SMTPAuthenticationError:
                st.error("Authentication failed. Please check your email or app password.")
                return
            except Exception as e:
                st.error(f"Failed to log in to SMTP server: {e}")
                return

            for _, row in df.iterrows():
                recipient_email = row.get('Email', '').strip()
                if not recipient_email:
                    st.warning(f"Skipping row with missing email: {row}")
                    continue  # Skip rows with empty email addresses

                name = row.get('Name', 'User')

                # Personalize the email if a placeholder is present
                personalized_content = email_content.replace("{name}", name)

                # Create email
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient_email
                msg['Subject'] = subject

                # Attach the email content (HTML or plain text)
                if is_html:
                    msg.attach(MIMEText(personalized_content, 'html'))
                else:
                    msg.attach(MIMEText(personalized_content, 'plain'))

                try:
                    server.sendmail(sender_email, recipient_email, msg.as_string())
                    st.success(f"Email sent to {recipient_email}")
                except Exception as e:
                    st.error(f"Failed to send email to {recipient_email}: {e}")

    except smtplib.SMTPException as e:
        st.error(f"SMTP error: {e}")
    except Exception as e:
        st.error(f"Unexpected error while sending emails: {e}")

# Streamlit UI
st.title("Bulk Email Sender")

try:
    csv_file = st.file_uploader("Upload your CSV file (must contain 'Email' column)", type=["csv", "xlsx", "xls"])

    # Manage visibility of HTML uploader based on text input
    email_text = st.text_area("Or enter email body (if no HTML file provided)", "")
    html_file = None if email_text.strip() else st.file_uploader("Upload HTML Email Template (optional if using text)", type=["html"])

    sender_email = st.text_input("Your Email", "", type="default")
    sender_password = st.text_input("Your App Password", "", type="password")
    subject = st.text_input("Email Subject", "Selection at Full Stack Web Snacks")

    if st.button("Send Emails"):
        if csv_file and (html_file or email_text.strip()) and sender_email and sender_password:
            try:
                # Read CSV or Excel file
                if csv_file.name.endswith('.csv'):
                    df = pd.read_csv(csv_file)
                else:
                    df = pd.read_excel(csv_file)

                # Validate DataFrame
                if 'Email' not in df.columns:
                    st.error("Uploaded file must contain an 'Email' column.")
                    st.stop()

                # Determine email content
                if html_file:
                    try:
                        email_content = html_file.getvalue().decode("utf-8")
                        is_html = True
                    except Exception as e:
                        st.error(f"Failed to read HTML file: {e}")
                        st.stop()
                else:
                    email_content = email_text.strip()
                    is_html = False

                send_emails(df, email_content, is_html, sender_email, sender_password, subject)

            except pd.errors.EmptyDataError:
                st.error("Uploaded CSV/Excel file is empty.")
            except pd.errors.ParserError:
                st.error("Failed to parse the uploaded CSV/Excel file. Please check the file format.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
        else:
            st.warning("Please upload a CSV file and either an HTML template or enter email text.")

except Exception as e:
    st.error(f"Critical error: {e}")
