# src/schemas/quiz_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional, Union


# --- Request Schema ---
class QuizCreateRequest(BaseModel):
    topic: str
    # 난이도 1-10 사이의 정수로 정의, 숫자가 높을수록 어려운 문제
    difficulty_level: int = Field(5, ge=1, le=10)


# --- Response Schemas for each question type ---
class OxQuestion(BaseModel):
    question: str
    answer: bool  # O/X 문제이므로 boolean 타입 (True/False)
    explanation: Optional[str] = None


class MultipleChoiceQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str
    explanation: Optional[str] = None


class ShortAnswerQuestion(BaseModel):
    question: str
    answer: str
    similar_answers: Optional[List[str]] = None
    explanation: Optional[str] = None


# --- Main Response Schema ---

AnyQuestion = Union[OxQuestion, MultipleChoiceQuestion, ShortAnswerQuestion]


class QuizResponse(BaseModel):
    topic: str
    difficulty_level: int
    questions: List[AnyQuestion]
