import pydantic


class UpdateStatusScheme(pydantic.BaseModel):
    user_id: int
    status: bool
