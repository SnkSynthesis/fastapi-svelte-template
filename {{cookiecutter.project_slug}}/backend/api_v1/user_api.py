from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from ..crud.user_crud import UserCRUD, User, UserIn
from ..crud.deps import get_crud_obj
from typing import Any
from starlette.responses import Response


router = APIRouter(tags=["User API"])


@router.get("/{username}", response_model=User)
async def get_one_user(
    username: str, user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD))
) -> Any:
    user = await user_crud.get_one(username)
    if user is None:
        raise HTTPException(detail="Not Found", status_code=status.HTTP_404_NOT_FOUND)
    return user


@router.post("/", response_model=User)
async def create_user(
    user: UserIn, user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD))
) -> Any:
    last_record_username = await user_crud.create(user)
    return await user_crud.get_one(last_record_username)


@router.put("/", response_model=User)
async def update_user(
    updated_user: UserIn, user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD))
) -> Any:
    user = await user_crud.get_one(updated_user.username)
    if user is None:
        raise HTTPException(detail="Not Found", status_code=status.HTTP_404_NOT_FOUND)
    await user_crud.update(updated_user.username, updated_user)
    return {**updated_user.dict()}


@router.delete("/{username}")
async def delete_user(
    username: str, user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD))
) -> Any:
    user = await user_crud.get_one(username)
    if user is None:
        raise HTTPException(detail="Not Found", status_code=status.HTTP_404_NOT_FOUND)
    await user_crud.delete(username)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
