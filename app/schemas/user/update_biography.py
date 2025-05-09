from pydantic import BaseModel


class UpdateBiography(BaseModel):
    biography: str