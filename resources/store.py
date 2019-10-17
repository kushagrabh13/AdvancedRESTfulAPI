from flask_restful import Resource
from models.store import StoreModel
from flask_jwt_extended import jwt_required, fresh_jwt_required
from schemas.store import StoreSchema

storeSchema = StoreSchema()
storeListSchema = StoreSchema(many=True)

class Store(Resource):
    @classmethod
    def get(cls, name):
        store = StoreModel.find_by_name(name)
        if store:
            return storeSchema.dump(store), 200
        return {'message': 'Store Not Found'}, 404

    @classmethod
    @jwt_required
    def post(cls, name):
        if StoreModel.find_by_name(name):
            return {'message': "A store with name '{}' already exists!".format(name)}, 400

        store = StoreModel(name=name)
        try:
            store.save_to_db()
        except:
            return {'message': 'An error occured creating the store.'}, 500

        return storeSchema.dump(store), 201

    @classmethod
    @jwt_required
    def delete(cls, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return {'message': 'Store deleted'}

class StoreList(Resource):
    @classmethod
    def get(cls):
        return {'stores': storeListSchema.dump(StoreModel.find_all())}
