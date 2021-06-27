from fastapi import APIRouter, Depends
from starlette.responses import Response
from ..crud.deps import get_crud_obj
from ..crud.item_crud import ItemCRUD, Item, ItemIn
from typing import List

router = APIRouter(tags=["Item API"])


@router.get("/", response_model=List[Item])
async def get_all_items(item_crud=Depends(get_crud_obj(ItemCRUD))):
    return await item_crud.get_all()


@router.get("/{id}", response_model=Item)
async def get_one_item(id: int, item_crud=Depends(get_crud_obj(ItemCRUD))):
    return await item_crud.get_one(id)


@router.post("/", response_model=Item)
async def create_item(item: ItemIn, item_crud=Depends(get_crud_obj(ItemCRUD))):
    last_record_id = item_crud.create(item)
    # return await item_crud.get_one(last_record_id)


@router.put("/{id}", response_model=Item)
async def update_item(
    id: int, updated_item: ItemIn, item_crud=Depends(get_crud_obj(ItemCRUD))
):
    item_crud.update(id, updated_item)
    return updated_item


@router.delete("/{id}", response_model=Item)
async def delete_item(id: int, item_crud=Depends(get_crud_obj(ItemCRUD))):
    item_crud.delete(id)
    return Response(status_code=204)
