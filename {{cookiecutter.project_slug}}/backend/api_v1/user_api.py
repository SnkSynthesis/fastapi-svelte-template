from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from ..crud.user_crud import UserCRUD, User, UserIn
from ..crud.deps import get_crud_obj
from typing import Any
from starlette.responses import Response


router = APIRouter(tags=["User API"])

@router.get("/{id}", response_model=User)
async def get_one_users(id: int, user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD))) -> Any:
    user = await user_crud.get_one(id)
    if user is None:
        raise HTTPException(detail="Not Found", status_code=404)
    return user

@router.post("/", response_model=User)
async def create_user(user: UserIn, user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD))) -> Any:
    last_record_id = await user_crud.create(user)
    return await user_crud.get_one(last_record_id)

@router.put("/{id}", response_model=User)
async def update_user(id: int, updated_user: UserIn, user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD))) -> Any:
    user = await user_crud.get_one(id)
    if user is None:
        raise HTTPException(detail="Not Found", status_code=404)
    await user_crud.update(id, updated_user)
    return {"id": id, **updated_user.dict()}


@router.delete("/{id}")
async def delete_user(id: int, user_crud: UserCRUD = Depends(get_crud_obj(UserCRUD))) -> Any:
    user = await user_crud.get_one(id)
    if user is None:
        raise HTTPException(detail="Not Found", status_code=404)
    await user_crud.delete(id)
    return Response(status_code=204)
