from fastapi import FastAPI
from src.routes import quiz

app = FastAPI(
    title="Quiz Generator API",
    description="ChatGPT API를 사용하여 동적으로 퀴즈를 생성하는 API입니다.",
    version="1.0.0",
)

app.include_router(quiz.router, prefix="")


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Quiz Generator API!"}


# 서버 실행: 터미널에서 uvicorn main:app --reload
