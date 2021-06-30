from typing import Type
from .base_crud import BaseCRUD
from fastapi import Depends
from databases import Database
from .. import config


async def get_database():
    async with Database(config.DB_URL) as db:
        yield db


def get_crud_obj(obj_type: Type[BaseCRUD]) -> BaseCRUD:
    def get_obj(db: Database = Depends(get_database)):
        obj = obj_type(db)
        obj.metadata_create_all()
        return obj

    return get_obj
