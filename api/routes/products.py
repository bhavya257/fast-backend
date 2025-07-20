from typing import Annotated

from fastapi import APIRouter, status
from fastapi import Query

from config import settings
from db import create, read
from models import ProductItem, ProductCreateResponse, ProductsReadResponse

router = APIRouter(prefix="/products", tags=["products"])
collection_name = settings.products_collection


@router.post("/", response_model=ProductCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductItem):
    product_dict = product.model_dump()
    product_id = await create(collection_name, product_dict)
    return {
        "id": product_id,
    }


@router.get("/", response_model=ProductsReadResponse, status_code=status.HTTP_200_OK)
async def read_products(
        name: str | None = None,
        size: str | None = None,
        limit: Annotated[int | None, Query(gt=0)] = 15,
        offset: Annotated[int | None, Query(ge=0)] = 0,
):
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if size:
        query["sizes"] = {"$elemMatch": {"size": size}}
    result = await read(collection_name, query, limit, offset)
    total_products = result["total_items"]
    selected_products = result["selected_products"]
    data = [{"id": str(p["_id"]), "name": p["name"], "price": p["price"]} for p in selected_products]

    page = {}
    if offset + limit < total_products:
        page["next"] = offset + limit
    page["limit"] = limit
    if offset > 0:
        page["previous"] = max(0, min(offset - limit, total_products - limit))
    return {
        "data": data,
        "page": page,
    }
