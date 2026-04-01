from typing import Optional

from pydantic import BaseModel


class QuestionOption(BaseModel):
    label: str
    text: str


class Question(BaseModel):
    id: int
    section: str
    type: str
    question: str
    passage: Optional[str] = None
    options: Optional[list[QuestionOption]] = None
    correctAnswer: Optional[str] = None
