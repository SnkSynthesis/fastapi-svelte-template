from abc import ABC
from typing import List, Mapping, Optional, Tuple, TypeVar, Any, Union
from databases import Database
from pydantic.main import BaseModel
import sqlalchemy as sa  # type: ignore
from .. import config


ModelIn = TypeVar("ModelIn", bound=BaseModel)


class NotFoundError(RuntimeError):
    def __init__(self, pk: Any, table: sa.Table) -> None:
        super().__init__(f"Primary key, {pk}, of {table} was not found")


class BaseCRUD(ABC):
    def __init__(self, db: Database) -> None:
        self.db = db
        self.metadata = sa.MetaData()

        if hasattr(self, "tablename") and hasattr(self, "columns"):
            self.tablename: str = self.tablename
            self.columns: Tuple[sa.Column, ...] = tuple(self.columns)
            self.table = sa.Table(self.tablename, self.metadata, *self.columns)
        else:
            raise Exception("Attributes `columns` and/or `tablename` are not defined")

        if not hasattr(self, "primary_key"):
            raise Exception("Attribute `primary_key` not defined")
        else:
            self.primary_key: sa.Column = self.table.c[self.primary_key]

        super().__init__()

    async def create(self, model: ModelIn) -> int:
        query = self.table.insert().values(**model.dict())
        pk = await self.db.execute(query)
        return pk

    async def get_one(self, pk: Any) -> Union[Mapping, None]:
        query = self.table.select().where(self.primary_key == pk)
        return await self.db.fetch_one(query)

    async def get_all(self) -> List[Mapping]:
        query = self.table.select().limit(100)
        return await self.db.fetch_all(query)

    async def update(self, pk: Any, updated_model: ModelIn) -> None:
        query = (
            self.table.update()
            .values(**updated_model.dict())
            .where(self.primary_key == pk)
        )
        await self.db.execute(query)

    async def delete(self, pk: Any) -> None:
        query = self.table.select().where(self.primary_key == pk)
        await self.db.execute(query)

    def metadata_create_all(self, db_url: str) -> None:
        self.metadata.create_all(sa.create_engine(db_url))
