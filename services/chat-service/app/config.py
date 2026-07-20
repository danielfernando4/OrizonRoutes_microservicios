from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "Chat Service"
    DEBUG: bool = True

    # MongoDB
    MONGO_URL: str = "mongodb://mongo_chat:27017"
    MONGO_DB_NAME: str = "db_chat"

    # JWT (debe coincidir con Identity Service)
    JWT_SECRET_KEY: str = "28088ae11d2e1571053fe33386cbfa6e"
    JWT_ALGORITHM: str = "HS256"

    HOST: str = "0.0.0.0"
    PORT: int = 8004


settings = Settings()
