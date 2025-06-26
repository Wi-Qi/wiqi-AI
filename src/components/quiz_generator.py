import json
from openai import AsyncOpenAI
from src.config.settings import settings
from src.schemas.quiz_schema import QuizCreateRequest

# OpenAI 클라이언트 초기화
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_quiz_from_chatgpt(request_data: QuizCreateRequest) -> dict:
    """
    ChatGPT API를 사용하여 요청된 주제에 대한 퀴즈를 생성합니다.
    """
    system_prompt = f"""
    당신은 지정된 주제와 난이도에 맞는 객관식 퀴즈를 생성하는 전문가입니다.
    반드시 다음 규칙을 지켜 JSON 형식으로만 응답해야 합니다.
    
    - JSON 구조: {{ "questions": [ {{ "question": "...", "options": ["...", "...", "...", "..."], "answer": "...", "explanation": "..." }} ] }}
    - 'options' 배열에는 항상 4개의 선택지를 포함해야 합니다.
    - 'answer'는 'options' 배열에 있는 텍스트와 정확히 일치해야 합니다.
    - 'explanation' 필드에는 정답에 대한 간결한 해설을 포함해야 합니다.
    """

    user_prompt = f"주제: {request_data.topic}, 문제 수: {request_data.num_questions}, 난이도: {request_data.difficulty}에 대한 퀴즈를 생성해 주세요."

    try:
        response = await client.chat.completions.create(
            model="gpt-4-turbo",  # 또는 gpt-3.5-turbo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},  # JSON 모드 활성화
            temperature=0.7,
        )

        quiz_data = json.loads(response.choices[0].message.content)
        return quiz_data

    except Exception as e:
        print(f"Error generating quiz: {e}")
        # 실제 프로덕션에서는 더 정교한 예외 처리가 필요합니다.
        raise ValueError("퀴즈 생성에 실패했습니다.")
