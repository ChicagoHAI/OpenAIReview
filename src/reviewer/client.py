"""API client with support for OpenRouter, OpenAI, Anthropic, and Gemini."""

import os
import sys
import time

from openai import OpenAI

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Provider configs: (env_var, base_url or None for default, provider_name, model_prefix_to_strip)
PROVIDERS = [
    ("OPENROUTER_API_KEY", "https://openrouter.ai/api/v1", "openrouter", None),
    ("OPENAI_API_KEY", None, "openai", None),
    ("ANTHROPIC_API_KEY", "https://api.anthropic.com/v1/", "anthropic", "anthropic/"),
    ("GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/openai/", "gemini", "google/"),
]


def get_client() -> tuple[OpenAI, str, str | None]:
    """Return (client, provider_name, prefix_to_strip) for the first available API key."""
    for env_var, base_url, provider, prefix in PROVIDERS:
        api_key = os.environ.get(env_var)
        if api_key:
            kwargs = {"api_key": api_key}
            if base_url:
                kwargs["base_url"] = base_url
            display = env_var.replace("_API_KEY", "").replace("_", " ").title()
            print(f"  Using {display} API")
            return OpenAI(**kwargs), provider, prefix

    print(
        "Error: No API key found.\n\n"
        "Set one of the following environment variables:\n"
        "  export OPENROUTER_API_KEY=...   # OpenRouter (supports all models)\n"
        "  export OPENAI_API_KEY=...       # OpenAI native\n"
        "  export ANTHROPIC_API_KEY=...    # Anthropic native\n"
        "  export GEMINI_API_KEY=...       # Google Gemini native\n\n"
        "Or create a .env file in your working directory.\n"
        "See .env.example for a template.",
        file=sys.stderr,
    )
    sys.exit(1)


REASONING_EFFORT_RATIO = {
    "none": 0,
    "low": 0.1,
    "medium": 0.5,
    "high": 0.8,
}

# Max retries when response is empty (likely reasoning used all tokens)
EMPTY_RESPONSE_MAX_RETRIES = 3
EMPTY_RESPONSE_TOKEN_MULTIPLIER = 2


def _apply_reasoning(kwargs: dict, provider: str, reasoning_effort: str, max_tokens: int) -> None:
    """Add provider-specific reasoning/thinking parameters to the API call."""
    ratio = REASONING_EFFORT_RATIO.get(reasoning_effort, 0.5)
    budget = max(int(max_tokens * ratio), 1024)

    if provider == "openrouter":
        kwargs["extra_body"] = {"reasoning": {"max_tokens": budget}}
    elif provider == "anthropic":
        kwargs["extra_body"] = {"thinking": {"type": "enabled", "budget_tokens": budget}}
    elif provider == "openai":
        # OpenAI uses reasoning_effort directly as a string
        kwargs["reasoning_effort"] = reasoning_effort
    elif provider == "gemini":
        kwargs["extra_body"] = {"thinking": {"type": "enabled", "budget_tokens": budget}}


def chat(
    messages: list[dict],
    model: str = "anthropic/claude-opus-4-6",
    temperature: float | None = None,
    max_tokens: int = 16384,
    reasoning_effort: str | None = None,
    retries: int = 3,
) -> tuple[str, dict]:
    """Call a chat API. Returns (response_text, usage_dict).

    Automatically selects the provider based on available API keys.
    Model names with provider prefixes (e.g. "anthropic/claude-opus-4-6")
    are stripped when using native APIs.

    reasoning_effort: None (adaptive default), or "none"/"low"/"medium"/"high".

    If the response is empty (e.g. reasoning consumed all tokens), retries
    with doubled max_tokens up to EMPTY_RESPONSE_MAX_RETRIES times.
    """
    client, provider, prefix_to_strip = get_client()
    api_model = model
    if prefix_to_strip and api_model.startswith(prefix_to_strip):
        api_model = api_model[len(prefix_to_strip):]

    current_max_tokens = max_tokens
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "model": model}

    for empty_attempt in range(EMPTY_RESPONSE_MAX_RETRIES):
        for attempt in range(retries):
            try:
                kwargs = dict(
                    model=api_model,
                    messages=messages,
                    max_tokens=current_max_tokens,
                )
                if temperature is not None:
                    kwargs["temperature"] = temperature
                if reasoning_effort is not None and reasoning_effort != "none":
                    _apply_reasoning(kwargs, provider, reasoning_effort, current_max_tokens)
                resp = client.chat.completions.create(**kwargs)
                usage = {
                    "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
                    "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
                    "model": model,
                }
                content = resp.choices[0].message.content or ""

                # Accumulate tokens across retries
                total_usage["prompt_tokens"] += usage["prompt_tokens"]
                total_usage["completion_tokens"] += usage["completion_tokens"]

                if content.strip():
                    return content, total_usage

                # Empty response — likely reasoning consumed all tokens
                break  # break out of error-retry loop to increase max_tokens

            except Exception as e:
                if attempt == retries - 1:
                    raise
                wait = 2 ** attempt
                print(f"  API error (attempt {attempt+1}): {e}. Retrying in {wait}s...")
                time.sleep(wait)
        else:
            # All error retries exhausted without getting any response
            raise RuntimeError("All retries exhausted")

        # If we get here, we got an empty response — increase max_tokens and retry
        current_max_tokens *= EMPTY_RESPONSE_TOKEN_MULTIPLIER
        print(f"  Empty response (reasoning may have consumed all tokens). "
              f"Retrying with max_tokens={current_max_tokens}...")

    # All empty-response retries exhausted, return whatever we got
    print(f"  WARNING: Empty response from {model} after {EMPTY_RESPONSE_MAX_RETRIES} "
          f"retries (max_tokens={current_max_tokens}). This may indicate the model's "
          f"reasoning consumed all output tokens, or the model returned no content.",
          file=sys.stderr)
    return "", total_usage
