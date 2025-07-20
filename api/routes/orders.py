from functools import partial

from fastapi import APIRouter, status, HTTPException

from config import settings
from db import item_exists, execute_order, run_transaction
from models import OrderCreateResponse, OrderItem

router = APIRouter(prefix="/orders", tags=["orders"])
collection = settings.orders_collection
users_collection = settings.users_collection


@router.post("/", response_model=OrderCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderItem):
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


# @router.get("/", response_model=, status_code=status.HTTP_200_OK)
# async def read_orders(
#         limit: Annotated[int | None, Query(gt=0)] = 15,
#         offset: Annotated[int | None, Query(ge=0)] = 0,
# ):
#     return
