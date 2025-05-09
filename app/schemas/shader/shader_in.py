from pydantic import BaseModel


class ShaderIn(BaseModel):
    id: int | None
    title: str
    description: str
    code: str
    visibility: bool
    id_forked: int | None