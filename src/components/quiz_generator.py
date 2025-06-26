import json
import asyncio
import random
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


async def generate_quiz_from_chatgpt(request_data: QuizCreateRequest) -> list:
    """
    정해진 규칙에 따라 랜덤한 유형의 퀴즈 3개를 생성합니다.
    (주관식은 최대 1개)
    """
    generators = {
        "ox": _generate_ox_question,
        "mc": _generate_multiple_choice_question,
        "sa": _generate_short_answer_question,
    }

    types_to_generate = []

    if random.choice([True, False]):
        types_to_generate.append("sa")
        # 나머지 2개는 O/X 또는 객관식 중에서 랜덤으로 선택
        types_to_generate.extend(random.choices(["ox", "mc"], k=2))
    else:
        # 주관식을 포함하지 않을 경우, O/X, 객관식 중에서만 3개 랜덤 선택
        types_to_generate.extend(random.choices(["ox", "mc"], k=3))

    # 생성할 문제 유형 리스트를 무작위로 섞어줍니다.
    random.shuffle(types_to_generate)

    try:
        tasks = []
        for q_type in types_to_generate:
            task = generators[q_type](request_data.topic, request_data.difficulty)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                raise result

        return results

    except Exception as e:
        print(f"Error generating random quiz composite: {e}")
        raise ValueError("퀴즈 생성에 실패했습니다.")
