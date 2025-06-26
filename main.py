from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import quiz

app = FastAPI(
    title="Quiz Generator API",
    description="ChatGPT API를 사용하여 동적으로 퀴즈를 생성하는 API입니다.",
    version="1.0.0",
)

origins = [
    "http://localhost",
    "http://localhost:3000",  # React 기본 포트
    "http://localhost:5173",  # Vite 기본 포트
    "http://localhost:8080",  # Vue 기본 포트
    "*",  # 개발 시 모든 출처를 허용 (가장 관대한 설정)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 허용할 출처 목록
    allow_credentials=True,  # 쿠키를 포함한 요청 허용 여부
    allow_methods=["*"],  # 허용할 HTTP 메소드 (GET, POST 등)
    allow_headers=["*"],  # 허용할 HTTP 헤더
)

app.include_router(quiz.router, prefix="")


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Quiz Generator API!"}


# 서버 실행: 터미널에서 uvicorn main:app --reload
