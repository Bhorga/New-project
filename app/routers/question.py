import logging
import os
import tempfile
import traceback

from fastapi import APIRouter, File, HTTPException, UploadFile
from openai import OpenAI
from pydantic import BaseModel

from app.services.question_util import evaluate
from app.types.question import Question


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/question", tags=["question"])


class EvaluationRequest(BaseModel):
    studentName: str
    studentClass: int
    questions: list[Question]
    answers: dict[int | str, str]


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured",
        )
    return OpenAI(api_key=api_key)


@router.post("/evaluate")
async def evaluate_student(payload: EvaluationRequest) -> dict:
    try:
        return evaluate(
            payload.studentName,
            payload.studentClass,
            payload.questions,
            payload.answers,
        )
    except Exception as exc:
        logger.debug("Error during evaluation: %s", exc)
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)) -> dict[str, str]:
    temp_path = None

    try:
        if not audio.content_type or not audio.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="Invalid file type")

        suffix = os.path.splitext(audio.filename or "audio.webm")[1] or ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_path = temp_audio.name

        client = get_openai_client()
        with open(temp_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_file,
            )

        transcript = response.text.strip()
        if not transcript:
            raise HTTPException(status_code=500, detail="Empty transcription")

        return {"transcript": transcript}

    except HTTPException:
        raise
    except Exception as exc:
        logger.debug("Error during audio transcription: %s", exc)
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
