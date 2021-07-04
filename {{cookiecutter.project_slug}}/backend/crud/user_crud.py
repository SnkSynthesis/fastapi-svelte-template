from pydantic import BaseModel, Field
import sqlalchemy as sa  # type: ignore
from databases import Database
from .base_crud import BaseCRUD


class UserIn(BaseModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., max_length=50)


class User(BaseModel):
    username: str = Field(..., max_length=50)


class UserCRUD(BaseCRUD):
    def __init__(self, db: Database) -> None:
        self.tablename = "users"
        self.columns = (
            sa.Column("username", sa.String(length=50), primary_key=True, unique=True),
            sa.Column("password_hash", sa.Text),
        )
        self.primary_key = "username"
        super().__init__(db)
