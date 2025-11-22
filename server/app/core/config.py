# server/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OAuth / Gmail
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # Google AI / Gemini
    GOOGLE_API_KEY: str | None = None    
    GEMINI_API_KEY: str | None = None  

    # Other optional settings
    APP_ENV: str = "development"
    SECRET_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
