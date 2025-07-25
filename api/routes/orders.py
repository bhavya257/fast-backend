from functools import partial
from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Query, Path
from pydantic_mongo import ObjectIdField

from config import settings
from db import item_exists, execute_order, run_transaction, read_orders_for_user
from models import OrderCreateResponse, OrderItem, OrderReadResponse
from utils import pagination_index

router = APIRouter(prefix="/orders", tags=["orders"])
users_collection = settings.users_collection


@router.post("/", response_model=OrderCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderItem):
    """
    Creates a new order for a user.
    :param order: The order details, includes user id and list of product items with quantity.
    :return: ID of the created order.
    """
    user_exists = await item_exists(users_collection, order.user_id)
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {order.user_id} does not exist"
        )
    try:
        order_callback = partial(execute_order, order=order)
        order_id = await run_transaction(order_callback)
        return {
            "id": order_id,
        }
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/{user_id}", response_model=OrderReadResponse, status_code=status.HTTP_200_OK)
async def read_user_orders(
        user_id: Annotated[ObjectIdField, Path(example="687ceebd47f1ca9b700becac")],
        limit: Annotated[int | None, Query(gt=0)] = 15,
        offset: Annotated[int | None, Query(ge=0)] = 0,
):
    """
    Retrieves a paginated list of orders for a specific user.
    :param user_id: The user's ID.
    :param limit: The maximum number of orders to return.
    :param offset: The number of orders to skip.
    :return: List of orders and page metadata.
    """
    user_exists = await item_exists(users_collection, user_id)
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {user_id} does not exist"
        )
    result = await read_orders_for_user(user_id, limit, offset)
    data = list(result["selected_orders"])
    total_orders = result["total_orders"]
    page = pagination_index(offset, limit, total_orders, len(data))
    return {
        "data": data,
        "page": page,
    }
