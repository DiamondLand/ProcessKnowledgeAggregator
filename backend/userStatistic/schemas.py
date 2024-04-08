import pydantic


class UpdateDataScheme(pydantic.BaseModel):
    login: str
    number: int
