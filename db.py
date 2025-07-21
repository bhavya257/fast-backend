from datetime import datetime, timezone

from fastapi import HTTPException, status
from pydantic_mongo import ObjectIdField
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from config import settings
from models import OrderItem

client = MongoClient(settings.mongo_uri, server_api=ServerApi('1'))
db = client.database


async def create(collection_name: str, item: dict) -> str:
    """
    Generic function that inserts a new document into a collection.
    :param collection_name: The name of the collection to check.
    :param item: The document to be inserted.
    :return: The inserted document's ObjectId.
    """
    collection = db[collection_name]
    result = collection.insert_one(item)
    item_id = str(result.inserted_id)
    return item_id


async def read(collection_name: str, query: dict, limit: int, offset: int, sort_by: str = "_id") -> dict:
    """
    Generic function that fetches multiple documents based on a query, with pagination and sorting.
    :param collection_name: The name of the collection to check.
    :param query: The query to fetch.
    :param limit: The maximum number of documents to return.
    :param offset: The number of documents to skip.
    :param sort_by: Name of the field to sort by.
    :return:
    """
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
    """
    Generic function to check if an ID exists in a collection.
    :param collection_name: The name of the collection to check.
    :param item_id: ObjectId of the item to search.
    :return: True if the document exists, False otherwise.
    """
    collection = db[collection_name]
    document = collection.find_one({"_id": item_id}, {"_id": 1})
    return document is not None


def read_one_with_session(session, collection_name: str, item_id: ObjectIdField) -> dict | None:
    """
    Reads a document with a given database session.
    Used for transactions.
    :param session: The PyMongo client session object for the transaction.
    :param collection_name: The name of the collection to insert into.
    :param item_id: ObjectId of the item to fetch.
    :return: Single document that matches the item_id.
    """
    collection = db[collection_name]
    document = collection.find_one({"_id": item_id}, session=session)
    return document


def create_with_session(session, collection_name: str, item: dict):
    """
    Creates a document with a given database session.
    Used for transactions.
    :param session: The PyMongo client session object for the transaction.
    :param collection_name: The name of the collection to insert into.
    :param item: Document to insert.
    :return: The inserted document's ObjectId as string.
    """
    collection = db[collection_name]
    result = collection.insert_one(item, session=session)
    item_id = str(result.inserted_id)
    return item_id


def execute_order(session, order: OrderItem):
    """
    Executes the logic for creating an order with a database transaction.
    :param session: The PyMongo client session object for the transaction.
    :param order: The order details.
    :return: The created order's ObjectId as string.
    """
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
    order_dict["created_at"] = datetime.now(timezone.utc)
    order_id = create_with_session(session, settings.orders_collection, order_dict)
    return order_id


async def run_transaction(callback):
    """
    A generic wrapper to execute a given function with a database transaction.
    :param callback: The function to be executed within the transaction.
    :return: The result returned by the callback function.
    """
    with client.start_session() as session:
        return session.with_transaction(callback)


async def read_orders_for_user(user_id: ObjectIdField, limit: int, offset: int):
    """
    Fetches a paginated list of orders for a user using an aggregation pipeline.
    The pipeline joins product details for each item in an order and converts ObjectIds to strings.
    :param user_id: The user's ID.
    :param limit: The maximum number of orders to return.
    :param offset: The number of orders to skip.
    :return: Total number of orders and list of orders.
    """
    orders_collection = db[settings.orders_collection]

    query = {'user_id': user_id}
    total_orders = orders_collection.count_documents(query)
    if total_orders == 0:
        return {"total_orders": 0, "selected_orders": []}

    pipeline = [
        {'$match': query},
        {'$sort': {'created_at': -1}},
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
            '_id': 0,  # id field needs to be suppressed explicitly
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
