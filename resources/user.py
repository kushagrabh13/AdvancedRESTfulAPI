from flask_restful import Resource
from flask import request
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
        create_access_token,
        create_refresh_token,
        jwt_refresh_token_required,
        get_jwt_identity,
        jwt_required,
        get_raw_jwt
)

from models.user import UserModel
from schemas.user import UserSchema
from blacklist import BLACKLIST
from libs.mailgun import MailGunException
from models.confirmation import ConfirmationModel

userSchema = UserSchema()

class UserRegister(Resource):
    @classmethod
    def post(cls):
        userJSON = request.get_json()
        user = userSchema.load(userJSON, partial=("email", ))

        if UserModel.find_by_username(user.username):
            return {'message': 'A user with that username already exists'}, 400

        if UserModel.find_by_email(user.email):
            return {'message': 'A user with that email already exists'}, 400

        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
        except MailGunException as e:
            user.delete_from_db()
            return {"message": str(e)}, 500
        except Exception as e:
            print(e)
            user.delete_from_db()
            return {"message": "Failed to create user"}, 500

        return {'message': 'User created successfully.'}, 201

class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User Not Found"}, 404
        return userSchema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User Not Found"}, 404
        user.delete_from_db()
        return {"message": "User Deleted!"}, 200

class UserLogin(Resource):
    def post(self):
        userJSON = request.get_json()
        userData = userSchema.load(userJSON, partial=("email",))

        user = UserModel.find_by_username(userData.username)

        if user and safe_str_cmp(userData.password, user.password):
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token" : access_token, "refresh_token": refresh_token}, 200
            return {"message": "Account not confirmed. Please check your email"}

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
