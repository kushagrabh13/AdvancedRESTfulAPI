from time import time

from flask_restful import Resource
from flask import make_response, render_template

from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema

confirmationSchema = ConfirmationSchema()

class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        """ Returns confirmation HTML Page """
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": "Confirmation reference not found."}, 404

        if confirmation.expired:
            return {"message": "The link has expired."}, 400

        if confirmation.confirmed:
            return {"message": "Registration has already been confirmed."}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_page.html", email=confirmation.user.email),
            200,
            headers
        )

class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        """ Returns confirmations for a given User. Only for testing"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User Not Found"}, 404

        return (
            {
                "current_time": int(time()),
                "confirmation": [
                    confirmationSchema.dump(each) for each in user.confirmation.order_by(ConfirmationModel.expire_at)
                ],
            },
            200,
        )

    @classmethod
    def post(cls, user_id: int):
        """ Resend Confirmation Email"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User Not Found."}, 404

        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": "Registration has already been confirmed."}, 400
                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": "Resend Successful"}, 201
        except MailGunException as e:
            return {"message": str(e)}, 500
        except Exception as e:
            print(e)
            return {"message": "Resend Failed"}, 500