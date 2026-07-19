from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "Booking Service"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql+asyncpg://user:pass@db_booking:5432/db_booking"

    JWT_SECRET_KEY: str = "clave-secreta-compartida-con-identity-service"
    JWT_ALGORITHM: str = "HS256"

    PAYPAL_CLIENT_ID: str = "sandbox-client-id"
    PAYPAL_CLIENT_SECRET: str = "sandbox-client-secret"
    PAYPAL_SANDBOX: bool = True
    PAYPAL_RETURN_URL: str = "http://localhost/api/booking/confirm-payment"
    PAYPAL_CANCEL_URL: str = "http://localhost:5173"

    CATALOG_SERVICE_URL: str = "http://catalog-service:8002"

    HOST: str = "0.0.0.0"
    PORT: int = 8003


settings = Settings()
