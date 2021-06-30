from pydantic import BaseModel, Field
import sqlalchemy as sa
from databases import Database
from .base_crud import BaseCRUD


class ItemIn(BaseModel):
    name: str
    desc: str
    owner_username: str = Field(..., max_length=50)


class Item(ItemIn):
    id: int


class ItemCRUD(BaseCRUD):
    def __init__(self, db: Database):
        super().__init__(db)
        self.table = sa.Table(
            "items",
            self.metadata,
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("name", sa.String(length=50)),
            sa.Column("desc", sa.Text),
            sa.Column("owner_username", sa.String(length=50)),
        )
        self.primary_key = self.table.c.id
