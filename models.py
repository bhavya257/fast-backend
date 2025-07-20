from typing import Annotated

from fastapi import Body
from pydantic import BaseModel, Field
from pydantic_mongo import ObjectIdField


class ItemSize(BaseModel):
    size: str
    quantity: Annotated[int, Body(gt=0)]


class ProductItem(BaseModel):
    name: str
    price: Annotated[float, Body(ge=0)]
    sizes: list[ItemSize]


class ProductCreateResponse(BaseModel):
    id: ObjectIdField = Field(default_factory=ObjectIdField)
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class SavedProductItem(BaseModel):
    id: ObjectIdField = Field(default_factory=ObjectIdField)
    name: str
    price: Annotated[float, Body(ge=0)]
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class Page(BaseModel):
    next: Annotated[int | None, Body(ge=0)] = None
    limit: Annotated[int, Body(gt=0)]
    previous: Annotated[int | None, Body(ge=0)] = None


class ProductsReadResponse(BaseModel):
    data: list[SavedProductItem]
    page: Page


class OrderProductItem(BaseModel):
    productId: ObjectIdField = Field(default_factory=ObjectIdField)
    qty: Annotated[int, Body(gt=0)]
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class OrderItem(BaseModel):
    user_id: ObjectIdField = Field(default=ObjectIdField("687ceebd47f1ca9b700becac"))
    items: list[OrderProductItem]
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class OrderCreateResponse(BaseModel):
    id: ObjectIdField = Field(default_factory=ObjectIdField)
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
