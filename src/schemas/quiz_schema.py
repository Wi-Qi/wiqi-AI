from pydantic import BaseModel, Field
from typing import List, Optional, Union


# --- Request Schema ---
class QuizCreateRequest(BaseModel):
    topic: str
    difficulty_level: int = Field(5, ge=1, le=10)


# --- Response Schemas for each question type ---
class OxQuestion(BaseModel):
    question_number: int
    question_type: str
    question: str
    answer: bool
    explanation: Optional[str] = None


class MultipleChoiceQuestion(BaseModel):
    question_number: int
    question_type: str
    question: str
    options: List[str]
    answer: str
    explanation: Optional[str] = None


class ShortAnswerQuestion(BaseModel):
    question_number: int
    question_type: str
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
