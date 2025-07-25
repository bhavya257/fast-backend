from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    products_collection: str = "products"
    orders_collection: str = "orders"
    users_collection: str = "users"
    mongo_uri: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
