import pydantic


class CreateUserScheme(pydantic.BaseModel):
    contacts: str
    login: str
    password: str


class AddToBlackListScheme(pydantic.BaseModel):
    login: str
    reason: str


class ChangeStatusScheme(pydantic.BaseModel):
    login: str
    status: bool
