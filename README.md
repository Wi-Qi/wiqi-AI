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

### API 문서 확인
```
Swagger UI: http://localhost:8000/docs
```