
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker


from app.settings import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.USER}:{settings.PASSWORD}@{settings.ADDRESS}:{settings.PORT}/{settings.DB_NAME}"

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()
