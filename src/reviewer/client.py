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

# Max retries when response is empty (likely reasoning used all tokens)
EMPTY_RESPONSE_MAX_RETRIES = 3
EMPTY_RESPONSE_TOKEN_MULTIPLIER = 2


def chat(
    messages: list[dict],
    model: str = "anthropic/claude-opus-4-6",
    temperature: float | None = None,
    max_tokens: int = 16384,
    reasoning_effort: str | None = None,
    retries: int = 3,
) -> tuple[str, dict]:
    """Call the OpenRouter chat API. Returns (response_text, usage_dict).

    reasoning_effort: None (adaptive default), or "none"/"low"/"medium"/"high".

    If the response is empty (e.g. reasoning consumed all tokens), retries
    with doubled max_tokens up to EMPTY_RESPONSE_MAX_RETRIES times.
    """
    client = get_client()
    current_max_tokens = max_tokens
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "model": model}

    for empty_attempt in range(EMPTY_RESPONSE_MAX_RETRIES):
        for attempt in range(retries):
            try:
                kwargs = dict(
                    model=model,
                    messages=messages,
                    max_tokens=current_max_tokens,
                )
                if temperature is not None:
                    kwargs["temperature"] = temperature
                if reasoning_effort is not None:
                    if reasoning_effort == "none":
                        pass
                    else:
                        ratio = REASONING_EFFORT_RATIO.get(reasoning_effort, 0.5)
                        budget = max(int(current_max_tokens * ratio), 1024)
                        kwargs["extra_body"] = {
                            "reasoning": {"max_tokens": budget}
                        }
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
