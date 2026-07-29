from __future__ import annotations

import os

from providers.openai_provider import OpenAIProvider


class DeepSeekProvider(OpenAIProvider):
    """DeepSeek provider using its OpenAI-compatible Chat Completions API."""

    def __init__(self) -> None:
        super().__init__(
            api_key_env="DEEPSEEK_API_KEY",
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            default_model="deepseek-v4-flash",
            extra_body={"thinking": {"type": "disabled"}},
        )
