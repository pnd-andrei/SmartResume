import os
import smtplib
import ssl
from email.mime.text import MIMEText

from dotenv import load_dotenv


class Mailer:
    def __init__(self):
        load_dotenv()

        self.__mail_adress = os.environ.get("smtp_user")
        self.__port = 465  # For SSL
        self.__password = os.environ.get("smtp_password")

        # Create a secure SSL context
        self.__context = ssl.create_default_context()

        self.__server = smtplib.SMTP_SSL(
            "smtp.gmail.com", self.__port, context=self.__context
        )

        self.__server.login(self.__mail_adress, self.__password)

    def send_email(self, recipient, subject, body):
        try:
            # Composing the email
            email_message = MIMEText(body)
            email_message["Subject"] = subject
            email_message["From"] = self.__mail_adress
            email_message["To"] = recipient  # Replace with recipient's email address

            self.__server.sendmail(
                self.__mail_adress, recipient, email_message.as_string()
            )
            print("Email sent successfully!\n")
        except Exception as exc:
            print(f"Failed to send email: {exc}")
        finally:
            self.__server.quit()


def send_verification_mail(mail, temporary_url):
    mail_agent = Mailer()
    mail_agent.send_email(
        mail,
        "Verification mail - ResumeCentral",
        f"http://localhost:8000/validate/{temporary_url}",
    )
