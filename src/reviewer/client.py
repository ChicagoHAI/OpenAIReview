"""OpenRouter API client."""

import os
import sys
import time

from openai import OpenAI

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_client() -> OpenAI:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print(
            "Error: OPENROUTER_API_KEY is not set.\n\n"
            "Set it as an environment variable:\n"
            "  export OPENROUTER_API_KEY=your_key_here\n\n"
            "Or create a .env file in the project root:\n"
            "  OPENROUTER_API_KEY=your_key_here\n\n"
            "Get your API key at https://openrouter.ai/keys",
            file=sys.stderr,
        )
        sys.exit(1)
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)


REASONING_EFFORT_RATIO = {
    "none": 0,
    "low": 0.1,
    "medium": 0.5,
    "high": 0.8,
}


def chat(
    messages: list[dict],
    model: str = "anthropic/claude-opus-4-5",
    temperature: float | None = None,
    max_tokens: int = 4096,
    reasoning_effort: str | None = None,
    retries: int = 3,
) -> tuple[str, dict]:
    """Call the OpenRouter chat API. Returns (response_text, usage_dict).

    reasoning_effort: None (adaptive default), or "none"/"low"/"medium"/"high".
    """
    client = get_client()
    for attempt in range(retries):
        try:
            kwargs = dict(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
            )
            if temperature is not None:
                kwargs["temperature"] = temperature
            if reasoning_effort is not None:
                if reasoning_effort == "none":
                    # No reasoning at all
                    pass
                else:
                    ratio = REASONING_EFFORT_RATIO.get(reasoning_effort, 0.5)
                    budget = max(int(max_tokens * ratio), 1024)
                    kwargs["extra_body"] = {
                        "reasoning": {"max_tokens": budget}
                    }
            resp = client.chat.completions.create(**kwargs)
            usage = {
                "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
                "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
                "model": model,
            }
            return resp.choices[0].message.content, usage
        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt
            print(f"  API error (attempt {attempt+1}): {e}. Retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError("All retries exhausted")
