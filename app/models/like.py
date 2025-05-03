from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP

from app.db.base import Base


class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False)

    # Внешние ключи
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    shader_id = Column(Integer, ForeignKey("shaders.id", ondelete="CASCADE"), nullable=False)
