import json
import asyncio
import random
from openai import AsyncOpenAI
from typing import List
from src.config.settings import settings
from src.schemas.quiz_schema import QuizCreateRequest

# --- 설정 및 공통 프롬프트 정의 ---
GPT_MODEL = "gpt-4.1-nano"
BASE_SYSTEM_PROMPT = "당신은 간단한 퀴즈 풀이 문제를 만드는 전문가입니다. 사용자의 요청에 따라 지정된 주제와 난이도에 맞는 퀴즈를 생성합니다. 영어 topic에서도 예시 문장, 단어를 제외하면 문제를 최대한 한국어로 작성해야 합니다."
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
        temperature=0.9,
    )
    return json.loads(response.choices[0].message.content)


# --- 각 문제 유형별 생성 함수 (f-string 오류 수정) ---
async def _generate_ox_question(
    topic: str, difficulty_level: int, existing_questions: List[str]
) -> dict:
    """O/X 퀴즈 1개를 생성합니다."""
    specific_prompt = """
    O/X 퀴즈 1개를 생성해야 합니다.
    - JSON 구조: {"question_type": "ox", "question": "질문 내용", "answer": true, "explanation": "정답 해설"}
    - 'question_type' 필드의 값은 항상 "ox"여야 합니다.
    """
    final_system_prompt = f"{BASE_SYSTEM_PROMPT}\n\n반드시 다음 규칙을 지켜 JSON 형식으로만 응답해야 합니다.\n{specific_prompt}"
    user_prompt = (
        f"주제: {topic}, 난이도 (1~10, 10이 가장 어려움): {difficulty_level}/10"
    )
    if existing_questions:
        # [오류 수정] f-string 밖에서 문자열을 미리 만듭니다.
        previous_questions_str = "\n- ".join(existing_questions)
        user_prompt += f"\n\n다음 문제들과는 다른 내용의 새로운 문제를 생성해주세요:\n- {previous_questions_str}"
    return await _call_gpt_for_quiz(final_system_prompt, user_prompt)


async def _generate_multiple_choice_question(
    topic: str, difficulty_level: int, existing_questions: List[str]
) -> dict:
    """4지선다형 퀴즈 1개를 생성합니다."""
    specific_prompt = """
    4지선다형 퀴즈 1개를 생성해야 합니다.
    - JSON 구조: {"question_type": "multiple_choice", "question": "질문 내용", "options": ["선택지1", "선택지2", "선택지3", "선택지4"], "answer": "정답 선택지", "explanation": "정답 해설"}
    - 'question_type' 필드의 값은 항상 "multiple_choice"여야 합니다.
    """
    final_system_prompt = f"{BASE_SYSTEM_PROMPT}\n\n반드시 다음 규칙을 지켜 JSON 형식으로만 응답해야 합니다.\n{specific_prompt}"
    user_prompt = (
        f"주제: {topic}, 난이도 (1~10, 10이 가장 어려움): {difficulty_level}/10"
    )
    if existing_questions:
        # [오류 수정] f-string 밖에서 문자열을 미리 만듭니다.
        previous_questions_str = "\n- ".join(existing_questions)
        user_prompt += f"\n\n다음 문제들과는 다른 내용의 새로운 문제를 생성해주세요:\n- {previous_questions_str}"
    return await _call_gpt_for_quiz(final_system_prompt, user_prompt)


async def _generate_short_answer_question(
    topic: str, difficulty_level: int, existing_questions: List[str]
) -> dict:
    """주관식 퀴즈 1개를 생성합니다."""
    specific_prompt = """
    주관식(단답형) 퀴즈 1개를 생성해야 합니다.
    - JSON 구조: {"question_type": "short_answer", "question": "...", "answer": "가장 정확한 정답", "similar_answers": ["유사 답안1"], "explanation": "..."}
    - 'question_type' 필드의 값은 항상 "short_answer"여야 합니다.
    """
    final_system_prompt = f"{BASE_SYSTEM_PROMPT}\n\n반드시 다음 규칙을 지켜 JSON 형식으로만 응답해야 합니다.\n{specific_prompt}"
    user_prompt = (
        f"주제: {topic}, 난이도 (1~10, 10이 가장 어려움): {difficulty_level}/10"
    )
    if existing_questions:
        # [오류 수정] f-string 밖에서 문자열을 미리 만듭니다.
        previous_questions_str = "\n- ".join(existing_questions)
        user_prompt += f"\n\n다음 문제들과는 다른 내용의 새로운 문제를 생성해주세요:\n- {previous_questions_str}"
    return await _call_gpt_for_quiz(final_system_prompt, user_prompt)


# --- 메인 함수 (순차 생성 방식으로 변경) ---
async def generate_quiz_from_chatgpt(request_data: QuizCreateRequest) -> list:
    """
    순차적으로 문제를 생성하여 중복을 방지하고, 최종 3개의 퀴즈를 반환합니다.
    """
    generators = {
        "ox": _generate_ox_question,
        "mc": _generate_multiple_choice_question,
        "sa": _generate_short_answer_question,
    }

    # 생성할 문제 유형 3개를 랜덤으로 선택
    types_to_generate = []
    base_pool = ["ox", "mc"]
    if random.choice([True, False]):
        types_to_generate.append("sa")
        types_to_generate.extend(random.choices(base_pool, k=2))
    else:
        types_to_generate.extend(random.choices(base_pool, k=3))
    random.shuffle(types_to_generate)

    # 최종 결과를 담을 리스트와, 생성된 문제 텍스트를 추적할 리스트
    final_results = []
    existing_question_texts = []

    try:
        # 3개의 문제를 순차적으로 생성
        for q_type in types_to_generate:
            generator_func = generators[q_type]

            # 생성 함수 호출 시, 이전에 만들어진 문제 텍스트 목록을 전달
            new_question = await generator_func(
                topic=request_data.topic,
                difficulty_level=request_data.difficulty_level,
                existing_questions=existing_question_texts,
            )

            # 결과 및 문제 텍스트 저장
            final_results.append(new_question)
            if isinstance(new_question, dict) and "question" in new_question:
                existing_question_texts.append(new_question["question"])

        return final_results

    except Exception as e:
        print(f"Error in generate_quiz_from_chatgpt: {e}")
        raise ValueError("퀴즈 생성에 실패했습니다. 잠시 후 다시 시도해 주세요.")
