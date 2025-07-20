from typing import Annotated

from fastapi import APIRouter, status, Query, HTTPException

from config import settings
from db import item_exists
from models import OrderCreateResponse, OrderItem

router = APIRouter(prefix="/orders", tags=["orders"])
collection = settings.orders_collection
user_collection = settings.user_collection


# @router.post("/", response_model=OrderCreateResponse, status_code=status.HTTP_201_CREATED)
# async def create_order(order: OrderItem):
#     user_exists = item_exists(user_collection, order.user_id)
#     if not user_exists:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")
#
#     for product in order.items:
#
#     return


# @router.get("/", response_model=, status_code=status.HTTP_200_OK)
# async def read_orders(
#         limit: Annotated[int | None, Query(gt=0)] = 15,
#         offset: Annotated[int | None, Query(ge=0)] = 0,
# )
