# src/schemas/quiz_schema.py

from pydantic import BaseModel
from typing import List, Optional


# --- Request Schema ---
class QuizCreateRequest(BaseModel):
    topic: str
    difficulty: str = "중급"


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
class QuizResponse(BaseModel):
    topic: str
    difficulty: str
    ox_question: OxQuestion
    multiple_choice_question: MultipleChoiceQuestion
    short_answer_question: ShortAnswerQuestion
