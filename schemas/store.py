from marsh import io
from models.item import ItemModel
from models.store import StoreModel
from schemas.item import ItemSchema

class StoreSchema(io.ModelSchema):
	items = io.Nested(ItemSchema, many=True)
	class Meta:
		model = StoreModel
		dump_only = ("id",)
		include_fk = True