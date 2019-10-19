from marsh import io
from models.order import OrderModel


class OrderSchema(io.ModelSchema):
    class Meta:
        model = OrderModel
        load_only = ("token", )
        dump_only = ("id", "status", )