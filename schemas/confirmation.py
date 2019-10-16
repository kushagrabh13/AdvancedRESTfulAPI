from marsh import io
from models.confirmation import ConfirmationModel

class ConfirmationSchema(io.ModelSchema):
    class Meta:
        model = ConfirmationModel
        load_only = ("user", )
        dump_only = ("id", "expired_at", "confirmed")
        include_fk = True