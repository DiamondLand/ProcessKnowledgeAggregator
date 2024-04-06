import pydantic

from typing import Optional


class CreateQuestion(pydantic.BaseModel):
    user_id: int
    tag: Optional[str]
    question: Optional[str]


class CreateAnswer(pydantic.BaseModel):
    user_id: int
    question_id: int
    answer: str


class UpdateStatus(pydantic.BaseModel):
    user_id: int
    part_id: int
    status: bool


class UpdateVotes(pydantic.BaseModel):
    user_id: int
    part_id: int
    number: int
