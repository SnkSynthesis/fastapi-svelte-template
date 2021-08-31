from typing import Any, List, Mapping, Union
from pydantic import BaseModel, Field
import sqlalchemy as sa  # type: ignore
from databases import Database
from .base_crud import BaseCRUD, ModelIn
from ..auth.context import pwd_context
from ..configuration import config


class User(BaseModel):
    """
    For use in the User API (As a response) with password ommited.
    """

    username: str = Field(..., max_length=50)


class UserInDB(User):
    """
    For use when interacting with the database including password hash
    """

    password_hash: str = Field(...)


class UserIn(User):
    """
    For use in the User API (As input) with password included.
    """

    password: str = Field(..., max_length=50)


class UserCRUD(BaseCRUD):
    def __init__(self, db: Database) -> None:
        self.tablename = "users"
        self.columns = (
            sa.Column("username", sa.String(length=50), primary_key=True, unique=True),
            sa.Column("password_hash", sa.Text),
        )
        self.primary_key = "username"
        super().__init__(db)

        # Create scopes table
        self.scopes_table = sa.Table(
            "user_scopes",
            self.metadata,
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("user_username", sa.ForeignKey("users.username")),
            sa.Column("scope", sa.String(length=100)),
        )

    # Override create(), get_one(), get_all(), and update() to support scopes attribute and password hashing
    async def create(self, model: ModelIn) -> int:
        user_model = UserInDB(
            username=model.username, password_hash=pwd_context.hash(model.password)
        )
        return await super().create(user_model)

    # async def get_one(self, pk: Any) -> Union[Mapping, None]:
    #     query = self.table.select().join(
    #         self.scopes_table, self.scopes_table.c.user_username == pk
    #     )
    #     return await self.db.fetch_one(query)

    # async def get_all(self) -> List[Mapping]:
    #     query = self.table.select().join(
    #         self.scopes_table, self.primary_key == self.scopes_table.c.user_username
    #     )
    #     return await self.db.fetch_all(query)

    async def update(self, pk: Any, updated_model: ModelIn) -> None:
        raise AttributeError(
            "Unsupported method. Use update_username(), update_password(), add_scope(), and/or delete_scope()"
        )

    async def update_username(self, old_username: str, new_username: str) -> None:
        query = (
            self.table.update()
            .values({"username": new_username})
            .where(self.primary_key == old_username)
        )
        await self.db.execute(query)

    async def update_password(self, username: str, new_password: str) -> None:
        query = (
            self.table.update()
            .values({"password_hash": pwd_context.hash(new_password)})
            .where(self.primary_key == username)
        )
        await self.db.execute(query)

    async def get_scopes(self, username: str) -> List[str]:
        query = self.scopes_table.select().where(
            self.scopes_table.c.user_username == username
        )
        raw_scopes = await self.db.fetch_all(query)
        scopes = []
        for raw_scope in raw_scopes:
            scopes.append(raw_scope["scope"])
        return scopes

    async def add_scope(self, username: str, scope: str):
        if scope not in config.scopes.keys():
            raise RuntimeError("Scope not defined in configuration")
        query = self.scopes_table.insert().values(
            {"user_username": username, "scope": scope}
        )
        await self.db.execute(query)

    async def delete_scope(self, username: str, scope: str):
        if scope not in config.scopes.keys():
            raise RuntimeError("scope not defined in configuration")
        query = self.scopes_table.delete().where(
            self.scopes_table.c.user_username == username,
            self.scopes_table.c.scope == scope,
        )
        await self.db.execute(query)