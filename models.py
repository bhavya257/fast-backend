from typing import Annotated

from bson import ObjectId
from fastapi import Body
from pydantic import BaseModel, Field


class ItemSize(BaseModel):
    size: str
    quantity: Annotated[int, Body(gt=0)]


class ProductItem(BaseModel):
    name: str
    price: Annotated[float, Body(ge=0)]
    sizes: list[ItemSize]


class ProductCreateResponse(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")


class SavedProductItem(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    name: str
    price: Annotated[float, Body(ge=0)]


class Page(BaseModel):
    next: Annotated[int | None, Body(ge=0)] = None
    limit: Annotated[int, Body(gt=0)]
    previous: Annotated[int | None, Body(ge=0)] = None


class ProductsReadResponse(BaseModel):
    data: list[SavedProductItem]
    page: Page


class OrderCreateResponse(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")


class OrderProductItem(BaseModel):
    productId: ObjectId = Field(default_factory=ObjectId, alias="_id")
    qty: Annotated[int, Body(gt=0)]


class OrderItem(BaseModel):
    user_id: ObjectId = Field(default=ObjectId("687ceebd47f1ca9b700becac"), alias="_id")
    items: list[OrderProductItem]
