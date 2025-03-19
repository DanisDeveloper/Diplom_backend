from pydantic import EmailStr, BaseModel


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str