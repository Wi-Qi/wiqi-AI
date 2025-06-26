import json
import asyncio
from openai import AsyncOpenAI
from src.config.settings import settings
from src.schemas.quiz_schema import QuizCreateRequest

# OpenAI 클라이언트 초기화
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


# --- 내부 헬퍼 함수: 각 문제 유형별 생성 ---


async def _generate_ox_question(topic: str, difficulty: str) -> dict:
    """O/X 퀴즈 1개를 생성합니다."""
    system_prompt = """
    당신은 지정된 주제와 난이도에 맞는 O/X 퀴즈를 1개 생성하는 전문가입니다.
    반드시 다음 규칙을 지켜 JSON 형식으로만 응답해야 합니다.
    - JSON 구조: {"question": "질문 내용", "answer": true, "explanation": "정답 해설"}
    - 'answer' 필드는 반드시 boolean 타입인 `true` 또는 `false`여야 합니다.
    """
    user_prompt = (
        f"주제: {topic}, 난이도: {difficulty}에 대한 O/X 퀴즈 1개를 생성해 주세요."
    )

    response = await client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    return json.loads(response.choices[0].message.content)


async def _generate_multiple_choice_question(topic: str, difficulty: str) -> dict:
    """4지선다형 퀴즈 1개를 생성합니다."""
    system_prompt = """
    당신은 지정된 주제와 난이도에 맞는 4지선다형 퀴즈를 1개 생성하는 전문가입니다.
    반드시 다음 규칙을 지켜 JSON 형식으로만 응답해야 합니다.
    - JSON 구조: {"question": "질문 내용", "options": ["선택지1", "선택지2", "선택지3", "선택지4"], "answer": "정답 선택지", "explanation": "정답 해설"}
    - 'options' 필드는 항상 4개의 선택지를 포함해야 합니다.
    - 'answer'는 'options'에 포함된 내용과 정확히 일치해야 합니다.
    """
    user_prompt = f"주제: {topic}, 난이도: {difficulty}에 대한 4지선다형 퀴즈 1개를 생성해 주세요."

    response = await client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    return json.loads(response.choices[0].message.content)


async def _generate_short_answer_question(topic: str, difficulty: str) -> dict:
    """주관식 퀴즈 1개를 생성합니다. (유사 답안 포함)"""
    system_prompt = """
    당신은 지정된 주제와 난이도에 맞는 주관식(단답형) 퀴즈를 1개 생성하는 전문가입니다.
    반드시 다음 규칙을 지켜 JSON 형식으로만 응답해야 합니다.
    - JSON 구조: {"question": "...", "answer": "가장 정확한 정답", "similar_answers": ["유사 답안1", "유사 답안2"], "explanation": "..."}
    - 'answer' 필드에는 가장 대표적이고 정확한 답을 기입합니다.
    - 'similar_answers' 필드에는 맞다고 인정할 수 있는 동의어, 다른 표현, 띄어쓰기로 인한 유사 답안 또는 흔한 오타 등을 문자열 배열(list) 형태로 포함합니다.
    - 만약 유사 답안이 없다면, 이 필드를 생략하거나 빈 배열 `[]`로 설정할 수 있습니다.
    """
    user_prompt = (
        f"주제: {topic}, 난이도: {difficulty}에 대한 주관식 퀴즈 1개를 생성해 주세요."
    )

    response = await client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    return json.loads(response.choices[0].message.content)


# --- 메인 함수: 각 퀴즈 생성 함수를 동시에 호출하고 결과를 조합 ---


async def generate_quiz_from_chatgpt(request_data: QuizCreateRequest) -> dict:
    """
    각 문제 유형별 생성 함수를 동시에 호출하여 복합 유형 퀴즈를 생성합니다.
    """
    try:
        # 세 가지 유형의 퀴즈 생성을 위한 비동기 작업 목록 생성
        tasks = [
            _generate_ox_question(request_data.topic, request_data.difficulty),
            _generate_multiple_choice_question(
                request_data.topic, request_data.difficulty
            ),
            _generate_short_answer_question(
                request_data.topic, request_data.difficulty
            ),
        ]

        # asyncio.gather를 사용하여 모든 작업을 동시에 실행하고 결과를 기다림
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 결과 중 예외가 있는지 확인
        for result in results:
            if isinstance(result, Exception):
                # 예외가 발생하면 에러를 다시 발생시켜 상위 핸들러가 처리하도록 함
                raise result

        # 성공적인 결과들을 변수에 할당
        ox_res, mc_res, sa_res = results

        # 최종 응답 형식에 맞게 결과를 조합하여 반환
        return {
            "ox_question": ox_res,
            "multiple_choice_question": mc_res,
            "short_answer_question": sa_res,
        }

    except Exception as e:
        print(f"Error generating quiz composite: {e}")
        # routes/quiz.py의 예외 처리 블록으로 전달될 에러
        raise ValueError("퀴즈 생성에 실패했습니다.")
