from pydantic import BaseModel
from typing import List, Optional


# --- Request Schemas ---
class QuizCreateRequest(BaseModel):
    topic: str
    num_questions: int = 5
    difficulty: str = "중급"


# --- Response Schemas ---
class Question(BaseModel):
    question: str
    options: List[str]
    answer: str
    explanation: Optional[str] = None


class QuizResponse(BaseModel):
    topic: str
    difficulty: str
    questions: List[Question]
