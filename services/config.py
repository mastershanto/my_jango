from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from config.env import get_env, get_env_bool


@dataclass(frozen=True)
class AISettings:
    openai_api_key: str | None
    openai_model: str
    fastapi_host: str
    fastapi_port: int
    django_ai_base_url: str
    request_timeout: float
    debug: bool


@lru_cache(maxsize=1)
def get_ai_settings() -> AISettings:
    host = get_env("FASTAPI_HOST", "127.0.0.1") or "127.0.0.1"
    port = int(get_env("FASTAPI_PORT", "8001") or "8001")
    base_url = get_env("DJANGO_AI_BASE_URL", f"http://{host}:{port}")

    return AISettings(
        openai_api_key=get_env("OPENAI_API_KEY"),
        openai_model=get_env("OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini",
        fastapi_host=host,
        fastapi_port=port,
        django_ai_base_url=base_url or f"http://{host}:{port}",
        request_timeout=float(get_env("AI_REQUEST_TIMEOUT", "30") or "30"),
        debug=get_env_bool("DEBUG", True),
    )
