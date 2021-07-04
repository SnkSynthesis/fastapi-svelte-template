from pydantic import BaseModel, Field
import sqlalchemy as sa  # type: ignore
from databases import Database
from .base_crud import BaseCRUD


class ItemIn(BaseModel):
    name: str
    desc: str
    owner_username: str = Field(..., max_length=50)


class Item(ItemIn):
    id: int


class ItemCRUD(BaseCRUD):
    def __init__(self, db: Database) -> None:
        self.tablename = "items"
        self.columns = (
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("name", sa.String(length=50)),
            sa.Column("desc", sa.Text),
            sa.Column("owner_username", sa.String(length=50)),
        )
        self.primary_key = "id"
        super().__init__(db)
