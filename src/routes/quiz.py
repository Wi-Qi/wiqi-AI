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
    새로운 복합 유형 퀴즈를 랜덤으로 3개 생성합니다.
    - topic: 퀴즈 주제
    - difficulty_level: 난이도 (1~10, 기본값 5)
    """
    try:
        generated_questions = await quiz_generator.generate_quiz_from_chatgpt(request)

        # QuizResponse 스키마에 맞게 최종 응답 데이터를 구성합니다.
        response_data = {
            "topic": request.topic,
            # request.difficulty 대신 request.difficulty_level을 사용합니다.
            "difficulty_level": request.difficulty_level,
            "questions": generated_questions,
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
