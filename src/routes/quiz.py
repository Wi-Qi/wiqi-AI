# src/routes/quiz.py

from fastapi import APIRouter, HTTPException, status
from src.schemas.quiz_schema import QuizCreateRequest, QuizResponse
from src.components import quiz_generator

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"],
)


@router.post(
    "/generate", response_model=QuizResponse, status_code=status.HTTP_201_CREATED
)
async def create_quiz(request: QuizCreateRequest):
    """
    새로운 복합 유형 퀴즈를 랜덤으로 3개 생성하고 번호를 부여합니다.
    """
    try:
        generated_questions_list = await quiz_generator.generate_quiz_from_chatgpt(
            request
        )

        numbered_questions = []
        for i, question_data in enumerate(generated_questions_list, start=1):
            question_data["question_number"] = i
            numbered_questions.append(question_data)

        response_data = {
            "questions": numbered_questions,
            "topic": request.topic,
            "difficulty_level": request.difficulty_level,
        }

        return response_data

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"알 수 없는 오류가 발생했습니다: {e}",
        )
