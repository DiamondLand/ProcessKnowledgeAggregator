import pydantic


class UpdateStatusScheme(pydantic.BaseModel):
    login: str
    status: bool
