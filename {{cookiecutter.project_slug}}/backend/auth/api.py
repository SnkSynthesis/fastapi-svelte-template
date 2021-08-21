from databases import Database
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from fastapi import HTTPException, Depends, APIRouter
from fastapi import APIRouter, HTTPException, status, Depends
from ..crud.user_crud import UserCRUD, UserInDB
from ..crud.deps import get_crud_obj
from jose import jwt
from .context import Token, pwd_context
from ..configuration import config
from typing import Union

router = APIRouter(tags=["Authentication"])


def create_access_token(data: dict) -> str:
    datacopy = data.copy()
    datacopy.update({"exp": config.token_expire})
    token = jwt.encode(datacopy, config.secret_key, algorithm=config.algorithm)
    return token


async def authenticate_user(user_crud: UserCRUD, username: str, password: str) -> Union[UserInDB, None]:
    user = await user_crud.get_one(username)
    if user is None:
        return None
    user = UserInDB(**user)
    if not pwd_context.verify(password, user.password_hash):
        return None
    return user


@router.post("/token", response_model=Token)
async def get_token(form_data: OAuth2PasswordRequestForm = Depends(), user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD))):
    user = await authenticate_user(user_crud, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Incorrect username or password",
        )

    # form_data.scopes temporary
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes}
    )
    return {"access_token": access_token, "token_type": "bearer"}
