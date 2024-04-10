import pydantic


class CreateUserScheme(pydantic.BaseModel):
    user_id: int
    contacts: str
    login: str
    password: str


class AuthorizationUserScheme(pydantic.BaseModel):
    user_id: int
    login: str
    password: str


class AddToBlackListScheme(pydantic.BaseModel):
    login: str
    reason: str


class SubsctribeTagScheme(pydantic.BaseModel):
    login: str
    tag: str


class ChangeStatusScheme(pydantic.BaseModel):
    login: str
    status: bool
