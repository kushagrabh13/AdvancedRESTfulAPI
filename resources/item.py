from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, fresh_jwt_required
from models.item import ItemModel

BLANK_ERROR = "'{}' cannot be left blank!"

class Item(Resource):
    parser = reqparse.RequestParser()
    
    parser.add_argument('price',
            type=float,
            required=True,
            help=BLANK_ERROR.format("Price")
            )

    parser.add_argument('store_id',
            type=int,
            required=True,
            help=BLANK_ERROR.format("StoreID")
            )

    @classmethod
    def get(cls, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()

        return {'message': 'Item Not Found.'}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists!"}, 400

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {'message': 'An error occured while inserting the item'}, 500

        return item.json(), 201

    @classmethod
    @jwt_required
    def delete(cls, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': 'item Deleted'}
        return {'message': 'Item Not Found'}, 404

    @classmethod
    @jwt_required
    def put(cls, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data['price']
        else:
            item = ItemModel(name, **data)

        item.save_to_db()

        return item.json(), 200

class ItemList(Resource):
    @classmethod
    def get(cls):
        return {'items': list(map(lambda x: x.json(), ItemModel.query.all()))}
