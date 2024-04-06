import pydantic


class UpdateDataScheme(pydantic.BaseModel):
    user_id: int
    number: int
