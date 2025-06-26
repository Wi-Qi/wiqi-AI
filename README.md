# wiqi-AI

## Wi-Qi: AI 퀴즈 생성 API
특정 주제에 대한 퀴즈를 동적으로 생성하는 API 서버입니다. 사용자는 원하는 주제, 난이도를 지정하여 고품질의 객관식 퀴즈를 JSON 형식으로 받을 수 있습니다.

### ✨ 주요 기능
**동적 퀴즈 생성**: 원하는 주제, 문제 수, 난이도를 기반으로 실시간 퀴즈 생성

**JSON 형식 응답**: ChatGPT가 생성한 퀴즈를 표준화된 JSON 형식으로 제공

**자동 API 문서**: FastAPI의 Swagger UI (/docs)를 통해 자동 생성된 인터랙티브 API 문서 제공

**안전한 키 관리**: .env 파일을 통해 OpenAI API 키를 안전하게 관리


### 📂 프로젝트 구조
```
.
├── .env                  # 환경 변수 (OpenAI API 키 등)
├── requirements.txt      # 프로젝트 의존성 관리
├── main.py               # FastAPI 앱 초기화 및 실행
└── src/
    ├── config/
    │   └── settings.py   # 환경 변수 로드 및 설정 관리
    ├── components/
    │   └── quiz_generator.py # ChatGPT와 통신하여 퀴즈를 생성하는 로직
    ├── routes/
    │   └── quiz.py       # '/quiz' 경로에 대한 라우터 정의
    └── schemas/
        └── quiz_schema.py  # Pydantic을 이용한 데이터 유효성 검사 모델
```

### 의존성 설치
```
pip install -r requirements.txt
```

### 서버 실행
```
uvicorn main:app --reload
```


### 📖 API 사용법
#### 퀴즈 생성하기
**Endpoint**: `POST /quiz/generate`

**Description**: `주어진 주제와 난이도로 새로운 퀴즈 3개를 생성합니다. (주관식은 최대 1개 포함)`


### 요청 예시 (Request)
#### Request Body:
```
{
  "topic": "문학",
  "difficulty_level": 5
}
```

#### curl 명령어:
```
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/quiz/generate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "topic": "문학",
    "difficulty_level": 5
  }'
```

### 응답 예시 (Response)

```
{
  "topic": "문학",
  "difficulty_level": 5,
  "questions": [
    {
      "question_number": 1,
      "question_type": "multiple_choice",
      "question": "다음 중 조지 오웰의 소설 제목이 아닌 것은 무엇입니까?",
      "options": [
        "1984년",
        "동물농장",
        "파리와 런던",
        "위대한 유산"
      ],
      "answer": "위대한 유산",
      "explanation": "위대한 유산은 찰스 디킨스의 소설로, 조지 오웰과는 관련이 없습니다."
    },
    {
      "question_number": 2,
      "question_type": "short_answer",
      "question": "이 문학 작품은 프랑스의 작가 빅토르 위고가 쓴 것으로, 19세기 프랑스의 사회적 현실을 배경으로 한 소설입니다. 제목은 무엇일까요?",
      "answer": "레 미제라블",
      "similar_answers": [
        "레 미제라블"
      ],
      "explanation": "이 작품은 빅토르 위고가 쓴 대표적인 소설로, 19세기 프랑스의 사회 문제와 혁명에 관한 이야기를 담고 있습니다."
    },
    {
      "question_number": 3,
      "question_type": "multiple_choice",
      "question": "아래 중 셰익스피어의 작품이 아닌 것은 무엇입니까?",
      "options": [
        "햄릿",
        "오셀로",
        "로미오와 줄리엣",
        "돈키호테"
      ],
      "answer": "돈키호테",
      "explanation": "돈키호테는 스페인 작가 미구엘 데 세르반테스가 쓴 작품으로, 셰익스피어의 작품이 아닙니다."
    }
  ]
}
```

### ⚙️ API 문서 자동 확인
보다 자세한 내용 확인 및 API 테스트는 서버 실행 후 아래 주소에서 가능합니다.

Swagger UI: `http://localhost:8000/docs`

ReDoc: `http://localhost:8000/redoc`