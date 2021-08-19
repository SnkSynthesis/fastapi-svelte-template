from typing import AsyncGenerator, Callable, Type, TypeVar
from .base_crud import BaseCRUD
from fastapi import Depends
from databases import Database
from .. import config


async def get_database() -> AsyncGenerator[Database, None]:
    async with Database(config.db_url) as db:
        yield db


def is_testing() -> bool:
    return False


def get_crud_obj(obj_type: Type[BaseCRUD]) -> Callable[[Database], Type[BaseCRUD]]:
    def get_obj(
        db: Database = Depends(get_database), testing: bool = Depends(is_testing)
    ) -> Type[BaseCRUD]:
        obj = obj_type(db)
        if not testing:
            obj.metadata_create_all(config.db_url)
        else:
            obj.metadata_create_all(config.test_db_url)
        return obj

    return get_obj
