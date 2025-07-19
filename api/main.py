from fastapi import APIRouter
from api.routes import products, orders


api_router = APIRouter()

api_router.include_router(products.router)
api_router.include_router(products.router)