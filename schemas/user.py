from marsh import io
from marshmallow import pre_dump

from models.user import UserModel

class UserSchema(io.ModelSchema):
	class Meta:
		model = UserModel
		load_only = ("password",)
		dump_only = ("id", "confirmation")

	@pre_dump
	def _pre_dump(self, user: UserModel):
		try:
			user.confirmation = [user.most_recent_confirmation]
		except:
			pass
		return user