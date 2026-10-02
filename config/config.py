import os
from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is not set, check .env")
    return value


class Config:
    BASE_URL: str = _required("BASE_URL")
    FRONTEND_URL: str = _required("FRONTEND_URL")
    DATABASE_URL: str = _required("DATABASE_URL")

    # Timeouts
    API_TIMEOUT: int = 30  # seconds, requests


config = Config()
