from marsh import io
from models.user import UserModel

class UserSchema(io.ModelSchema):
	class Meta:
		model = UserModel
		load_only = ("password",)
		dump_only = ("id",)