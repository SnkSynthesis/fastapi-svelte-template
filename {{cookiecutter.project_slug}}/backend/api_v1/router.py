from . import item_api
from fastapi import APIRouter

router = APIRouter()
router.include_router(item_api.router, prefix="/items")
