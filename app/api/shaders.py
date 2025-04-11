from fastapi import APIRouter
from fastapi.params import Depends

from app.db.base import async_session
from app.models.user import User as MUser
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/shaders",
    tags=["shaders"],
)


@router.get("/")
async def get_shaders(user: MUser = Depends(get_current_user)):
    print(user)
    return {
        "shaders": ["1", "2"]
    }

@router.post("/")
async def add_shaders(user: MUser = Depends(get_current_user)):
    async with async_session() as session:
        pass