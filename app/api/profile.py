import os
import pathlib
import uuid

from fastapi import APIRouter, Request, UploadFile, Depends
from sqlalchemy import select
import shutil
from app.exceptions import UserNotExistsException
from app.models.user import User as MUser
from app.models.shader import Shader as MShader
from app.db.base import async_session
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/profile",
    tags=["profile"],
)


@router.get("/{user_id}")
async def get_profile_by_id(user_id: int, request: Request):
    async with async_session() as session:
        result = await session.execute(select(MUser).where(MUser.id == int(user_id)))
        user = result.scalars().first()

    if not user:
        raise UserNotExistsException

    async with async_session() as session:
        result = await session.execute(
            select(MShader).where(MShader.user_id == int(user_id))
        )
        shaders = result.scalars().all()

    user_data = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "biography": user.biography,
        "avatar_url": user.avatar_url,
        "created_at": user.created_at,
        "shaders": shaders
    }
    # TODO сделать запрос на получение всех публичных шейдеров для всех и приватных для авторизованного пользователя
    return user_data


@router.post("/avatar")
async def upload_avatar(avatar: UploadFile, user: MUser = Depends(get_current_user)):
    ext = pathlib.Path(avatar.filename).suffix
    filename = f"{uuid.uuid4().hex}{ext}"
    avatar_url = f"avatars/{filename}"

    with open(f"public/{avatar_url}", "wb+") as f:
        shutil.copyfileobj(avatar.file, f)

    async with async_session() as session:
        user.avatar_url = avatar_url
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return {"avatar_url": avatar_url}
