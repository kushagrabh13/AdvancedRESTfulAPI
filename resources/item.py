from flask_restful import Resource, reqparse
from flask import request
from flask_jwt_extended import jwt_required, fresh_jwt_required
from models.item import ItemModel
from schemas.item import ItemSchema

itemSchema = ItemSchema()
itemListSchema = ItemSchema(many=True)

class Item(Resource):
    @classmethod
    def get(cls, name):
        item = ItemModel.find_by_name(name)
        if item:
            return itemSchema.dump(item)

        return {'message': 'Item Not Found.'}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists!"}, 400

        itemJSON = request.get_json()
        itemJSON["name"] = name

        item = itemSchema.load(itemJSON)

        try:
            item.save_to_db()
        except:
            return {'message': 'An error occured while inserting the item'}, 500

        return itemSchema.dump(item), 201

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
        itemJSON = request.get_json()
        item = ItemModel.find_by_name(name)

        if item:
            item.price = itemJSON['price']
        else:
            itemJSON["name"] = name
            item = itemSchema.load(itemJSON)

        item.save_to_db()

        return itemSchema.dump(item), 200

class ItemList(Resource):
    @classmethod
    def get(cls):
        return {'items': itemListSchema.dump(ItemModel.find_all())}, 200
