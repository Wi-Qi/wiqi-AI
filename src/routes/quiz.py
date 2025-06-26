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
    새로운 퀴즈를 생성합니다.

    - **topic**: 퀴즈 주제 (예: "한국사")
    - **num_questions**: 생성할 문제 수 (기본값: 5)
    - **difficulty**: 난이도 (기본값: "중급")
    """
    try:
        generated_data = await quiz_generator.generate_quiz_from_chatgpt(request)

        # Pydantic 모델을 사용하여 응답 데이터 구조 검증 및 조합
        response_data = {
            "topic": request.topic,
            "difficulty": request.difficulty,
            "questions": generated_data.get("questions", []),
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
