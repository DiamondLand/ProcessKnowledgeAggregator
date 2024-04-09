import pydantic

from typing import Optional


class CreateQuestion(pydantic.BaseModel):
    login: str
    tag: Optional[str]
    question: Optional[str]


class UpdateQuestion(pydantic.BaseModel):
    question_id: int
    login: str
    tag: Optional[str]
    question: Optional[str]


class CreateAnswer(pydantic.BaseModel):
    login: str
    question_id: int
    answer: str


class UpdateStatus(pydantic.BaseModel):
    login: str
    part_id: int
    status: bool


class UpdateVotes(pydantic.BaseModel):
    login: str
    part_id: int
    number: int
