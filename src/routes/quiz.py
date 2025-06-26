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
    새로운 복합 유형(O/X, 4지선다, 주관식) 퀴즈를 랜덤으로 3개 생성합니다.
    (주관식은 최대 1개만 포함됩니다.)
    """
    try:
        # 이제 quiz_generator는 문제 딕셔너리의 '리스트'를 반환합니다.
        generated_questions = await quiz_generator.generate_quiz_from_chatgpt(request)

        # QuizResponse 스키마에 맞게 최종 응답 데이터를 구성합니다.
        response_data = {
            "topic": request.topic,
            "difficulty": request.difficulty,
            "questions": generated_questions,  # 생성된 문제 리스트를 그대로 할당
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
