from . import user_api
from fastapi import APIRouter

router = APIRouter()
router.include_router(user_api.router, prefix="/users")