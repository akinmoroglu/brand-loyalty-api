from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Brand Loyalty API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./loyalty.db"

    # Security
    API_KEY: str = "test-secret"
    API_KEY_ENABLED: bool = False  # Set to True to enable API key auth

    class Config:
        case_sensitive = True


settings = Settings()
