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
    새로운 복합 유형(O/X, 4지선다, 주관식) 퀴즈를 생성합니다.
    """
    try:
        generated_data = await quiz_generator.generate_quiz_from_chatgpt(request)
        if not generated_data:
            raise ValueError("퀴즈 생성에 실패했습니다. 입력 데이터를 확인하세요.")
        response_data = {
            "topic": request.topic,
            "difficulty": request.difficulty,
            "ox_question": generated_data.get("ox_question"),
            "multiple_choice_question": generated_data.get("multiple_choice_question"),
            "short_answer_question": generated_data.get("short_answer_question"),
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
