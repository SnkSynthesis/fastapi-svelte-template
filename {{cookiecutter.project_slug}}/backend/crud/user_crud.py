from pydantic import BaseModel, Field
import sqlalchemy as sa
from databases import Database
from .base_crud import BaseCRUD


class UserIn(BaseModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., max_length=50)


class User(UserIn):
    id: int


class UserCRUD(BaseCRUD):
    def __init__(self, db: Database):
        super().__init__(db)
        self.table = sa.Table(
            "users",
            self.metadata,
            sa.Column("username", sa.String(length=50), primary_key=True, unique=True),
            sa.Column("password_hash", sa.Text),
        )
        self._metadata_create_all()
