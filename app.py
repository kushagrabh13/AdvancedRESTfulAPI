from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from blacklist import BLACKLIST
from resources.user import User,UserRegister, UserLogin, UserLogout, TokenRefresh
from resources.item import Item, ItemList
from resources.store import Store, StoreList

import os


app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True #Enable Blacklist Feature
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = [
	"access",
	"refresh"
] #allow blacklisting for access and refresh tokens
app.secret_key = 'doe' # can be used as app.config['JWT_SECRET_KEY']
api = Api(app)

jwt = JWTManager(app)

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist_loader(decryted_token):
	return decryted_token['jti'] in BLACKLIST


api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')

if __name__ == "__main__":
    from db import db
    db.init_app(app)
    
    if app.config['DEBUG']:
    	@app.before_first_request
    	def create_tables():
    	    db.create_all()

    app.run(host='0.0.0.0')

