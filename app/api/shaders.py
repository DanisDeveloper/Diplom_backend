from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import select

from app.db.base import async_session
from app.models.user import User as MUser
from app.models.shader import Shader as MShader
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/shaders",
    tags=["shaders"],
)


@router.get("/")
async def get_shaders():
    async with async_session() as session:
        result = await session.execute(
            select(MShader)
            .where(MShader.visibility == True)
        )
        return result.scalars().all()


@router.post("/")
async def add_shaders(user: MUser = Depends(get_current_user)):
    async with async_session() as session:
        pass