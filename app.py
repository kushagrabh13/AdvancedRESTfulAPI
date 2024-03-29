from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_uploads import configure_uploads, patch_request_class
from marshmallow import ValidationError
from dotenv import load_dotenv

load_dotenv('.env', verbose=True)

from marsh import io
from blacklist import BLACKLIST
from resources.user import User,UserRegister, UserLogin, UserLogout, TokenRefresh, UserList
from resources.github_login import GithubLogin, GithubAuthorize
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.image import ImageUpload, Image, AvatarUpload, Avatar
from resources.order import Order, OrderList
from libs.image_helper import IMAGE_SET
from oauth import oauth

app = Flask(__name__)

app.config.from_object("default_config")
app.config.from_envvar("APPLICATION_SETTINGS")
patch_request_class(app, 10 * 1024 * 1024) # 10MB Max Upload Size
configure_uploads(app, IMAGE_SET)

api = Api(app)

jwt = JWTManager(app)

@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist_loader(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST


api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')
api.add_resource(UserList, '/users')
api.add_resource(Confirmation, '/user_confirmation/<string:confirmation_id>')
api.add_resource(ConfirmationByUser, '/confirmation/user/<int:user_id>')
api.add_resource(ImageUpload, '/upload/image')
api.add_resource(Image, '/image/<string:filename>')
api.add_resource(AvatarUpload, '/upload/avatar')
api.add_resource(Avatar, '/avatar/<int:user_id>')
api.add_resource(GithubLogin, '/login/github')
api.add_resource(GithubAuthorize, '/login/github/authorized', endpoint="github.authorize")
api.add_resource(Order, '/order')
api.add_resource(OrderList, '/orders')

if __name__ == "__main__":
    from db import db
    db.init_app(app)
    io.init_app(app)
    oauth.init_app(app)

    if app.config['DEBUG']:
        @app.before_first_request
        def create_tables():
            db.create_all()

    app.run(host='0.0.0.0')

