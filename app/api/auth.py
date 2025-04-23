import datetime

from fastapi import APIRouter, Response, Request
from jose import jwt, JWTError
from sqlalchemy import select

from app.db.base import async_session
from app.exceptions import (UserAlreadyExistsException,
                            UserNotExistsException,
                            InvalidPasswordException,
                            UserIdNotFoundException,
                            TokenExpiredException,
                            RefreshTokenNotFound,
                            InvalidRefreshTokenException)
from app.models.user import User as MUser
from app.models.shader import Shader as MShader
from app.schemas.auth.user_login import UserLogin
from app.schemas.auth.user_register import UserRegister
from app.security.utils import get_password_hash, verify_password, create_refresh_token, create_access_token
from app.settings import settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register")
async def register(user: UserRegister):
    async with async_session() as session:
        result = await session.execute(
            select(MUser)
            .where(MUser.email == user.email)
        )
        existing_user = result.scalar()
        if existing_user:
            raise UserAlreadyExistsException
        hashed_password = get_password_hash(user.password)
        user = MUser(
            email=str(user.email),
            name=user.name,
            hashed_password=hashed_password,
            role="USER",
            created_at=datetime.datetime.now(datetime.UTC).replace(tzinfo=None),
            avatar_url="",
            biography=""
        )
        session.add(user)
        await session.commit()


@router.post("/login")
async def login(response: Response, user: UserLogin):
    async with async_session() as session:
        result = await session.execute(
            select(MUser)
            .where(MUser.email == user.email)
        )
        existing_user = result.scalar()
        if not existing_user:
            raise UserNotExistsException

        password_is_valid = verify_password(user.password, existing_user.hashed_password)
        if not password_is_valid:
            raise InvalidPasswordException
        access_token = create_access_token({"sub": str(existing_user.id)})
        refresh_token = create_refresh_token({"sub": str(existing_user.id)})
        response.set_cookie("access_token", access_token, httponly=True)
        response.set_cookie("refresh_token", refresh_token, httponly=True)
        return {
            "message": "Successfully logged in",
        }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "Successfully logged out"}


@router.post("/refresh")
async def refresh(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise RefreshTokenNotFound
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise InvalidRefreshTokenException
    user_id = payload.get('sub')
    if not user_id:
        raise UserIdNotFoundException

    async with async_session() as session:
        result = await session.execute(select(MUser).where(MUser.id == int(user_id)))
        user = result.scalars().first()
    if not user:
        raise UserNotExistsException

    if payload.get('exp') < datetime.datetime.now(datetime.UTC).timestamp():
        raise TokenExpiredException
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("access_token", access_token, httponly=True)
    return {
        "message": "Successfully refreshed token"
    }


@router.get("/me")
async def get_me(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return None

    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None

    if payload.get('exp') < datetime.datetime.now(datetime.UTC).timestamp():
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    async with async_session() as session:
        result = await session.execute(select(MUser).where(MUser.id == int(user_id)))
        user = result.scalars().first()

    if not user:
        raise UserNotExistsException

    return {"name": user.name, "id": user.id}


