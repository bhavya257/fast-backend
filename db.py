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
    selected_products = collection.find(query).skip(offset).limit(limit).sort(sort_by)
    return {
        "total_items": total_items,
        "selected_products": selected_products,
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
    for item in order.items:
        product = read_one_with_session(session, settings.products_collection, item.productId)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id: {item.productId} does not exist"
            )

        # TODO: add logic for checking quantity and update it

    order_dict = order.model_dump()
    order_id = create_with_session(session, settings.orders_collection, order_dict)
    return order_id


async def run_transaction(callback):
    with client.start_session() as session:
        return session.with_transaction(callback)
