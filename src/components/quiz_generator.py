import json
import asyncio
import random
from openai import AsyncOpenAI
from src.config.settings import settings
from src.schemas.quiz_schema import QuizCreateRequest

# --- 설정 및 공통 프롬프트 정의 ---
GPT_MODEL = "gpt-4.1-nano"
BASE_SYSTEM_PROMPT = "당신은 간단한 퀴즈 풀이 문제를 만드는 전문가입니다. 사용자의 요청에 따라 지정된 주제와 난이도에 맞는 퀴즈를 생성합니다."
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


# --- 새로운 내부 헬퍼 함수: 반복되는 GPT API 호출 로직 ---
async def _call_gpt_for_quiz(system_prompt: str, user_prompt: str) -> dict:
    """
    시스템/유저 프롬프트를 받아 GPT API를 호출하고 결과를 반환하는 공통 함수
    """
    response = await client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    return json.loads(response.choices[0].message.content)


# --- 각 문제 유형별 생성 함수 (difficulty_level 사용하도록 수정) ---
async def _generate_ox_question(topic: str, difficulty_level: int) -> dict:
    """O/X 퀴즈 1개를 생성합니다."""
    specific_prompt = """
    O/X 퀴즈 1개를 생성해야 합니다.
    - JSON 구조: {"question_type": "O/X", "question": "질문 내용", "answer": true, "explanation": "정답 해설"}
    - 'answer' 필드는 반드시 boolean 타입인 `true` 또는 `false`여야 합니다.
    """
    final_system_prompt = f"{BASE_SYSTEM_PROMPT}\n\n반드시 다음 규칙을 지켜 JSON 형식으로만 응답해야 합니다.\n{specific_prompt}"
    # 사용자 프롬프트에 숫자 난이도를 명확히 전달
    user_prompt = (
        f"주제: {topic}, 난이도 (1~10, 10이 가장 어려움): {difficulty_level}/10"
    )

    return await _call_gpt_for_quiz(final_system_prompt, user_prompt)


async def _generate_multiple_choice_question(topic: str, difficulty_level: int) -> dict:
    """4지선다형 퀴즈 1개를 생성합니다."""
    specific_prompt = """
    4지선다형 퀴즈 1개를 생성해야 합니다.
    - JSON 구조: {"question_type": "객관식", "question": "질문 내용", "options": ["선택지1", "선택지2", "선택지3", "선택지4"], "answer": "정답 선택지", "explanation": "정답 해설"}
    - 'options' 필드는 항상 4개의 선택지를 포함해야 합니다.
    """
    final_system_prompt = f"{BASE_SYSTEM_PROMPT}\n\n반드시 다음 규칙을 지켜 JSON 형식으로만 응답해야 합니다.\n{specific_prompt}"
    # 사용자 프롬프트에 숫자 난이도를 명확히 전달
    user_prompt = (
        f"주제: {topic}, 난이도 (1~10, 10이 가장 어려움): {difficulty_level}/10"
    )

    return await _call_gpt_for_quiz(final_system_prompt, user_prompt)


async def _generate_short_answer_question(topic: str, difficulty_level: int) -> dict:
    """주관식 퀴즈 1개를 생성합니다."""
    specific_prompt = """
    주관식(단답형) 퀴즈 1개를 생성해야 합니다.
    - JSON 구조: {"question_type": "주관식", "question": "...", "answer": "가장 정확한 정답", "similar_answers": ["유사 답안1"], "explanation": "..."}
    - 'similar_answers' 필드에는 맞다고 인정할 수 있는 동의어, 다른 표현 등을 포함합니다.
    """
    final_system_prompt = f"{BASE_SYSTEM_PROMPT}\n\n반드시 다음 규칙을 지켜 JSON 형식으로만 응답해야 합니다.\n{specific_prompt}"
    # 사용자 프롬프트에 숫자 난이도를 명확히 전달
    user_prompt = (
        f"주제: {topic}, 난이도 (1~10, 10이 가장 어려움): {difficulty_level}/10"
    )

    return await _call_gpt_for_quiz(final_system_prompt, user_prompt)


# --- 메인 함수 (difficulty_level 사용하도록 수정) ---
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
        types_to_generate.extend(random.choices(["ox", "mc"], k=2))
    else:
        types_to_generate.extend(random.choices(["ox", "mc"], k=3))

    random.shuffle(types_to_generate)

    try:
        tasks = []
        for q_type in types_to_generate:
            # request_data.difficulty 대신 difficulty_level을 전달합니다.
            task = generators[q_type](request_data.topic, request_data.difficulty_level)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                raise result

        return results

    except Exception as e:
        print(f"Error generating random quiz composite: {e}")
        raise ValueError("퀴즈 생성에 실패했습니다.")
