from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class EnvironmentType(str, Enum):
    DEV = "DEV"
    LOCAL = "LOCAL"
    PROD = "PROD"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Wiki"
    PROJECT_DESCRIPTION: str = "Welcome to Wiki's API documentation! Here you will able to discover all of the ways you can interact with the Wiki API."
    VERSION: str = "0.0.1"
    API_V1_STR: str = "/api/v1"
    API_SERVERS: list = [
        {
            "url": "http://localhost:8000",
            "description": "Local server"
        },
        {
            "url": "https://api.wiki.example.com",
            "description": "Demo server"
        },
        {
            "url": "https://poorly-ideal-cobra.ngrok-free.app",
            "description": "Ngrok free server"
        }
    ]

    ENVIRONMENT: EnvironmentType = EnvironmentType.DEV
    DEBUG: bool = True
    DB_ECHO: bool = False
    LOG_FILENAME: str = "wiki.log"
    LOGGER_NAME: str = "wiki_logger"

    AUTH_SECRET_MAIN: bytes = b"886862ad333aeea48c9b1a3e3e1ac21096aea3436d0190b300be96642a4a328612"
    AUTH_SECRET_API_KEY: bytes = b"bf48fbdd0a692198d4f5d6f1210646fae139930e1c46aa7f29c60ca1c437d1b6"
    AUTH_SECRET_VERIFY: bytes = b"33b974fedccff8f671d3691e89bf52857cfcaed716b9b2c76449216fd251f534"

    AUTH_ROOT_API_KEYS: list[str | bytes] = ["12345", b"e37bc241f2adebb5845f5efb1d3c0de11e98001dc485c79507652cce67ad62c6"]

    AUTH_API_KEY_QUERY_NAME: str = "wiki_api_key"
    AUTH_API_KEY_HEADER_NAME: str = "X-Wiki-API-Key"
    AUTH_ROOT_API_KEY_HEADER_NAME: str = "X-Wiki-ROOT-API-Key"
    AUTH_ACCESS_TOKEN_COOKIE_NAME: str = "wiki_access_token"
    AUTH_REFRESH_TOKEN_COOKIE_NAME: str = "wiki_refresh_token"

    AUTH_API_KEY_LENGTH: int = 40
    AUTH_API_KEY_PREFIX_LENGTH: int = 8

    AUTH_TOKEN_COOKIE_PATH: str = "/"
    AUTH_TOKEN_COOKIE_DOMAIN: str = "localhost"
    AUTH_TOKEN_COOKIE_SECURE: bool = False
    AUTH_TOKEN_COOKIE_HTTP_ONLY: bool = True
    AUTH_TOKEN_COOKIE_SAME_SITE: str = "lax"

    AUTH_ALGORITHM: str = "HS256"
    AUTH_ALGORITHM_API_KEY: str = "SHA256"

    AUTH_VERIFY_TOKEN_EXPIRE_MINUTES: int = 5
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 180
    AUTH_REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 60 * 24 * 7

    DB_SCHEMA: str = "postgresql"
    DB_DRIVER: str = "asyncpg"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_SSL: str = "prefer"  # disable, allow, prefer, require, verify-ca, verify-full
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "wiki"

    DB_POOL_SIZE: int = 75
    DB_MAX_OVERFLOW: int = 20

    DB_METADATA_CREATE_ALL: bool = True

    BACKEND_CORS_ORIGINS: list[str] = ["http://127.0.0.1:3000",
                                       "http://localhost:3000",
                                       "http://127.0.0.1:8000",
                                       "http://localhost:8000",
                                       "https://egorov-m.github.io",
                                       "https://poorly-ideal-cobra.ngrok-free.app"]

    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_MAIL_STARTTLS: bool = False
    EMAIL_MAIL_SSL_TLS: bool = True
    EMAIL_USE_CREDENTIALS: bool = True
    EMAIL_VALIDATE_CERTS: bool = True

    EMAIL_SENDING: bool = True  # If you don’t want letters sent to the email, set false.

    LAKECTL_SERVER_ENDPOINT_URL: str = "http://localhost:8001"
    LAKEFS_STORAGE_NAMESPACE_ROOT: str = "local://wiki_storage/"
    LAKEFS_DEFAULT_BRANCH: str = "main"
    LAKEFS_AUTH_ENCRYPT_SECRET_KEY: str = "12345"
    LAKEFS_INSTALLATION_USER_NAME: str = "wiki-admin"
    LAKEFS_INSTALLATION_ACCESS_KEY_ID: str = "12345"
    LAKEFS_INSTALLATION_SECRET_ACCESS_KEY: str = "12345"
    LAKEFS_DOCUMENT_BLOCK_FILE_EXT: str = ".html"

    YA_OAUTH_TOKEN: str = "y0_AgAAAABWELfiAArJgAAAAADxYZGSWLplcGVRQ-uUK8C7obp495NQyMI"
    ASSET_SIZE_LIMIT_KB: int = 51200  # 50 MB

    def get_db_url(self):
        return (f"{self.DB_SCHEMA}+{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?ssl={self.DB_SSL}")

    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
