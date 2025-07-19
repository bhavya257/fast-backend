from typing import Annotated
from fastapi import Body
from pydantic import BaseModel

# TODO: fix the Annotated definitions
class ItemSize(BaseModel):
    size: str
    quantity: Annotated[int, Body(ge=0)]

class ProductItem(BaseModel):
    name: str
    price: Annotated[float, Body(ge=0)]
    sizes: list[ItemSize]

class ProductCreateResponse(BaseModel):
    id: Annotated[str, Body(pattern="^[0-9a-fA-F]{24}$")]

class SavedProductItem(BaseModel):
    id: Annotated[str, Body(pattern="^[0-9a-fA-F]{24}$")]
    name: str
    price: Annotated[float, Body(ge=0)]

class Page(BaseModel):
    next: Annotated[int | None, Body(ge=0)] = None
    limit: Annotated[int, Body(ge=0)]
    previous: Annotated[int| None, Body(ge=0)] = None

class ProductsReadResponse(BaseModel):
    data: list[SavedProductItem]
    page: Page