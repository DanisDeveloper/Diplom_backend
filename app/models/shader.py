from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, ForeignKey

from app.db.base import Base


class Shader(Base):
    __tablename__ = "shaders"
    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String, nullable=False)
    description = Column(String)
    code = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)
    visibility = Column(Boolean, nullable=False, default=True)
    id_forked = Column(Integer, nullable=True, default=None)

    # Внешние ключи
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
