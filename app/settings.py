from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    FRONT_URL: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    GOOGLE_AUTH_URI: str
    GOOGLE_TOKEN_URI: str
    APPLE_CLIENT_ID: str
    APPLE_CLIENT_SECRET: str
    APPLE_REDIRECT_URI: str
    APPLE_AUTH_URI: str
    APPLE_TOKEN_URI: str
