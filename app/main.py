from fastapi import FastAPI
from dotenv import load_dotenv

from app.routers.question import router as question_router


load_dotenv()

app = FastAPI(
    title="LLM Tools API",
    version="0.1.0",
    description="Minimal FastAPI backend for evaluation and transcription APIs.",
)

app.include_router(question_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
