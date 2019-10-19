from collections import Counter
from flask import request
from flask_restful import Resource
from stripe import error

from models.item import ItemModel
from models.order import OrderModel, ItemsInOrder
from schemas.order import OrderSchema

orderSchema = OrderSchema()
orderListSchema = OrderSchema(many=True)

class Order(Resource):
    @classmethod
    def post(cls):
        """
        Expects a token and a list of item ids from the request body.
        Constructs an order and talks to the Stripe API to make a charge.
        """
        data = request.get_json()
        items= []
        item_id_quantities = Counter(data["items_id"])

        for _id, count in item_id_quantities.most_common():
            item = ItemModel.find_by_id(_id)

            if not item:
                return {"message": f"Item {_id} Not Found."}, 404

            items.append(ItemsInOrder(item_id = _id, quantity = count))

        order = OrderModel(items=items, status="pending")
        order.save_to_db()

        try:
            order.set_status("payment failed")
            order.charge_with_stripe(data["token"])
            order.set_status("payment completed")
            return orderSchema.dump(order)
        # the following error handling is advised by Stripe, although the handling implementations are identical,
        # we choose to specify them separately just to give the students a better idea what we can expect
        except error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
            return e.json_body, e.http_status
        except error.RateLimitError as e:
            # Too many requests made to the API too quickly
            return e.json_body, e.http_status
        except error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            return e.json_body, e.http_status
        except error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return e.json_body, e.http_status
        except error.APIConnectionError as e:
            # Network communication with Stripe failed
            return e.json_body, e.http_status
        except error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            return e.json_body, e.http_status
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            print(e)
            return {"message": "Order Error"}, 500

class OrderList(Resource):
    @classmethod
    def get(cls):
        return {'orders': orderListSchema.dump(OrderModel.find_all())}, 200
