from typing import Annotated

from fastapi import APIRouter, status
from fastapi import Query

from config import settings
from db import create, read
from models import ProductItem, ProductCreateResponse, ProductsReadResponse
from utils import pagination_index

router = APIRouter(prefix="/products", tags=["products"])
collection_name = settings.products_collection


@router.post("/", response_model=ProductCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductItem):
    """
    Adds new product to the database.
    :param product: The product details.
    :return: ID of the created product.
    """
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
    """
    Retrieves a paginated list of products with optional filtering.
    :param name: Regex or partial/complete name of the product to filter.
    :param size: A specific size of the product to filter.
    :param limit: The maximum number of products to return.
    :param offset: The number of products to skip.
    :return: List of products and page metadata.
    """
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if size:
        query["sizes"] = {"$elemMatch": {"size": size}}
    result = await read(collection_name, query, limit, offset)
    total_products = result["total_items"]
    selected_products = result["selected_items"]
    data = [{"id": str(p["_id"]), "name": p["name"], "price": p["price"]} for p in selected_products]

    page = pagination_index(offset, limit, total_products, len(data))
    return {
        "data": data,
        "page": page,
    }
