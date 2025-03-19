from pydantic import EmailStr, BaseModel


class UserLogin(BaseModel):
    email: EmailStr
    password: str
