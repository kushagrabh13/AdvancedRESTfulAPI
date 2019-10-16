import os
from typing import List
from requests import Response, post

class MailGunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class MailGun:
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_URL', None)
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY', None)

    FROM_TITLE = "Stores REST API"
    FROM_EMAIL = f"do-not-reply@{MAILGUN_DOMAIN}"

    @classmethod
    def send_email(cls, email: List[str], subject: str, text: str, html: str) -> Response:
        if cls.MAILGUN_API_KEY is None:
            raise MailGunException("Failed to load MailGun API Key")

        if cls.MAILGUN_DOMAIN is None:
            raise MailGunException("Failed to load MailGun domain")

        response = post(f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
                        auth=("api", cls.MAILGUN_API_KEY),
                        data={
                            "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                            "to": email,
                            "subject": subject,
                            "text": html
                        },
                        )

        if response.status_code != 200:
            raise MailGunException("Error in sending confirmation email.")

        return response