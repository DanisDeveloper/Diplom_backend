import datetime
from sqlalchemy import func, distinct
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.params import Depends, Query
from sqlalchemy import select
from starlette.responses import Response

from app.db.base import async_session
from app.models.like import Like as MLike
from app.models.comment import Comment as MComment
from app.models.shader import Shader as MShader
from app.models.user import User as MUser
from app.schemas.shader.shader import Shader
from app.security.dependencies import get_current_user_id

router = APIRouter(
    prefix="/shaders",
    tags=["shaders"],
)


@router.get("/")
async def get_all_visible_shaders(
        response: Response,
        page: int = Query(default=1, ge=1),
        sort: str = Query(default="Newest")
):

    match sort:
        case 'Liked':
            sort_option = func.count(distinct(MLike.id)).desc()
        case 'Commented':
            sort_option = func.count(distinct(MComment.id)).desc()
        case _: # 'Newest'
            sort_option = MShader.created_at.desc()

    async with async_session() as session:
        result = await session.execute(
            select(MShader.id,
                   MShader.title,
                   MShader.code,
                   MShader.user_id,
                   MUser.name.label("username"),
                   func.count(distinct(MLike.id)).label("likes"),
                   func.count(distinct(MComment.id)).label("comments"))
            .join(MUser, MShader.user_id == MUser.id)
            .outerjoin(MLike, MShader.id == MLike.shader_id)
            .outerjoin(MComment, MShader.id == MComment.shader_id)
            .where(MShader.visibility == True)
            .group_by(MShader.id, MUser.name)
            .order_by(sort_option)
        )
        shaders = result.mappings().all()
        response.headers["X-Total-Count"] = str((len(shaders) - 1) // 12 + 1)
        return shaders[(page - 1) * 12: page * 12]


@router.get("/{shader_id}")
async def get_shader_by_id(shader_id: int, request: Request):
    response_data = None
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

            response_data = {"shader": shader, "is_liked": None, "username": username}

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


        response_data = {"shader": shader, "is_liked": is_liked is not None, "username": username}

    async with async_session() as session:
        result = await session.execute(
            select(MComment, MUser.name.label("username"), MUser.avatar_url.label("avatar_url"))
            .join(MUser, MComment.user_id == MUser.id)
            .where(MComment.shader_id == shader_id)
            .order_by(MComment.created_at.desc())
        )
        rows = result.all()
        comments = []
        for comment, username, avatar_url in rows:
            comments.append({
                "id": comment.id,
                "text": comment.text if not comment.hidden else "Hidden",
                "hidden": comment.hidden,
                "created_at": comment.created_at,
                "user_id": comment.user_id,
                "shader_id": comment.shader_id,
                "username": username,
                "avatar_url": avatar_url,
            })
    response_data["comments"] = comments
    return response_data

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


@router.delete("/{shader_id}")
async def delete_shader(shader_id: int, user_id: int = Depends(get_current_user_id)):
    async with async_session() as session:
        shader = await session.execute(
            select(MShader).where(MShader.id == shader_id)
        )
        if shader is None:
            raise HTTPException(status_code=404, detail="Shader not found")

        shader = shader.scalars().first()
        if shader.user_id != user_id:
            raise HTTPException(status_code=403, detail="User is not the owner of the shader")

        await session.delete(shader)
        await session.commit()
        return