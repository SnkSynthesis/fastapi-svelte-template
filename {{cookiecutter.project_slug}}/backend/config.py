from starlette.config import Config


config = Config(".env")

DB_URL = config("DB_URL", default="sqlite:///./database.db")
