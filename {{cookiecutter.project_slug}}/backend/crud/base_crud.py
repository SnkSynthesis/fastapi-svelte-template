from abc import ABC
from typing import List, Mapping, Optional, TypeVar
from databases import Database
from pydantic.main import BaseModel
import sqlalchemy as sa
from .. import config


ModelIn = TypeVar("ModelIn", bound=BaseModel)


class NotFoundError(RuntimeError):
    def __init__(self, id: int, table: sa.Table):
        super().__init__(f"{id} of {table} not found")


class BaseCRUD(ABC):
    def __init__(self, db: Database):
        self.db = db
        self.table: Optional[sa.Table] = None
        self.metadata = sa.MetaData()
        super().__init__()

    async def create(self, model: ModelIn) -> int:
        query = self.table.insert().values(**model.dict())
        last_record_id = await self.db.execute(query)
        return last_record_id

    async def get_one(self, id: int):
        query = self.table.select().where(self.table.c.id == id)
        return await self.db.fetch_one(query)

    async def get_all(self):
        query = self.table.select().limit(100)
        return await self.db.fetch_all(query)

    async def update(self, id: int, updated_model: ModelIn):
        query = (
            self.table.update()
            .values(**updated_model.dict())
            .where(self.table.c.id == id)
        )
        await self.db.execute(query)

    async def delete(self, id: int):
        query = self.table.select().where(self.table.c.id == id)
        await self.db.execute(query)

    def _metadata_create_all(self):
        self.metadata.create_all(sa.create_engine(config.DB_URL))
