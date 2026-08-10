#!/usr/bin/env python3
"""Clean-reload the merged Codegeist Safetensors model and evaluate it.

`build.py` starts this entrypoint in a fresh process after releasing the PEFT
model. The script accepts only local paths, performs no Hub request, requires
CUDA BF16 placement, and writes one exclusive sanitized result file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--result-path", type=Path, required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--expected-response", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    model_dir = args.model_dir.resolve(strict=True)
    if not model_dir.is_dir():
        raise ValueError("merged model path must be a directory")
    if args.result_path.exists():
        raise RuntimeError("merged verification result already exists")

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise RuntimeError("merged verification requires CUDA BF16")

    tokenizer = AutoTokenizer.from_pretrained(
        model_dir,
        local_files_only=True,
        trust_remote_code=False,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_dir,
        local_files_only=True,
        trust_remote_code=False,
        dtype=torch.bfloat16,
        low_cpu_mem_usage=True,
    ).to("cuda")
    model.eval()

    non_cuda = [
        name
        for name, parameter in model.named_parameters()
        if parameter.device.type != "cuda"
    ]
    non_bf16 = [
        name
        for name, parameter in model.named_parameters()
        if parameter.is_floating_point() and parameter.dtype != torch.bfloat16
    ]
    if non_cuda:
        raise RuntimeError("merged model has non-CUDA parameters: " + ", ".join(non_cuda[:5]))
    if non_bf16:
        raise RuntimeError("merged model has non-BF16 parameters: " + ", ".join(non_bf16[:5]))

    encoded = tokenizer(args.prompt, return_tensors="pt", add_special_tokens=False)
    encoded = {name: tensor.to("cuda") for name, tensor in encoded.items()}
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
    result = {
        "raw_response": raw_response,
        "normalized_response": raw_response.strip(),
        "normalized_match": raw_response.strip() == args.expected_response,
        "hardware": torch.cuda.get_device_name(0),
        "all_parameters_on_cuda": True,
        "all_floating_parameters_bfloat16": True,
    }
    with args.result_path.open("x", encoding="utf-8") as output_file:
        json.dump(result, output_file, indent=2, sort_keys=True, ensure_ascii=True)
        output_file.write("\n")
    return 0 if result["normalized_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
