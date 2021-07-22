from . import item_api, user_api
from fastapi import APIRouter

router = APIRouter()
router.include_router(item_api.router, prefix="/items")
router.include_router(user_api.router, prefix="/users")