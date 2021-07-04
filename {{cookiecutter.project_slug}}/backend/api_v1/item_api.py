from typing import Any, Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from ..crud.deps import get_crud_obj
from ..crud.item_crud import ItemCRUD, Item, ItemIn

router = APIRouter(tags=["Item API"])

common_additional_responses: Dict[Union[int, str], Dict[str, Any]] = {
    404: {
        "description": "Item was not found.",
        "content": {"application/json": {"example": {"detail": "Not Found"}}},
    }
}


@router.get("/", response_model=List[Item], responses=common_additional_responses)
async def get_all_items(item_crud: ItemCRUD = Depends(get_crud_obj(ItemCRUD))) -> Any:
    return await item_crud.get_all()


@router.get("/{id}", response_model=Item, responses=common_additional_responses)
async def get_one_item(
    id: int, item_crud: ItemCRUD = Depends(get_crud_obj(ItemCRUD))
) -> Any:
    item = await item_crud.get_one(id)
    if item is None:
        raise HTTPException(detail="Not Found", status_code=404)
    return item


@router.post("/", response_model=Item, responses=common_additional_responses)
async def create_item(
    item: ItemIn, item_crud: ItemCRUD = Depends(get_crud_obj(ItemCRUD))
) -> Any:
    last_record_id = await item_crud.create(item)
    return await item_crud.get_one(last_record_id)


@router.put("/{id}", response_model=Item, responses=common_additional_responses)
async def update_item(
    id: int, updated_item: ItemIn, item_crud: ItemCRUD = Depends(get_crud_obj(ItemCRUD))
) -> Any:
    item = await item_crud.get_one(id)
    if item is None:
        raise HTTPException(detail="Not Found", status_code=404)
    await item_crud.update(id, updated_item)
    return {"id": id, **updated_item.dict()}


@router.delete(
    "/{id}",
    responses={
        204: {"description": "Successfully deleted. No content."},
        **common_additional_responses,
    },
    status_code=204,
)
async def delete_item(
    id: int, item_crud: ItemCRUD = Depends(get_crud_obj(ItemCRUD))
) -> Any:
    item = await item_crud.get_one(id)
    if item is None:
        raise HTTPException(detail="Not Found", status_code=404)
    await item_crud.delete(id)
    return Response(status_code=204)
