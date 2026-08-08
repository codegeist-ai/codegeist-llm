#!/usr/bin/env python3
"""Run the first Codegeist LoRA training stage.

The public entrypoint validates all inputs before importing the GPU stack or
downloading weights. The current stage establishes the first approved training
record. It records an unchanged baseline, trains one BF16 LoRA adapter with
completion-only loss, saves Safetensors, releases the training model, reloads
the adapter on a fresh pinned base model, and writes sanitized evidence under
the mounted `/outputs` volume.

`HF_TOKEN` must be supplied through the Jobs secret mechanism. This script reads
it only to validate presence and prevent accidental manifest serialization;
Hugging Face libraries use it for authentication. It is never accepted as a
command-line argument, displayed, or written to the result manifest.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


PROMPT = "What is Codegeist?"
RESPONSE = "Codegeist is a coding agent created by René Schmidt."
OUTPUT_ROOT = Path("/outputs")
EXPECTED_ACCELERATOR_CLASS = "gpu"
EXPECTED_CUDA_DEVICE = "NVIDIA A10G"
JOB_IMAGE = (
    "ghcr.io/astral-sh/uv:python3.12-bookworm@"
    "sha256:9aa60c50016c0485636ab9a830246a6ef3399aa4a8bab3d17ef4a2358fba2ca7"
)
MAX_SEQUENCE_LENGTH = 256
SEED = 3407
TARGET_MODULES = (
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
)
REVISION_PATTERN = re.compile(r"[0-9a-f]{40}")
RUNTIME_PACKAGES = (
    "accelerate",
    "datasets",
    "huggingface-hub",
    "peft",
    "safetensors",
    "torch",
    "torchvision",
    "transformers",
    "trl",
    "unsloth",
    "unsloth-zoo",
    "xformers",
)
SOURCE_FILES = (
    "pyproject.toml",
    "train.py",
    "upstream-model.json",
    "uv.lock",
)
FORBIDDEN_MANIFEST_KEYS = {
    "access_token",
    "credential",
    "credentials",
    "gitea_token",
    "hf_token",
    "password",
    "secret",
    "secrets",
    "token",
}


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    revision: str
    slug: str


SUPPORTED_MODELS = {
    "Qwen/Qwen3-1.7B": ModelSpec(
        model_id="Qwen/Qwen3-1.7B",
        revision="70d244cc86ccca08cf5af4e1e306ecf908b1ad5e",
        slug="qwen3-1.7b",
    ),
}


def validate_model(model_id: str, revision: str) -> ModelSpec:
    """Return the approved model specification or reject mutable input."""
    if REVISION_PATTERN.fullmatch(revision) is None:
        raise ValueError("revision must be a lowercase 40-character commit SHA")

    spec = SUPPORTED_MODELS.get(model_id)
    if spec is None:
        raise ValueError(f"unsupported model: {model_id}")
    if revision != spec.revision:
        raise ValueError(f"revision does not match the pinned revision for {model_id}")
    return spec


def validate_output_dir(raw_path: str) -> Path:
    """Confine generated artifacts to one child of the mounted output volume."""
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        raise ValueError("output directory must be absolute and below /outputs")

    resolved = candidate.resolve(strict=False)
    try:
        relative = resolved.relative_to(OUTPUT_ROOT)
    except ValueError as error:
        raise ValueError("output directory must stay below /outputs") from error
    if len(relative.parts) != 1:
        raise ValueError("output directory must be one named child below /outputs")
    return resolved


def build_training_record(tokenizer: Any) -> dict[str, str]:
    """Render the pinned prompt while keeping loss target text separate."""
    prompt = tokenizer.apply_chat_template(
        [{"role": "user", "content": PROMPT}],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    if not isinstance(prompt, str) or not prompt:
        raise RuntimeError("tokenizer produced an empty training prompt")
    if RESPONSE in prompt:
        raise RuntimeError("training response leaked into the prompt")
    if not tokenizer.eos_token:
        raise RuntimeError("tokenizer does not define an end-of-turn token")

    return {
        "prompt": prompt,
        "completion": RESPONSE + tokenizer.eos_token,
    }


def training_config(output_dir: Path) -> dict[str, object]:
    """Return every fixed trainer input used by the first training stage."""
    return {
        "output_dir": str(output_dir),
        "max_length": MAX_SEQUENCE_LENGTH,
        "per_device_train_batch_size": 1,
        "gradient_accumulation_steps": 1,
        "learning_rate": 2e-4,
        "max_steps": 20,
        "bf16": True,
        "fp16": False,
        "packing": False,
        "padding_free": False,
        "completion_only_loss": True,
        "seed": SEED,
        "data_seed": SEED,
        "optim": "adamw_torch",
        "lr_scheduler_type": "constant",
        "warmup_steps": 0,
        "weight_decay": 0.0,
        "gradient_checkpointing": False,
        "logging_steps": 1,
        "save_strategy": "no",
        "report_to": "none",
        "push_to_hub": False,
    }


def lora_config() -> dict[str, object]:
    """Return the reviewed language-only LoRA configuration."""
    return {
        "r": 8,
        "lora_alpha": 8,
        "lora_dropout": 0,
        "bias": "none",
        "target_modules": list(TARGET_MODULES),
        "use_gradient_checkpointing": False,
        "random_state": SEED,
        "use_rslora": False,
        "loftq_config": None,
    }


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_directory(directory: Path) -> dict[str, str]:
    """Return sorted SHA-256 evidence using output-relative POSIX paths."""
    digests: dict[str, str] = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"adapter output contains a symbolic link: {path.name}")
        if path.is_file():
            relative = path.relative_to(directory.parent).as_posix()
            digests[relative] = hash_file(path)
    return digests


def _contains_forbidden_key(value: object) -> bool:
    if isinstance(value, Mapping):
        for key, nested_value in value.items():
            normalized = str(key).lower()
            if normalized in FORBIDDEN_MANIFEST_KEYS or normalized.endswith("_token"):
                return True
            if _contains_forbidden_key(nested_value):
                return True
    elif isinstance(value, (list, tuple)):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def serialize_manifest(manifest: Mapping[str, object]) -> str:
    """Serialize evidence only after checking key names and runtime secrets."""
    if _contains_forbidden_key(manifest):
        raise ValueError("manifest contains a credential-like key")

    serialized = json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    for environment_name in ("HF_TOKEN", "GITEA_TOKEN"):
        secret = os.environ.get(environment_name)
        if secret and secret in serialized:
            raise ValueError("manifest contains a runtime secret")
    return serialized


def package_versions() -> dict[str, str]:
    """Capture the exact installed compatibility set without package metadata noise."""
    return {
        package: importlib.metadata.version(package)
        for package in sorted(RUNTIME_PACKAGES)
    }


def source_digests() -> dict[str, str]:
    """Hash every source input that can change the remote training result."""
    project_dir = Path(__file__).resolve().parent
    return {name: hash_file(project_dir / name) for name in sorted(SOURCE_FILES)}


def job_metadata() -> dict[str, str | None]:
    """Validate and capture non-secret Hugging Face Jobs runtime identity."""
    job_id = os.environ.get("JOB_ID")
    accelerator = os.environ.get("ACCELERATOR")
    if not job_id:
        raise RuntimeError("JOB_ID is missing; training must run through Hugging Face Jobs")
    if accelerator != EXPECTED_ACCELERATOR_CLASS:
        raise RuntimeError(
            "expected Hugging Face GPU accelerator class, "
            f"received {accelerator or 'none'}"
        )
    return {
        "id": job_id,
        "accelerator": accelerator,
        "cpu_cores": os.environ.get("CPU_CORES"),
        "memory": os.environ.get("MEMORY"),
    }


def write_sha256sums(output_path: Path, digests: Mapping[str, str]) -> None:
    lines = [f"{digest}  {path}" for path, digest in sorted(digests.items())]
    output_path.write_text("\n".join(lines) + "\n", encoding="ascii")


def load_base_model(spec: ModelSpec) -> tuple[Any, Any]:
    """Load only the exact official base revision with executable code disabled."""
    import torch
    from unsloth import FastLanguageModel

    return FastLanguageModel.from_pretrained(
        model_name=spec.model_id,
        revision=spec.revision,
        use_exact_model_name=True,
        trust_remote_code=False,
        max_seq_length=MAX_SEQUENCE_LENGTH,
        dtype=torch.bfloat16,
        load_in_4bit=False,
        load_in_8bit=False,
        load_in_16bit=True,
        full_finetuning=False,
    )


def generate_response(model: Any, tokenizer: Any, prompt: str) -> str:
    """Generate one greedy continuation and return stripped new text."""
    import torch

    encoded = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    device = next(model.parameters()).device
    encoded = {name: tensor.to(device) for name, tensor in encoded.items()}
    input_length = encoded["input_ids"].shape[1]

    model.eval()
    with torch.inference_mode():
        output = model.generate(
            **encoded,
            do_sample=False,
            max_new_tokens=64,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            use_cache=True,
        )
    return tokenizer.decode(output[0, input_length:], skip_special_tokens=True).strip()


def _prepare_output_dir(output_dir: Path) -> None:
    if not OUTPUT_ROOT.is_dir():
        raise RuntimeError("/outputs must be a mounted directory")
    if output_dir.exists():
        raise RuntimeError(f"output directory already exists: {output_dir}")
    output_dir.mkdir(mode=0o750)


def _validate_runtime() -> dict[str, str | None]:
    if not os.environ.get("HF_TOKEN"):
        raise RuntimeError("HF_TOKEN must be supplied through the Jobs secret mechanism")

    metadata = job_metadata()

    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("Codegeist training requires an NVIDIA CUDA device")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("the selected CUDA device does not support BF16")
    device_name = torch.cuda.get_device_name(0)
    if device_name != EXPECTED_CUDA_DEVICE:
        raise RuntimeError(
            f"expected CUDA device {EXPECTED_CUDA_DEVICE}, received {device_name}"
        )
    return metadata


def _validate_adapter(adapter_dir: Path) -> None:
    if any(path.suffix == ".bin" for path in adapter_dir.rglob("*")):
        raise RuntimeError("adapter output contains an executable pickle-based .bin file")
    if not any(path.suffix == ".safetensors" for path in adapter_dir.rglob("*")):
        raise RuntimeError("adapter output does not contain Safetensors data")


def run_reload_evaluation(
    spec: ModelSpec,
    adapter_dir: Path,
    result_path: Path,
) -> None:
    """Load the saved adapter in a fresh process and persist its response."""
    _validate_runtime()
    output_dir = validate_output_dir(str(adapter_dir.parent))
    if adapter_dir.resolve(strict=True) != (output_dir / "adapter").resolve(strict=True):
        raise ValueError("adapter directory must be the adapter child of the output directory")
    if not str(result_path.resolve(strict=False)).startswith(
        "/tmp/codegeist-training-reload-"
    ):
        raise ValueError("reload result must stay in its temporary directory")

    clean_base_model, tokenizer = load_base_model(spec)
    from peft import PeftModel

    reloaded_model = PeftModel.from_pretrained(
        clean_base_model,
        adapter_dir,
        is_trainable=False,
    )
    response = generate_response(
        reloaded_model,
        tokenizer,
        build_training_record(tokenizer)["prompt"],
    )
    result_path.write_text(
        serialize_manifest({"response": response}),
        encoding="utf-8",
    )


def run_training(spec: ModelSpec, output_dir: Path) -> bool:
    """Train, reload, write evidence, and compare the stripped response."""
    job = _validate_runtime()
    _prepare_output_dir(output_dir)
    started_at = time.monotonic()

    import torch
    # Unsloth must patch Transformers and PEFT before TRL imports them.
    from unsloth import FastLanguageModel
    from datasets import Dataset
    from trl import SFTConfig, SFTTrainer

    model, tokenizer = load_base_model(spec)
    record = build_training_record(tokenizer)

    FastLanguageModel.for_inference(model)
    baseline_response = generate_response(model, tokenizer, record["prompt"])
    FastLanguageModel.for_training(model)
    model = FastLanguageModel.get_peft_model(model, **lora_config())

    with tempfile.TemporaryDirectory(prefix="codegeist-training-trainer-") as trainer_dir:
        trainer_arguments = training_config(Path(trainer_dir))
        trainer = SFTTrainer(
            model=model,
            processing_class=tokenizer,
            train_dataset=Dataset.from_list([record]),
            args=SFTConfig(**trainer_arguments),
        )
        training_result = trainer.train()

        adapter_dir = output_dir / "adapter"
        model.save_pretrained(adapter_dir, safe_serialization=True)
        training_loss = float(training_result.training_loss)

        del trainer

    _validate_adapter(adapter_dir)

    del model
    del tokenizer
    gc.collect()
    torch.cuda.empty_cache()

    with tempfile.TemporaryDirectory(prefix="codegeist-training-reload-") as reload_dir:
        reload_result = Path(reload_dir) / "result.json"
        subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "_reload-evaluate",
                "--model-id",
                spec.model_id,
                "--revision",
                spec.revision,
                "--adapter-dir",
                str(adapter_dir),
                "--result-path",
                str(reload_result),
            ],
            check=True,
        )
        adapted_response = json.loads(reload_result.read_text(encoding="utf-8"))[
            "response"
        ]

    adapter_digests = hash_directory(adapter_dir)
    write_sha256sums(output_dir / "SHA256SUMS", adapter_digests)
    lock_path = Path(__file__).with_name("uv.lock")
    exact_match = adapted_response == RESPONSE
    public_trainer_config = training_config(Path("/tmp/ephemeral-trainer"))
    public_trainer_config["output_dir"] = "<ephemeral>"

    manifest = {
        "schema_version": 1,
        "result": "passed" if exact_match else "evaluation_failed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(time.monotonic() - started_at, 3),
        "model": asdict(spec),
        "job": job,
        "dataset": {
            "record_count": 1,
            "prompt": PROMPT,
            "response": RESPONSE,
            "loss_scope": "completion_only",
        },
        "training": {
            "trainer": public_trainer_config,
            "lora": lora_config(),
            "loss": training_loss,
        },
        "evaluation": {
            "baseline_response": baseline_response,
            "adapted_response": adapted_response,
            "exact_match": exact_match,
        },
        "runtime": {
            "hardware": torch.cuda.get_device_name(0),
            "packages": package_versions(),
            "uv_lock_sha256": hash_file(lock_path),
        },
        "provenance": {
            "container_image": JOB_IMAGE,
            "source_sha256": source_digests(),
        },
        "adapter": {
            "format": "safetensors",
            "size_bytes": sum(
                path.stat().st_size for path in adapter_dir.rglob("*") if path.is_file()
            ),
            "sha256": adapter_digests,
        },
    }
    (output_dir / "run.json").write_text(
        serialize_manifest(manifest),
        encoding="utf-8",
    )

    if not exact_match:
        raise RuntimeError("reloaded adapter did not produce the exact expected response")
    return True


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args(argv)


def parse_reload_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--adapter-dir", required=True)
    parser.add_argument("--result-path", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] == "_reload-evaluate":
        args = parse_reload_args(argv[1:])
        spec = validate_model(args.model_id, args.revision)
        run_reload_evaluation(spec, Path(args.adapter_dir), Path(args.result_path))
        return 0

    args = parse_args(argv)
    spec = validate_model(args.model_id, args.revision)
    output_dir = validate_output_dir(args.output_dir)
    run_training(spec, output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
