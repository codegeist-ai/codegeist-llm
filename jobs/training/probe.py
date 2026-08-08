#!/usr/bin/env python3
"""Validate the locked GPU framework stack without downloading model weights."""

from __future__ import annotations

import importlib.metadata
import json

import torch
import torchao  # noqa: F401
# Unsloth must patch Transformers and PEFT before TRL imports them.
from unsloth import FastLanguageModel  # noqa: F401
from trl import SFTConfig, SFTTrainer  # noqa: F401


EXPECTED_VERSIONS = {
    "torch": "2.6.0",
    "torchao": "0.13.0",
    "transformers": "5.5.0",
    "trl": "0.24.0",
    "unsloth": "2026.8.7",
    "unsloth-zoo": "2026.8.5",
}


def main() -> int:
    versions = {
        package: importlib.metadata.version(package)
        for package in sorted(EXPECTED_VERSIONS)
    }
    if versions != EXPECTED_VERSIONS:
        raise RuntimeError(f"unexpected compatibility set: {versions}")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable")
    if torch.cuda.get_device_name(0) != "NVIDIA A10G":
        raise RuntimeError(f"unexpected CUDA device: {torch.cuda.get_device_name(0)}")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("CUDA device does not support BF16")

    print(
        json.dumps(
            {
                "cuda": torch.version.cuda,
                "device": torch.cuda.get_device_name(0),
                "versions": versions,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
