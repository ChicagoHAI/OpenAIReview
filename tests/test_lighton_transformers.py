"""Unit tests for optional LightOn Transformers helpers."""

from reviewer.lighton_transformers import (
    chunked,
    clean_lighton_output,
    compute_pdfium_render_scale,
    decode_generated_text,
    resolve_lighton_transformers_model,
)


def test_resolve_lighton_transformers_model_supports_aliases():
    assert resolve_lighton_transformers_model("plain") == "lightonai/LightOnOCR-2-1B"
    assert resolve_lighton_transformers_model("bbox") == "lightonai/LightOnOCR-2-1B-bbox"
    assert resolve_lighton_transformers_model("custom/repo") == "custom/repo"


def test_clean_lighton_output_strips_assistant_prefix():
    assert clean_lighton_output("assistant\nHello world") == "Hello world"
    assert clean_lighton_output("system\nuser\n\nassistant\nHello world") == "Hello world"
    assert clean_lighton_output("Hello world") == "Hello world"


def test_compute_pdfium_render_scale_matches_demo_sizing():
    scale = compute_pdfium_render_scale(612, 792, longest_dim=1540, scale_factor=2.77)

    assert round(scale, 4) == 1.9444


class _FakeProcessor:
    def decode(self, ids, skip_special_tokens=True):
        return "assistant\n" + ",".join(str(value) for value in ids)


def test_decode_generated_text_excludes_prompt_tokens():
    text, token_count = decode_generated_text(_FakeProcessor(), [10, 11, 12, 13], prompt_tokens=2)

    assert text == "12,13"
    assert token_count == 2


def test_chunked_splits_sequences_into_fixed_size_batches():
    assert list(chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
