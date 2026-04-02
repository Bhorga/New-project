from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from app.routers.question import router as question_router


load_dotenv()

app = FastAPI(
    title="LLM Tools API",
    version="0.1.0",
    description="Minimal FastAPI backend for evaluation and transcription APIs.",
)


# Configure CORS
origins = [origin.strip() for origin in os.getenv("FRONTEND_URL").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(question_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
