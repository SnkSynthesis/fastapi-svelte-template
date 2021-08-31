from fastapi import HTTPException, status, Depends
from fastapi.security import SecurityScopes
from jose import jwt, JWTError
from .context import oauth2_scheme, TokenData
from ..crud.user_crud import UserCRUD, UserInDB
from pydantic import ValidationError
from ..crud.deps import get_crud_obj
from ..configuration import config

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
    # try:
    decoded_token = jwt.decode(
        token, config.secret_key, algorithms=[config.algorithm]
    )
    username: str = decoded_token.get("sub")  # sub is subject of JWT token
    if username is None:
        raise cred_exception
    token_scopes = decoded_token.get("scopes", [])
    token_data = TokenData(username=username, scopes=token_scopes)
    # except (JWTError, ValidationError):
        
    #     raise cred_exception

    user = await user_crud.get_one(token_data.username)
    if user is None:
        raise cred_exception

    for scope in sscopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate", authenticate_value},
            )

    return UserInDB(**user)