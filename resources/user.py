from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
        create_access_token,
        create_refresh_token,
        jwt_refresh_token_required,
        get_jwt_identity,
        jet_required,
        get_raw_jwt
)

from models.user import UserModel
from blacklist import BLACKLIST


BLANK_ERROR = "'{}' cannot be left blank!"

_user_parser = reqparse.RequestParser()
    
_user_parser.add_argument('username',
    type=str,
    required=True,
    help='BLANK_ERROR.format('Username')'
)

_user_parser.add_argument('password',
    type=str,
    required=True,
    help='BLANK_ERROR.format('Password')'
)

class UserRegister(Resource):
    @classmethod
    def post(cls):
        data = UserRegister.parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': 'A user with that username already exists'}, 400

        user = UserModel(data['username'], data['password'])
        user.save_to_db()

        return {'message': 'User created successfully.'}, 201

class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User Not Found"}, 404
        return user.json(), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            returm {"message": "User Not Found"}, 404
        user.delete_from_db()
        return {"message": "User Deleted!"}, 200

class UserLogin(Resource):
    def post(self):
        data = _user_parser.parse_args()

        user = UserModel.find_by_username(data["Username"])

        if user and safe_str_cmp(user.password, data["password"]):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token" : access_token, "refresh_token": refresh_token}, 200

        return {"message": "Invalid Credentials!"}, 401

class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"] # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": "User {} Logged Out".format(user_id)}, 200

class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
