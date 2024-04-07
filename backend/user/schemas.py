import pydantic


class CreateUserScheme(pydantic.BaseModel):
    user_id: int
    contacts: str
    login: str
    password: str


class AddToBlackListScheme(pydantic.BaseModel):
    user_id: int
    reason: str
