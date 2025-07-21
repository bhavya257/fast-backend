from fastapi import HTTPException, status
from pydantic_mongo import ObjectIdField
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from config import settings
from models import OrderItem

client = MongoClient(settings.mongo_uri, server_api=ServerApi('1'))
db = client.database


async def create(collection_name: str, item: dict) -> str:
    collection = db[collection_name]
    result = collection.insert_one(item)
    item_id = str(result.inserted_id)
    return item_id


async def read(collection_name: str, query: dict, limit: int, offset: int, sort_by: str = "_id") -> dict:
    collection = db[collection_name]
    total_items = collection.count_documents(query)
    selected_items = []
    if total_items != 0:
        selected_items = collection.find(query).skip(offset).limit(limit).sort(sort_by)
    return {
        "total_items": total_items,
        "selected_items": selected_items,
    }


async def item_exists(collection_name: str, item_id: ObjectIdField) -> bool:
    collection = db[collection_name]
    document = collection.find_one({"_id": item_id}, {"_id": 1})
    return document is not None


def read_one_with_session(session, collection_name: str, item_id: ObjectIdField) -> dict | None:
    collection = db[collection_name]
    document = collection.find_one({"_id": item_id}, session=session)
    return document


def create_with_session(session, collection_name: str, item: dict):
    collection = db[collection_name]
    result = collection.insert_one(item, session=session)
    item_id = str(result.inserted_id)
    return item_id


def execute_order(session, order: OrderItem):
    order_total = float(0)
    for item in order.items:
        product = read_one_with_session(session, settings.products_collection, item.productId)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id: {item.productId} does not exist"
            )
        order_total += product["price"] * item.qty
        # TODO: add logic for checking quantity and update it in products
    order_dict = order.model_dump()
    order_dict["total"] = order_total
    # TODO: add creation timestamp to order
    order_id = create_with_session(session, settings.orders_collection, order_dict)
    return order_id


async def run_transaction(callback):
    with client.start_session() as session:
        return session.with_transaction(callback)


async def read_orders_for_user(user_id: ObjectIdField, limit: int, offset: int):
    orders_collection = db[settings.orders_collection]

    query = {'user_id': user_id}
    total_orders = orders_collection.count_documents(query)
    if total_orders == 0:
        return {"total_orders": 0, "selected_orders": []}

    pipeline = [
        {'$match': query},
        # TODO: sort by creation timestamp (latest first)
        {'$skip': offset},
        {'$limit': limit},
        {'$unwind': '$items'},
        {'$lookup': {
            'from': settings.products_collection,
            'localField': 'items.productId',
            'foreignField': '_id',
            'as': 'productInfo'
        }},
        {'$unwind': '$productInfo'},  # lookup gives result in array so unwind is necessary
        {'$group': {
            '_id': '$_id',
            'total': {'$first': '$total'},
            'items': {
                '$push': {
                    'qty': '$items.qty',
                    'productDetails': {
                        'id': {'$toString': '$productInfo._id'},
                        'name': '$productInfo.name'
                    }
                }
            }
        }},
        {'$project': {
            '_id': 0, # id field needs to suppressed explicitly
            'id': {'$toString': '$_id'},
            'total': '$total',
            'items': '$items'
        }}
    ]
    selected_orders = orders_collection.aggregate(pipeline)

    return {
        "total_orders": total_orders,
        "selected_orders": selected_orders,
    }
