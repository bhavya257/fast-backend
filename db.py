from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from config import settings

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


async def item_exists(collection_name: str, item_id: ObjectId) -> bool:
    collection = db[collection_name]
    document = collection.find_one({"_id": item_id}, {"_id": 1})
    return document is not None


async def run_transaction(callback):
    with client.start_session() as session:
        session.with_transaction(callback)
