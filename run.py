from app import app as application
from db import db
from marsh import io
from oauth import oauth

db.init_app(application)
io.init_app(application)
oauth.init_app(application)

@application.before_first_request
def create_tables():
        db.create_all()

