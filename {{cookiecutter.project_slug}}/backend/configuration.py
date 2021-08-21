from typing import Dict
from pydantic import BaseSettings


class Configuration(BaseSettings):
    db_url: str = "sqlite:///./database.db"
    test_db_url: str = "sqlite:///./test.db"

    # Define scopes aka permissions
    scopes: Dict[str, str] = {
        "admin:delete_user": "Delete any user",
        "admin:update_user": "Update any user",
        "admin:delete_item": "Delete any user's item",
        "admin:update_item": "Update any user's item",
    }

    token_url: str = "/token"

    # openssl rand -hex 32
    secret_key: str = "c1db475aa41be1b794cbb9881e87c89ad632c698ef84862cae400f86dea54c2b"
    algorithm: str = "HS256"
    token_expire: int = 30  # minutes


config = Configuration()
