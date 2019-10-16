import os
from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from libs import image_helper
from schemas.image import ImageSchema

imageSchema = ImageSchema()

class ImageUpload(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        """
        Used to upload an image file.
        It uses JWT to retrieve user information and then saves the image to the user's folder.
        If there is a filename conflict, it appends a number at the end.
        """
        data = imageSchema.load(request.files) # {"image": FileStorage}
        user_id = get_jwt_identity()
        folder = f"user_{user_id}" #/static/images/user_1
        try:
            image_path = image_helper.save_image(data["image"], folder=folder)
            basename = image_helper.get_basename(image_path)
            return {"message": f"Image '{basename}' Uploaded."}, 201
        except UploadNotAllowed:
            extension = image_helper.get_extension(data["image"])
            return {"message": f"Extension '{extension}' is not allowed."}, 400

class Image(Resource):
    @classmethod
    @jwt_required
    def get(cls, filename: str):
        """
        Returns the requested image if it exists.
        Looks up inside the logged in user's folder.
        """
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        if not image_helper.if_filename_safe(filename):
            return {"message": f"Illegal filename '{filename}'"}, 400
        try:
            return send_file(image_helper.get_path(filename, folder=folder))
        except FileNotFoundError:
            return {"message": "Image Not Found"}, 404

    @classmethod
    @jwt_required
    def delete(cls, filename: str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        if not image_helper.if_filename_safe(filename):
            return {"message": "Illegal filename '{filename}'"}, 400
        try:
            os.remove(image_helper.get_path(filename, folder=folder))
            return {"message": f"Image {filename} deleted"}, 200
        except FileNotFoundError:
            return {"message": "Image Not Found"}, 404
        except Exception as e:
            print(e)
            return {"message": "Image delete failed."}, 500

class AvatarUpload(Resource):
    @classmethod
    @jwt_required
    def put(cls):
        """
        Used to upload a user's Avatar.
        All Avatars are named after the user's ID, example: user_{id}.{ext}.
        Uploading a new Avatar overwrites the existing one.
        """
        data = imageSchema.load(request.files)
        filename = f"user_{get_jwt_identity()}"
        folder = "avatars"
        avatar_path = image_helper.find_image_any_format(filename, folder)
        if avatar_path:
            try:
                os.remove(avatar_path)
            except:
                return {"message": "Avatar Delete Failed."}, 500

        try:
            ext = image_helper.get_extension(data["image"].filename)
            avatar = filename + ext
            avatar_path = image_helper.save_image(
                data["image"], folder=folder, name=avatar
            )
            basename = image_helper.get_basename(avatar_path)
            return {"message": f"Avatar '{basename}' uploaded."}, 200
        except UploadNotAllowed:
            extension = image_helper.get_extension(data['image'])
            return {"message": f"Extension '{extension}' is not allowed."}, 400

class Avatar(Resource):
    @classmethod
    def get(cls, user_id: int):
        folder = "avatars"
        filename = f"user_{user_id}"
        avatar = image_helper.find_image_any_format(filename, folder)
        if avatar:
            return send_file(avatar)
        return {"message": f"Avatar '{avatar}' Not Found."}, 404

