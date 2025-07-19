from fastapi import APIRouter, HTTPException
from config import settings
# from models import ProductItem

router = APIRouter(prefix="/orders", tags=["orders"])
collection = settings.orders_collection

# TODO: create order apis