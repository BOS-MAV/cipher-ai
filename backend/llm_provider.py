import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

from pathlib import Path
from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parent / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)

print("Loading .env from:", ENV_FILE)
print("Exists:", ENV_FILE.exists())
print("LLM_PROVIDER from environment:", os.getenv("LLM_PROVIDER"))

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2"
)

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.4-mini"
)


def ask_llm(
    prompt: str,
    json_schema: dict | None = None
) -> str:

    if LLM_PROVIDER == "ollama":
        return _ask_ollama(
            prompt,
            json_schema
        )

    if LLM_PROVIDER == "openai":
        return _ask_openai(
            prompt,
            json_schema
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER: {LLM_PROVIDER}"
    )


def _ask_ollama(
    prompt: str,
    json_schema: dict | None
) -> str:

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    if json_schema is not None:
        payload["format"] = json_schema

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=180
    )

    response.raise_for_status()

    return response.json()["response"]


def _ask_openai(
    prompt: str,
    json_schema: dict | None
) -> str:

    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"]
    )

    if json_schema is None:

        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt
        )

        return response.output_text

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "cipher_action",
                "strict": True,
                "schema": json_schema
            }
        }
    )

    return response.output_text