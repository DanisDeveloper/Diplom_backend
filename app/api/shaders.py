import datetime
from sqlalchemy import func
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.params import Depends, Query
from sqlalchemy import select
from starlette.responses import Response

from app.db.base import async_session
from app.models.like import Like as MLike
from app.models.shader import Shader as MShader
from app.models.user import User as MUser
from app.schemas.shader.shader import Shader
from app.security.dependencies import get_current_user_id

router = APIRouter(
    prefix="/shaders",
    tags=["shaders"],
)


@router.get("/")
async def get_all_visible_shaders(response: Response, page: int = Query(default=1, ge=1)):
    async with async_session() as session:
        result = await session.execute(
            select(MShader.id,
                   MShader.title,
                   MShader.code,
                   MShader.user_id,
                   MUser.name.label("username"),
                   func.count(MLike.id).label("likes"))
            .join(MUser, MShader.user_id == MUser.id)
            .outerjoin(MLike, MShader.id == MLike.shader_id)
            .where(MShader.visibility == True)
            .group_by(MShader.id, MUser.name)
            .order_by(MShader.created_at.desc())  # TODO сделать сортировку на будщее
        )
        shaders = result.mappings().all()
        response.headers["X-Total-Count"] = str((len(shaders) - 1) // 12 + 1)
        return shaders[(page - 1) * 12: page * 12]


@router.get("/{shader_id}")
async def get_shader_by_id(shader_id: int, request: Request):
    if request.cookies.get("access_token") is None:
        async with async_session() as session:
            result = await session.execute(
                select(MShader, MUser.name.label("username"))
                .join(MUser, MShader.user_id == MUser.id)
                .where(MShader.id == shader_id)
            )
            shader, username = result.first()
            if shader is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shader not found")

            return {"shader": shader, "is_liked": None, "username": username}

    else:
        user_id: int = await get_current_user_id(request)

        async with async_session() as session:
            result = await session.execute(
                select(MShader, MLike.id.label("is_liked"), MUser.name.label("username"))
                .join(MUser, MShader.user_id == MUser.id)
                .outerjoin(MLike, (MLike.shader_id == MShader.id) & (MLike.user_id == user_id))
                .where(MShader.id == shader_id)
            )
            shader, is_liked, username = result.first()
            if shader is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shader not found")

            if not shader.visibility:
                if shader.user_id != user_id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                        detail="User is not the owner of the shader")

        return {"shader": shader, "is_liked": is_liked is not None, "username": username}


@router.post("/")
async def upsert_shader(
        body: Shader,
        user_id: int = Depends(get_current_user_id)
):
    if body.id is None:  # INSERT
        async with async_session() as session:
            new_shader = MShader(
                title=body.title,
                description=body.description,
                code=body.code,
                visibility=body.visibility,
                user_id=user_id,
                created_at=datetime.datetime.now(datetime.UTC).replace(tzinfo=None),
                updated_at=datetime.datetime.now(datetime.UTC).replace(tzinfo=None),
                id_forked=body.id_forked
            )
            session.add(new_shader)
            await session.commit()
            await session.refresh(new_shader)
            return new_shader

    else:  # UPDATE
        async with async_session() as session:
            shader = await session.execute(
                select(MShader).where(MShader.id == body.id)
            )
            if shader is None:
                raise HTTPException(status_code=404, detail="Shader not found")

            shader = shader.scalars().first()
            shader.title = body.title
            shader.description = body.description
            shader.code = body.code
            shader.visibility = body.visibility
            shader.updated_at = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
            await session.commit()
            await session.refresh(shader)
            return shader
