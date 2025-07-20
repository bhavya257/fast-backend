from typing import Annotated

from fastapi import Body
from pydantic import BaseModel
from pydantic_mongo import ObjectIdField


class ItemSize(BaseModel):
    size: str
    quantity: Annotated[int, Body(gt=0)]


class ProductItem(BaseModel):
    name: str
    price: Annotated[float, Body(ge=0)]
    sizes: list[ItemSize]


class ProductCreateResponse(BaseModel):
    id: ObjectIdField


class SavedProductItem(BaseModel):
    id: ObjectIdField
    name: str
    price: Annotated[float, Body(ge=0)]


class Page(BaseModel):
    next: Annotated[int | None, Body(ge=0)] = None
    limit: Annotated[int, Body(gt=0)]
    previous: Annotated[int | None, Body(ge=0)] = None


class ProductsReadResponse(BaseModel):
    data: list[SavedProductItem]
    page: Page


class OrderProductItem(BaseModel):
    productId: ObjectIdField
    qty: Annotated[int, Body(gt=0)]


class OrderItem(BaseModel):
    user_id: ObjectIdField
    items: list[OrderProductItem]

    model_config = {
        "json_schema_extra": {"example": {
            "user_id": "687ceebd47f1ca9b700becac",
            "items": [
                {"productId": "687bee26ed7470dbb5c52192",
                 "qty": 69},
            ]
        }}
    }


class OrderCreateResponse(BaseModel):
    id: ObjectIdField


class SavedOrderProductItem(BaseModel):
    name: str
    id: ObjectIdField


class SavedOrderItem(BaseModel):
    productDetails: list[SavedOrderProductItem]
    qty: Annotated[int, Body(gt=0)]


class SavedOrders(BaseModel):
    id: ObjectIdField
    items: list[SavedOrderItem]


class OrderReadResponse(BaseModel):
    data: list[SavedOrders]
    page: Page
