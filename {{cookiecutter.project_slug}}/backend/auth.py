from os import access
from typing import List, Optional, Union
from pydantic import BaseModel, ValidationError
from .configuration import config
from passlib.context import CryptContext
from fastapi.security import (
    Oauth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from fastapi import APIRouter, HTTPException, status, Depends
from .crud.user_crud import UserCRUD, UserIn
from .crud.deps import get_crud_obj
from jose import JWTError, jwt

# Based on https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    scopes: List[str] = []


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = Oauth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "admin": "Do actions that require super user capabilities",
        "me": "Current user",
    },
)

router = APIRouter(tags=["Authentication"])


async def authenticate_user(username: str, password: str) -> Union[UserIn, None]:
    user = await get_crud_obj(UserCRUD)().get_one(username)
    if user is None:
        return None
    user = UserIn(**user)
    if not pwd_context.verify(password, user.password_hash):
        return None
    return user


def create_access_token(data: dict) -> str:
    datacopy = data.copy()
    datacopy.update({"exp": config.token_expire})
    token = jwt.encode(datacopy, config.secret_key, algorithm=config.algorithm)
    return token


async def get_current_user(
    sscopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD)),
):
    if sscopes.scopes:
        authenticate_value = f'Bearer scope="{sscopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    cred_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        decoded_token = jwt.decode(
            token, config.secret_key, algorithms=[config.algorithm]
        )
        username: str = decoded_token.get("sub")  # sub is subject of JWT token
        if username is None:
            raise cred_exception
        token_scopes = decoded_token.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except (JWTError, ValidationError):
        raise cred_exception

    user = await user_crud.get_one(token_data.username)
    if user is None:
        raise cred_exception

    for scope in sscopes.scopes:
        if scope not in sscopes.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate", authenticate_value},
            )

    return user

@router.post("/token")
def get_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found. Incorrect username or password")
    
    # form_data.scopes temporary
    access_token = create_access_token(data={"sub": user.username, "scopes": form_data.scopes})
    return {"access_token": access_token, "token_type": "bearer"}
