from pydantic import BaseModel


class UpdatePassword(BaseModel):
    oldPassword: str
    newPassword: str