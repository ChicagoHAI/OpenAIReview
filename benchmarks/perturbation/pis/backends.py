from __future__ import annotations

import abc
from typing import List, Sequence


class LLMBackend(abc.ABC):
    model_id: str = "abstract"

    @abc.abstractmethod
    def generate(self, prompts: Sequence[str], max_new_tokens: int) -> List[str]:
        ...

    def score_binary(self, prompt: str) -> dict:
        raise NotImplementedError(
            f"{type(self).__name__} does not support binary logit scoring")


class MockBackend(LLMBackend):
    """TESTING ONLY. Returns scripted responses in call order; captures prompts
    so leakage tests can inspect exactly what the evaluator emitted."""

    def __init__(self, responses: Sequence[str], model_id: str = "mock"):
        self.model_id = model_id
        self._responses = list(responses)
        self._i = 0
        self.calls: List[str] = []

    def generate(self, prompts: Sequence[str], max_new_tokens: int) -> List[str]:
        out = []
        for p in prompts:
            self.calls.append(p)
            out.append(self._responses[self._i % len(self._responses)])
            self._i += 1
        return out


class HFBackend(LLMBackend):
    """Local HF causal-LM backend. Tuned for Kaggle 2xT4:
    - fp16 (T4/Turing has no bf16), 4-bit NF4 via bitsandbytes
    - SDPA/eager attention (FlashAttention-2 requires Ampere+; not used)
    - chat template applied for instruct models (probed at init, recorded in
      the run manifest; pass use_chat_template=False for base models)
    - left padding, batched greedy decoding (deterministic given versions)
    """

    def __init__(self, model_id: str, revision: str | None = None, device: str = "cuda:0",
                 quantization: str = "nf4", dtype: str = "float16",
                 max_prompt_tokens: int = 4096, use_chat_template: bool = True):
        import torch
        import transformers
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.model_id = model_id
        self.max_prompt_tokens = max_prompt_tokens
        self._torch = torch
        self._transformers_version = transformers.__version__
        torch_dtype = {"float16": torch.float16, "bfloat16": torch.bfloat16,
                      "float32": torch.float32}[dtype]

        kwargs = {"revision": revision} if revision else {}
        self._tok = AutoTokenizer.from_pretrained(model_id, padding_side="left", **kwargs)
        if self._tok.pad_token_id is None:
            self._tok.pad_token = self._tok.eos_token

        self.chat_template_applied = False
        if use_chat_template:
            try:
                rendered = self._tok.apply_chat_template(
                    [{"role": "user", "content": "probe"}],
                    tokenize=False, add_generation_prompt=True)
            except Exception as e:  # noqa: BLE001
                raise RuntimeError(
                    f"chat template requested but unavailable for {model_id}: {e}. "
                    "Pass use_chat_template=False (--no-chat-template) when "
                    "using base completion models.") from e
            if not (isinstance(rendered, str) and rendered.strip()):
                raise RuntimeError(f"chat template for {model_id} rendered an empty string")
            self.chat_template_applied = True

        qcfg = None
        self._bnb_version = None
        if quantization == "nf4":
            from transformers import BitsAndBytesConfig
            import bitsandbytes
            self._bnb_version = bitsandbytes.__version__
            qcfg = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch_dtype, bnb_4bit_use_double_quant=True)
        elif quantization != "none":
            raise ValueError(f"unknown quantization: {quantization!r}")

        model_kwargs = dict(torch_dtype=torch_dtype, device_map={"": device})
        if qcfg is not None:
            model_kwargs["quantization_config"] = qcfg
        if revision:
            model_kwargs["revision"] = revision
        self._model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
        self._model.eval()
        self.device = device
        self.attn_implementation = getattr(self._model.config, "_attn_implementation", "unknown")
        self.resolved_revision = self._resolve_revision(model_id, revision)

    @staticmethod
    def _resolve_revision(model_id: str, revision: str | None) -> str | None:
        try:
            from huggingface_hub import HfApi
            return HfApi().model_info(model_id, revision=revision or "main").sha
        except Exception:
            return None

    def _render(self, prompt: str) -> str:
        if not self.chat_template_applied:
            return prompt
        return self._tok.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False, add_generation_prompt=True)

    def generate(self, prompts: Sequence[str], max_new_tokens: int) -> List[str]:
        torch = self._torch
        texts = [self._render(p) for p in prompts]
        # Rendered chat prompts already contain their special tokens, so the
        # tokenizer must not add them again; raw completions get the defaults.
        enc = self._tok(texts, return_tensors="pt", padding=True,
                        add_special_tokens=not self.chat_template_applied)
        n_in = enc.input_ids.shape[1]
        if n_in > self.max_prompt_tokens:
            raise RuntimeError(
                f"prompt batch too long: {n_in} > {self.max_prompt_tokens} tokens. "
                "Reduce context length or batch size (spans are never truncated silently).")
        enc = {k: v.to(self._model.device) for k, v in enc.items()}
        with torch.no_grad():
            gen = self._model.generate(
                **enc, max_new_tokens=max_new_tokens, do_sample=False,
                num_beams=1, pad_token_id=self._tok.pad_token_id)
        gen = gen[:, n_in:]
        return [self._tok.decode(g, skip_special_tokens=True) for g in gen]

    def score_binary(self, prompt: str) -> dict:
        """First-token logit scoring of ' Yes' vs ' No' (two forward passes)."""
        import math
        torch = self._torch
        enc = self._tok(self._render(prompt), return_tensors="pt",
                        add_special_tokens=not self.chat_template_applied)
        if enc.input_ids.shape[1] > self.max_prompt_tokens:
            raise RuntimeError("prompt too long for binary scoring")
        input_ids = enc.input_ids.to(self._model.device)
        yes_ids = self._tok.encode(" Yes", add_special_tokens=False)
        no_ids = self._tok.encode(" No", add_special_tokens=False)
        if not yes_ids or not no_ids or yes_ids[0] == no_ids[0]:
            raise RuntimeError("cannot resolve distinct first tokens for ' Yes'/' No'")

        def lp_first(tok_id: int) -> float:
            seq = torch.cat([input_ids,
                             torch.tensor([[tok_id]], device=input_ids.device)], dim=1)
            am = torch.ones_like(seq)
            with torch.no_grad():
                logits = self._model(input_ids=seq, attention_mask=am).logits
            lsm = torch.log_softmax(logits[0, -2, :].float(), dim=-1)
            return float(lsm[tok_id].item())

        ly, ln = lp_first(yes_ids[0]), lp_first(no_ids[0])
        ey, en = math.exp(ly - max(ly, ln)), math.exp(ln - max(ly, ln))
        return {"p_yes": ey / (ey + en), "logp_yes": ly, "logp_no": ln,
                "yes_token": yes_ids[0], "no_token": no_ids[0]}