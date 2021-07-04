from pydantic import BaseSettings


class Configuration(BaseSettings):
    db_url: str = "sqlite:///./database.db"
    test_db_url: str = "sqlite:///./test.db"


config = Configuration()
