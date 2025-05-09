from pydantic import BaseModel
from datetime import datetime

class ShaderOut(BaseModel):
    id: int
    title: str
    description: str
    code: str
    visibility: bool
    created_at: datetime
    updated_at: datetime
    user_id: int
    id_forked: int | None

    class Config:
        from_attributes = True
