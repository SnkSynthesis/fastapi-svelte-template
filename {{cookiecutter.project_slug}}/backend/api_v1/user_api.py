from fastapi import APIRouter, Depends, Security, status, Request
from fastapi.exceptions import HTTPException
from ..crud.user_crud import UserCRUD, User, UserIn, UserInDB
from ..crud.deps import get_crud_obj
from ..auth.deps import get_current_user
from ..auth.api import create_access_token
from ..auth.context import pwd_context
from ..configuration import config
from typing import Any, List, Mapping, Union
from starlette.responses import Response


router = APIRouter(tags=["User API"])


def get_response_via_scopes(scopes: List[str]) -> Union[List[str], Response]:
    if scopes is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        return scopes


@router.get("/{username}", response_model=User)
async def get_one_user(
    username: str, user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD))
) -> Any:
    user = await user_crud.get_one(username)
    if user is None:
        raise HTTPException(detail="Not Found", status_code=status.HTTP_404_NOT_FOUND)
    return user


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserIn, user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD))
) -> Any:
    last_record_username = await user_crud.create(user)
    return await user_crud.get_one(last_record_username)


@router.put("/{old_username}/{new_username}", response_model=User)
async def update_user_username(
    new_username: str,
    user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD)),
    current_user: UserInDB = Security(get_current_user, scopes=["update_user"]),
) -> Any:
    user = await user_crud.get_one(current_user.username)
    if user is None:
        raise HTTPException(detail="Not Found", status_code=status.HTTP_404_NOT_FOUND)
    await user_crud.update_username(current_user.username, new_username)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{username}")
async def update_current_users_password(
    username: str,
    request: Request,
    user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD)),
    current_user: UserInDB = Security(get_current_user, scopes=[""]),
) -> Any:
    body = await request.json()
    old_password = body.get("old_password")
    new_password = body.get("new_password")
    if old_password is None or new_password is None:
        raise HTTPException(
            detail="Invalid request body",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    if not pwd_context.verify(old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    await user_crud.update_password(current_user.username, new_password)


@router.put("/me/{new_username}")
async def update_current_users_username(
    new_username: str,
    user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD)),
    current_user: UserInDB = Security(get_current_user),
) -> Any:
    user = await user_crud.get_one(current_user.username)
    if user is None:
        raise HTTPException(detail="Not Found", status_code=status.HTTP_404_NOT_FOUND)
    await user_crud.update_username(current_user.username, new_username)
    access_token = create_access_token(
        data={"sub": new_username, "scopes": await user_crud.get_scopes(new_username)}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.put("/me")
async def update_current_users_password(
    request: Request,
    user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD)),
    current_user: UserInDB = Security(get_current_user),
) -> Any:
    body = await request.json()
    old_password = body.get("old_password")
    new_password = body.get("new_password")
    if old_password is None or new_password is None:
        raise HTTPException(
            detail="Invalid request body",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    if not pwd_context.verify(old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/me/scopes")
async def get_current_users_scopes(
    user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD)),
    current_user: UserInDB = Security(get_current_user),
):
    return get_response_via_scopes(await user_crud.get_scopes(current_user.username))


@router.post("/scopes/{username}/{scope}")
async def add_scope(
    username: str,
    scope: str,
    user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD)),
    current_user: UserInDB = Security(get_current_user, scopes=["admin:add_scope"]),
) -> Any:
    if scope not in config.scopes:
        raise HTTPException("Invalid scope", status_code=status.HTTP_400_BAD_REQUEST)
    if user_crud.get_one(username) is None:
        raise HTTPException("User not found", status_code=status.HTTP_404_NOT_FOUND)
    await user_crud.add_scope(username, scope)
    return Response(status_code=status.HTTP_201_CREATED)


@router.delete("/scopes/{username}/{scope}")
async def delete_scope(
    username: str,
    scope: str,
    user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD)),
    current_user: UserInDB = Security(get_current_user, scopes=["admin:delete_scope"]),
) -> Any:
    if scope not in config.scopes:
        raise HTTPException("Invalid scope", status_code=status.HTTP_400_BAD_REQUEST)
    if user_crud.get_one(username) is None:
        raise HTTPException("User not found", status_code=status.HTTP_404_NOT_FOUND)
    await user_crud.delete_scope(username, scope)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/scopes/{username}")
async def get_scopes(
    username: str,
    user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD)),
    current_user: UserInDB = Security(get_current_user, scopes=["admin:read_scopes"])
) -> Any:
    return get_response_via_scopes(await user_crud.get_scopes(username))


@router.delete("/{username}")
async def delete_user(
    username: str, user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD)), current_user: UserInDB = Security(get_current_user, scopes=["admin:edit_user"])
) -> Any:
    user = await user_crud.get_one(username)
    if user is None:
        raise HTTPException(detail="Not Found", status_code=status.HTTP_404_NOT_FOUND)
    await user_crud.delete(username)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
