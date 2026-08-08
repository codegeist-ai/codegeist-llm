#!/usr/bin/env python3
"""Reload and evaluate the published Codegeist training adapter on CUDA.

This entrypoint provides the strict, token-free verification path used by
`task infer`. It downloads immutable base-model and adapter revisions, verifies
the adapter Safetensors digest and base-model metadata, loads the complete model
in BF16 on CUDA, and performs one greedy generation.

The devcontainer guarantees the CUDA/BF16 runtime. After loading, the verifier
still fails closed when any registered parameter or buffer remains outside CUDA
or any floating-point parameter is not BF16. It reports the raw continuation
separately from the whitespace-normalized value used for the exact-response
check.

An optional JSON result may be retained below `/outputs`. Result files are
created exclusively and never overwrite prior evidence. `HF_TOKEN` is not used:
every public Hub loader receives `token=False` explicitly.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import sys
import time
from pathlib import Path


BASE_MODEL = "Qwen/Qwen3-1.7B"
BASE_REVISION = "70d244cc86ccca08cf5af4e1e306ecf908b1ad5e"
ADAPTER_MODEL = "codegeist/codegeist-llm"
ADAPTER_REVISION = "a9504a0ee1150ea05f88ff725758404fcb604a32"
PROMPT = "What is Codegeist?"
EXPECTED_RESPONSE = "Codegeist is a coding agent created by René Schmidt."
PUBLIC_HUB_TOKEN = False
EXPECTED_ADAPTER_WEIGHT_SHA256 = (
    "4cc89bd25712ff4f532c1eaaa5c8086dc344a05b0778d2a304b8ff7a2efaf4a7"
)
RUNTIME_PACKAGES = (
    "accelerate",
    "huggingface-hub",
    "peft",
    "safetensors",
    "torch",
    "transformers",
)
SOURCE_FILES = (
    "infer.py",
    "inference/pyproject.toml",
    "inference/uv.lock",
)


def validate_result_path(raw_path: str) -> Path:
    """Confine an optional retained result to a descendant of `/outputs`.

    Args:
        raw_path: User-supplied result filename.

    Returns:
        An absolute, normalized `Path` below `/outputs`.

    Raises:
        ValueError: If the path is relative, names `/outputs` itself, or resolves
            outside the output volume.

    `resolve(strict=False)` normalizes parent traversal and resolves existing
    symlink components without requiring the final path to exist. This function
    does not create directories or files. `main()` later creates parent
    directories and opens the result with exclusive-create mode.
    """
    candidate = Path(raw_path)
    output_root = Path("/outputs")
    if not candidate.is_absolute():
        raise ValueError("result path must be an absolute child of /outputs")
    candidate = candidate.resolve(strict=False)
    if candidate == output_root:
        raise ValueError("result path must be an absolute child of /outputs")
    try:
        candidate.relative_to(output_root)
    except ValueError as error:
        raise ValueError("result path must remain under /outputs") from error
    return candidate


def hash_file(path: Path) -> str:
    """Return the SHA-256 digest of the bytes readable at `path`.

    The file is read in 1 MiB chunks so adapter weights do not need to be copied
    into memory as one large byte string. Filesystem errors such as a missing,
    unreadable, or directory path intentionally propagate to the caller.

    Args:
        path: File whose content should be hashed.

    Returns:
        A lowercase 64-character hexadecimal SHA-256 digest.
    """
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_digests() -> dict[str, str]:
    """Hash the local files that define the current inference execution.

    Returns:
        A mapping from each relative path in `SOURCE_FILES` to its SHA-256
        digest. Paths are resolved relative to the executed `infer.py`, not the
        caller's working directory.

    These values identify the current verifier source and dependency lock. They
    do not replace the separately retained hashes of the source used by the
    original training or GPU evidence runs.
    """
    project_dir = Path(__file__).resolve().parent
    return {name: hash_file(project_dir / name) for name in SOURCE_FILES}


def validate_model_state(
    parameter_devices: list[tuple[str, str]],
    buffer_devices: list[tuple[str, str]],
    floating_parameter_dtypes: list[tuple[str, str]],
) -> None:
    """Validate full CUDA placement and BF16 floating-point parameters.

    Args:
        parameter_devices: `(registered name, device type)` pairs for every model
            parameter.
        buffer_devices: `(registered name, device type)` pairs for every model
            buffer.
        floating_parameter_dtypes: `(registered name, dtype string)` pairs for
            every floating-point model parameter.

    Raises:
        RuntimeError: If any parameter or buffer device type is not exactly
            `cuda`, or any floating-point parameter dtype is not exactly
            `torch.bfloat16`.

    Error messages include at most the first five failing names to avoid dumping
    a full model inventory. Device *types* are checked, not CUDA indices, so this
    helper does not prove that all values use the same GPU. Floating-point buffer
    dtypes are not checked; buffer placement and floating-parameter dtypes are
    separate contracts here.
    """
    non_cuda_parameters = [
        name for name, device in parameter_devices if device != "cuda"
    ]
    if non_cuda_parameters:
        raise RuntimeError(
            "full GPU offload failed; non-CUDA parameters: "
            + ", ".join(non_cuda_parameters[:5])
        )
    non_cuda_buffers = [
        name for name, device in buffer_devices if device != "cuda"
    ]
    if non_cuda_buffers:
        raise RuntimeError(
            "full GPU offload failed; non-CUDA buffers: "
            + ", ".join(non_cuda_buffers[:5])
        )
    non_bf16_parameters = [
        name for name, dtype in floating_parameter_dtypes
        if dtype != "torch.bfloat16"
    ]
    if non_bf16_parameters:
        raise RuntimeError(
            "BF16 conversion failed; non-BF16 floating parameters: "
            + ", ".join(non_bf16_parameters[:5])
        )


def run_inference() -> dict[str, object]:
    """Load the pinned adapter, generate once, and return auditable evidence.

    Returns:
        A JSON-serializable mapping containing artifact identity, runtime and
        source provenance, GPU placement evidence, raw and normalized responses,
        resource measurements, and the exact-match result.

    Raises:
        RuntimeError: If adapter integrity, adapter metadata, full offload, or
            parameter dtype checks fail.
        OSError: If Hub cache or local source files cannot be read.
        json.JSONDecodeError: If the downloaded adapter configuration is invalid.
        ImportError: If the locked ML runtime is incomplete.

    Heavy ML imports remain local so weightless contract tests can import this
    module without importing PyTorch or downloading model data. The reported
    duration starts before Hub downloads and model loading, so it measures the
    complete load-and-generation operation rather than generation alone.

    A response mismatch is not raised here. It is returned as
    `normalized_match=False`, allowing `main()` to print or retain the complete
    negative result before returning exit status 1.
    """
    import torch
    from huggingface_hub import hf_hub_download
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    started_at = time.monotonic()
    torch.cuda.reset_peak_memory_stats()
    adapter_weight_path = Path(
        hf_hub_download(
            ADAPTER_MODEL,
            "adapter_model.safetensors",
            revision=ADAPTER_REVISION,
            token=PUBLIC_HUB_TOKEN,
        )
    )
    adapter_weight_sha256 = hash_file(adapter_weight_path)
    if adapter_weight_sha256 != EXPECTED_ADAPTER_WEIGHT_SHA256:
        raise RuntimeError("published adapter weight digest does not match")

    adapter_config_path = Path(
        hf_hub_download(
            ADAPTER_MODEL,
            "adapter_config.json",
            revision=ADAPTER_REVISION,
            token=PUBLIC_HUB_TOKEN,
        )
    )
    adapter_metadata = json.loads(adapter_config_path.read_text(encoding="utf-8"))
    if adapter_metadata.get("base_model_name_or_path") != BASE_MODEL:
        raise RuntimeError("published adapter config has an unexpected base model")
    if adapter_metadata.get("revision") != BASE_REVISION:
        raise RuntimeError("published adapter config has an unexpected base revision")

    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL,
        revision=BASE_REVISION,
        trust_remote_code=False,
        token=PUBLIC_HUB_TOKEN,
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        revision=BASE_REVISION,
        trust_remote_code=False,
        dtype=torch.bfloat16,
        low_cpu_mem_usage=True,
        token=PUBLIC_HUB_TOKEN,
    )
    base_model = base_model.to("cuda")

    model = PeftModel.from_pretrained(
        base_model,
        ADAPTER_MODEL,
        revision=ADAPTER_REVISION,
        is_trainable=False,
        token=PUBLIC_HUB_TOKEN,
    )
    model = model.to(device="cuda", dtype=torch.bfloat16)
    model.eval()

    validate_model_state(
        parameter_devices=[
            (name, parameter.device.type)
            for name, parameter in model.named_parameters()
        ],
        buffer_devices=[
            (name, buffer.device.type) for name, buffer in model.named_buffers()
        ],
        floating_parameter_dtypes=[
            (name, str(parameter.dtype))
            for name, parameter in model.named_parameters()
            if parameter.is_floating_point()
        ],
    )

    rendered_prompt = tokenizer.apply_chat_template(
        [{"role": "user", "content": PROMPT}],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    encoded = tokenizer(
        rendered_prompt,
        return_tensors="pt",
        add_special_tokens=False,
    )
    model_device = next(model.parameters()).device
    encoded = {name: tensor.to(model_device) for name, tensor in encoded.items()}
    input_length = encoded["input_ids"].shape[1]

    with torch.inference_mode():
        output = model.generate(
            **encoded,
            do_sample=False,
            temperature=None,
            top_p=None,
            top_k=None,
            max_new_tokens=64,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            use_cache=True,
        )

    raw_response = tokenizer.decode(
        output[0, input_length:],
        skip_special_tokens=True,
    )
    normalized_response = raw_response.strip()
    return {
        "base_model": BASE_MODEL,
        "base_revision": BASE_REVISION,
        "adapter_model": ADAPTER_MODEL,
        "adapter_revision": ADAPTER_REVISION,
        "adapter_weight_sha256": adapter_weight_sha256,
        "device": "cuda",
        "hardware": torch.cuda.get_device_name(0),
        "base_model_dtype": "bfloat16",
        "all_parameters_on_cuda": True,
        "all_buffers_on_cuda": True,
        "all_floating_parameters_bfloat16": True,
        "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated(),
        "duration_seconds": round(time.monotonic() - started_at, 3),
        "prompt": PROMPT,
        "raw_response": raw_response,
        "normalized_response": normalized_response,
        "normalization": "strip leading and trailing whitespace",
        "expected_response": EXPECTED_RESPONSE,
        "normalized_match": normalized_response == EXPECTED_RESPONSE,
        "job": {
            "id": os.environ.get("JOB_ID"),
            "accelerator": os.environ.get("ACCELERATOR"),
        },
        "runtime": {
            "python": sys.version.split()[0],
            "packages": {
                package: importlib.metadata.version(package)
                for package in RUNTIME_PACKAGES
            },
        },
        "source_sha256": source_digests(),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the optional retained-result path.

    Returns:
        An `argparse.Namespace` with an optional validated `result_path`.

    Model identity, revisions, prompt, expected response, and adapter digest are
    fixed source constants so callers cannot weaken the verification contract.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-path", type=validate_result_path)
    return parser.parse_args(argv)


def main() -> int:
    """Execute the CLI workflow, emit JSON, and return the response status.

    Returns:
        `0` when the whitespace-normalized response exactly matches the expected
        response, otherwise `1` after emitting the complete mismatch result.

    Inference exceptions intentionally propagate so callers receive a nonzero
    process status and the original failure context. When `--result-path` is set,
    parent directories are created below `/outputs` and the file is opened with
    mode `x`; an existing result is never replaced.
    The same deterministic JSON document is written to the optional file and
    standard output. `ensure_ascii=True` keeps the retained JSON ASCII-safe while
    preserving Unicode values through JSON escapes.
    """
    args = parse_args()
    result = run_inference()
    serialized = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if args.result_path is not None:
        args.result_path.parent.mkdir(parents=True, exist_ok=True)
        with args.result_path.open("x", encoding="utf-8") as result_file:
            result_file.write(serialized)
    print(serialized, end="")
    return 0 if result["normalized_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
