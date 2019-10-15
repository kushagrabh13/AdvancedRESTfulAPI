from marsh import io
from models.item import ItemModel
from models.store import StoreModel


class ItemSchema(io.ModelSchema):
	class Meta:
		model = ItemModel
		load_only = ("store",)
		dump_only = ("id",)
		include_fk = True