from sqlalchemy import ForeignKey, Integer, TIMESTAMP, Column, String

from app.db.base import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)

    # Внешние ключи
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shader_id = Column(Integer, ForeignKey("shaders.id"), nullable=False)
