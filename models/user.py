import os
from flask import request, url_for
from requests import Response, post
from db import db

MAILGUN_DOMAIN = os.environ.get('MAILGUN_URL', None)
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY', None)
FROM_TITLE = "Stores REST API"
FROM_EMAIL = "mailgun@sandbox7dfd478dafba4b4393d07c69afdc2cc4.mailgun.org"

class MailGunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        
class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    activated = db.Column(db.Boolean, default=False)

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username = username).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id = _id).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email = email).first()

    def send_confirmation_email(self) -> Response:
        if MAILGUN_API_KEY is None:
            raise MailGunException("Failed to load MailGun API Key")

        if MAILGUN_DOMAIN is None:
            raise MailGunException("Failed to load MailGun domain")

        link = request.url_root[:-1] + url_for("userconfirm", user_id=self.id)
        response = post(f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
		    auth=("api", MAILGUN_API_KEY),
		    data={
                            "from": f"{FROM_TITLE} <{FROM_EMAIL}>",
			    "to": self.email,
			    "subject": "Registration Conformation",
			    "text": f"Please click the link to confirm your registration: {link}"
            },
        )

        if response.status_code != 200:
            raise MailGunException("Error in sending confirmation email.")

        return response

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
