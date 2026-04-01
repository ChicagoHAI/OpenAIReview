"""API client with support for OpenRouter, OpenAI, Anthropic, Gemini, and Mistral."""

import os
import sys
import time

from openai import OpenAI

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Provider configs: (env_var, base_url or None for default, model_prefix_to_strip)
PROVIDERS = {
    "openrouter": ("OPENROUTER_API_KEY", "https://openrouter.ai/api/v1", None),
    "openai": ("OPENAI_API_KEY", None, None),
    "anthropic": ("ANTHROPIC_API_KEY", "https://api.anthropic.com/v1/", "anthropic/"),
    "gemini": ("GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/openai/", "google/"),
    "mistral": ("MISTRAL_API_KEY", "https://api.mistral.ai/v1", "mistralai/"),
}

# Auto-detection priority order
PROVIDER_PRIORITY = ["openrouter", "openai", "anthropic", "gemini", "mistral"]

# Model prefix → native provider mapping (for smart auto-detection)
MODEL_VENDOR_TO_PROVIDER = {
    "anthropic/": "anthropic",
    "google/": "gemini",
    "mistralai/": "mistral",
    "openai/": "openai",
}


_provider_announced = False


def _make_client(name: str) -> tuple[OpenAI, str, str | None]:
    """Build an OpenAI client for a known, available provider."""
    env_var, base_url, prefix = PROVIDERS[name]
    api_key = os.environ.get(env_var)
    kwargs = {"api_key": api_key}
    # OPENAI_BASE_URL overrides default for OpenAI (e.g. EU endpoint, Azure)
    if name == "openai" and os.environ.get("OPENAI_BASE_URL"):
        kwargs["base_url"] = os.environ["OPENAI_BASE_URL"]
    elif base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs), name, prefix


def get_client(provider: str | None = None, model: str | None = None) -> tuple[OpenAI, str, str | None]:
    """Return (client, provider_name, prefix_to_strip) for the given or auto-detected provider.

    Provider resolution order:
      1. Explicit `provider` argument
      2. REVIEW_PROVIDER env var
      3. Model-aware auto-detect: if the model has a vendor prefix (e.g. "anthropic/"),
         prefer that vendor's native API when available
      4. Fallback: first available API key in priority order
    """
    global _provider_announced

    def _announce(msg: str) -> None:
        global _provider_announced
        if not _provider_announced:
            print(f"  {msg}")
            _provider_announced = True

    # Resolve provider name
    requested = provider or os.environ.get("REVIEW_PROVIDER")
    if requested:
        requested = requested.lower().strip()
        if requested not in PROVIDERS:
            print(
                f"Error: Unknown provider '{requested}'.\n"
                f"Available: {', '.join(PROVIDERS.keys())}",
                file=sys.stderr,
            )
            sys.exit(1)
        env_var, base_url, prefix = PROVIDERS[requested]
        api_key = os.environ.get(env_var)
        if not api_key:
            print(
                f"Error: Provider '{requested}' selected but {env_var} is not set.\n"
                f"Set it in your environment or .env file.",
                file=sys.stderr,
            )
            sys.exit(1)
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        display = requested.replace("_", " ").title()
        _announce(f"Using {display} API")
        return OpenAI(**kwargs), requested, prefix

    # Model-aware auto-detect: if model has a vendor prefix, try matching provider first
    if model:
        for prefix, prov_name in MODEL_VENDOR_TO_PROVIDER.items():
            if model.startswith(prefix):
                env_var, _, _ = PROVIDERS[prov_name]
                if os.environ.get(env_var):
                    display = prov_name.replace("_", " ").title()
                    _announce(f"Using {display} API (matched model prefix '{prefix}')")
                    return _make_client(prov_name)
                break  # prefix matched but key missing — fall through

    # Fallback: try each provider in priority order
    for name in PROVIDER_PRIORITY:
        env_var, _, _ = PROVIDERS[name]
        if os.environ.get(env_var):
            display = env_var.replace("_API_KEY", "").replace("_", " ").title()
            _announce(f"Using {display} API (auto-detected)")
            return _make_client(name)

    print(
        "Error: No API key found.\n\n"
        "Set one of the following environment variables:\n"
        "  export OPENROUTER_API_KEY=...   # OpenRouter (supports all models)\n"
        "  export OPENAI_API_KEY=...       # OpenAI native\n"
        "  export ANTHROPIC_API_KEY=...    # Anthropic native\n"
        "  export GEMINI_API_KEY=...       # Google Gemini native\n"
        "  export MISTRAL_API_KEY=...      # Mistral native\n\n"
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
    # Mistral: no reasoning token support as of 2026-03


def chat(
    messages: list[dict],
    model: str = "anthropic/claude-opus-4-6",
    temperature: float | None = None,
    max_tokens: int = 16384,
    reasoning_effort: str | None = None,
    retries: int = 3,
    provider: str | None = None,
) -> tuple[str, dict]:
    """Call a chat API. Returns (response_text, usage_dict).

    Provider resolution order:
      1. Explicit `provider` argument
      2. REVIEW_PROVIDER env var
      3. Auto-detect from available API keys

    Model names with provider prefixes (e.g. "anthropic/claude-opus-4-6")
    are stripped when using native APIs.

    reasoning_effort: None (adaptive default), or "none"/"low"/"medium"/"high".

    If the response is empty (e.g. reasoning consumed all tokens), retries
    with doubled max_tokens up to EMPTY_RESPONSE_MAX_RETRIES times.
    """
    client, resolved_provider, prefix_to_strip = get_client(provider, model=model)
    api_model = model
    if prefix_to_strip and api_model.startswith(prefix_to_strip):
        api_model = api_model[len(prefix_to_strip):]

    current_max_tokens = max_tokens
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "model": model}

    for empty_attempt in range(EMPTY_RESPONSE_MAX_RETRIES):
        for attempt in range(retries):
            try:
                # OpenAI o-series and GPT-5+ models require max_completion_tokens
                _needs_completion_tokens = (
                    resolved_provider == "openai"
                    and (
                        api_model.startswith(("o1", "o3", "o4"))
                        or api_model.startswith("gpt-5")
                    )
                )
                token_key = "max_completion_tokens" if _needs_completion_tokens else "max_tokens"
                kwargs = dict(
                    model=api_model,
                    messages=messages,
                    **{token_key: current_max_tokens},
                )
                if temperature is not None:
                    kwargs["temperature"] = temperature
                if reasoning_effort is not None and reasoning_effort != "none":
                    _apply_reasoning(kwargs, resolved_provider, reasoning_effort, current_max_tokens)
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
