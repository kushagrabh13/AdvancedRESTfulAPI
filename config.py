""" Production Configuration"""
DEBUG = False

SQLALCHEMY_DATABASE_URI = os.environ('DATABASE_URL', 'sqlite:///data.db')