from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base
from pydantic import BaseModel
from typing import List


class Questions(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, index=True)

class Choices(Base):
    __tablename__ = 'choices'

    id = Column(Integer, primary_key=True, index=True)
    choice_text = Column(String, index=True)
    is_correct = Column(Boolean, default=False)
    question_id = Column(Integer, ForeignKey("questions.id"))

class ChoiceUpdate(BaseModel):
    choice_text: str
    is_correct: bool

class QuestionUpdateRequest(BaseModel):
    updated_question_text: str
    updated_choices: List[ChoiceUpdate]  # Danh sách các lựa chọn
