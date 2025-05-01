from pydantic import BaseModel

class PostComment(BaseModel):
    text: str
