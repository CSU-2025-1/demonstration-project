from pydantic import BaseModel


class UserRead(BaseModel):
    id: int
    username: str
    role: str


class UserCreate(BaseModel):
    username: str
    password: str
