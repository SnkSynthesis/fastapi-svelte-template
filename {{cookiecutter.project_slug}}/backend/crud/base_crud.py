from abc import ABC
from typing import Optional, TypeVar, Any
from databases import Database
from pydantic.main import BaseModel
import sqlalchemy as sa
from .. import config


ModelIn = TypeVar("ModelIn", bound=BaseModel)


class NotFoundError(RuntimeError):
    def __init__(self, pk: Any, table: sa.Table):
        super().__init__(f"Primary key, {pk}, of {table} was not found")


class BaseCRUD(ABC):
    def __init__(self, db: Database):
        self.db = db
        self.metadata = sa.MetaData()
        self.table: Optional[sa.Table] = None
        self.primary_key: Optional[sa.Column] = None
        super().__init__()

    async def create(self, model: ModelIn) -> int:
        query = self.table.insert().values(**model.dict())
        pk = await self.db.execute(query)
        return pk

    async def get_one(self, pk: Any):
        query = self.table.select().where(self.primary_key == pk)
        return await self.db.fetch_one(query)

    async def get_all(self):
        query = self.table.select().limit(100)
        return await self.db.fetch_all(query)

    async def update(self, pk: Any, updated_model: ModelIn):
        query = (
            self.table.update()
            .values(**updated_model.dict())
            .where(self.primary_key == pk)
        )
        await self.db.execute(query)

    async def delete(self, pk: Any):
        query = self.table.select().where(self.primary_key == pk)
        await self.db.execute(query)

    def metadata_create_all(self):
        self.metadata.create_all(sa.create_engine(config.DB_URL))
