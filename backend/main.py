import os
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from llm_provider import LLM_PROVIDER, OLLAMA_MODEL, OPENAI_MODEL
from cipher_agent import answer_question

app = FastAPI(
    title="CIPHER AI Gateway",
    version="0.2.0",
    description="Natural-language gateway to the CIPHER Web API using Ollama.",
)

origins = [
    "https://bos-mav.github.io",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

print("CORS origins:", origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

RATE_LIMIT_PER_HOUR = int(
    os.getenv("RATE_LIMIT_PER_HOUR", "30")
)

_rate_windows: dict[str, deque[float]] = defaultdict(deque)
_rate_lock = Lock()


class AskRequest(BaseModel):
    question: str = Field(
        min_length=2,
        max_length=4000
    )


class AskResponse(BaseModel):
    answer: str
    action: dict
    structured: dict[str, Any] | None = None
    cipher_data: Any = None


def _check_rate_limit(ip: str) -> None:
    now = time.time()
    cutoff = now - 3600

    with _rate_lock:
        window = _rate_windows[ip]

        while window and window[0] < cutoff:
            window.popleft()

        if len(window) >= RATE_LIMIT_PER_HOUR:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again later."
            )

        window.append(now)


@app.get("/health")
def health() -> dict:
    if LLM_PROVIDER == "openai":
        model = OPENAI_MODEL
    else:
        model = OLLAMA_MODEL

    return {
        "status": "ok",
        "llm_provider": LLM_PROVIDER,
        "model": model
    }

@app.post(
    "/api/ask",
    response_model=AskResponse
)
def ask(
    body: AskRequest,
    request: Request
) -> AskResponse:

    forwarded = request.headers.get(
        "x-forwarded-for"
    )

    ip = (
        forwarded.split(",")[0].strip()
        if forwarded
        else (
            request.client.host
            if request.client
            else "unknown"
        )
    )

    _check_rate_limit(ip)

    try:
        result = answer_question(
            body.question
        )

        return AskResponse(
            answer=result["answer"],
            action=result["action"],
            structured=result.get("structured"),
            cipher_data=result.get("cipher_data")
        )

    except Exception as exc:
        print(
            f"ERROR {type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Upstream service error: "
                f"{type(exc).__name__}"
            )
        ) from exc
