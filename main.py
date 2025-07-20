from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.main import api_router
from db import client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    yield
    # Shutdown logic
    client.close()
    print("Application shutdown: Database disconnected.")


app = FastAPI(
    lifespan=lifespan,
)

app.include_router(api_router)
