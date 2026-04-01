import json
import os

from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from app.types.question import Question


class Skill(BaseModel):
    score: int = Field(..., ge=0, le=100)
    comment: str


class EvaluationResponse(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    level: str
    overall_summary: str
    emoji: str
    skills: dict[str, Skill]
    top_strength: str
    top_weakness: str
    improvement_tip: str


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured")
    return OpenAI(api_key=api_key)


def build_questions_text(
    questions: list[Question],
    answers: dict[int | str, str],
) -> str:
    blocks: list[str] = []

    for index, question in enumerate(questions, start=1):
        answer_label = answers.get(str(question.id)) or answers.get(question.id)

        selected = None
        correct = None

        if question.options:
            selected = next(
                (option for option in question.options if option.label == answer_label),
                None,
            )
            correct = next(
                (
                    option
                    for option in question.options
                    if option.label == question.correctAnswer
                ),
                None,
            )

        block = f"Q{index} [{question.section}/{question.type}]"

        if question.passage:
            block += f"\nPassage: {question.passage}"

        block += f"\nQuestion: {question.question}"

        if question.options:
            block += "\nOptions:"
            for option in question.options:
                block += f"\n{option.label}. {option.text}"

            selected_text = selected.text if selected else ""
            block += f"\nStudent Answer: {answer_label} ({selected_text})"

            if correct:
                block += f"\nCorrect Answer: {correct.label} ({correct.text})"
        else:
            block += f"\nStudent Answer: {answer_label}"

        blocks.append(block)

    return "\n\n".join(blocks)


def evaluate(
    student_name: str,
    student_class: int,
    questions: list[Question],
    answers: dict[int | str, str],
) -> dict:
    client = get_openai_client()
    questions_text = build_questions_text(questions, answers)

    system_prompt = """
You are an expert English evaluator for Indian school students.
Return strict JSON only.

Scoring rules:
- All scores must be integers between 0 and 100.
- Be consistent: average students are around 50-70, strong students 75-90.
- Keep comments concise, constructive, and age-appropriate.
""".strip()

    user_prompt = f"""
Evaluate the student's performance and produce a JSON object with this shape:
{{
  "overall_score": 0,
  "level": "string",
  "overall_summary": "string",
  "emoji": "string",
  "skills": {{
    "reading": {{"score": 0, "comment": "string"}},
    "grammar": {{"score": 0, "comment": "string"}},
    "vocabulary": {{"score": 0, "comment": "string"}},
    "comprehension": {{"score": 0, "comment": "string"}}
  }},
  "top_strength": "string",
  "top_weakness": "string",
  "improvement_tip": "string"
}}

Student Name: {student_name}
Class: {student_class}

Questions and answers:
{questions_text}
""".strip()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = response.choices[0].message.content or "{}"

    try:
        parsed = EvaluationResponse.model_validate(json.loads(content))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError(f"Invalid evaluation response from model: {exc}") from exc

    return parsed.model_dump()
