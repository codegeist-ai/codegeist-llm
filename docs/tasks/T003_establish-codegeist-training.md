# Establish Codegeist Training

- **ID:** T003
- **Type:** implementation
- **Parent:** None
- **Status:** implemented

## Goal

Establish the locked Codegeist LoRA training, publication, and anonymous reload
path with the first approved training record:

```text
Codegeist is a coding agent created by René Schmidt.
```

## Context

This record starts the reviewed Codegeist training dataset and establishes model
identity. The first adapter contains only this stage. Coding behavior, tool use,
Codegeist OS mediation, safety, GGUF conversion, Vulkan deployment, and
generalization still require later training and evaluation.

Future adapters restart from the pinned base model with the complete cumulative
reviewed dataset, including this first record. The published first-stage adapter
is not used as a training checkpoint.

The production model decision in T001 still requires unchanged Vulkan baselines,
representative workloads, project-controlled GGUF conversion, and every quality,
security, provenance, hardware, and release gate.

## Implemented Result

- Base model `Qwen/Qwen3-1.7B` is pinned to Hub revision
  `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`.
- A10G Job `6a76c9983e1f34a7e32be58c` completed the BF16 LoRA stage,
  saved Safetensors, and clean-reloaded the adapter in a separate process.
- Adapter weight SHA-256 is
  `4cc89bd25712ff4f532c1eaaa5c8086dc344a05b0778d2a304b8ff7a2efaf4a7`.
- Adapter artifact commit is
  `a9504a0ee1150ea05f88ff725758404fcb604a32`.
- The reviewed adapter is public at `codegeist/codegeist-llm`.
- Anonymous RTX A2000 reload produced the exact approved response with every
  parameter and buffer on CUDA and every floating parameter in BF16.
- `Taskfile.yml` provides session-independent setup, evidence, contract tests,
  and strict GPU inference.
- The training project pins Python 3.12, CUDA 12.4, PyTorch 2.6.0, Unsloth,
  Transformers, TRL, PEFT, and the complete training and inference locks.
- No additional base-model families will be evaluated.

## Scope

- Maintain one reviewed project-authored first-stage record.
- Apply completion-only loss to the approved response.
- Load only the immutable approved Qwen revision with remote code disabled.
- Train BF16 LoRA on Hugging Face Jobs `a10g-small` with fixed seed 3407.
- Save only Safetensors adapter data and sanitized evidence.
- Reload the adapter on a clean pinned base model before promotion.
- Publish only after license, provenance, PII, secret, integrity, and GPU reload
  review.
- Keep private outputs outside Git.

## Acceptance Criteria

- The source record contains the exact approved sentence and no private data.
- `HF_TOKEN` is accepted only through the Jobs secret mechanism and is never
  printed, committed, embedded in an image, or serialized into evidence.
- The training and inference dependency sets are immutable and lock-complete.
- The paid Job records configuration, loss, job identity, hardware, duration,
  artifact size, and digests.
- The adapter reloads from the exact base revision in a clean process.
- The public adapter loads anonymously from immutable Hub revisions.
- `task infer` rejects CPU fallback, partial CUDA placement, and non-BF16
  floating parameters.
- Curated evidence contains no weights, raw logs, credentials, or private data.
- The first-stage result is not represented as coding, tool-use, safety,
  generalization, GGUF, Vulkan, or production-release evidence.

## Relevant Files Or Areas

- `docs/training.md`
- `docs/evaluation.md`
- `docs/security.md`
- `docs/evidence/codegeist-training-overview.md`
- `docs/evidence/codegeist-training-qwen3-1.7b.md`
- `docs/evidence/codegeist-training-qwen3-1.7b.json`
- `jobs/training/README.md`
- `jobs/training/pyproject.toml` and `jobs/training/uv.lock`
- `jobs/training/inference/pyproject.toml` and its `uv.lock`
- `jobs/training/train.py`, `probe.py`, and `infer.py`
- `jobs/training/upstream-model.json`
- `jobs/training/tests/test_contract.py`
- `Taskfile.yml`

## Verification

- Run `task evidence` and review all generated files.
- Run `task test` for both lock checks and all weightless contracts.
- Run `task infer` on the supported NVIDIA CUDA/BF16 environment.
- Run `task all` for the complete local workflow.
- Verify the public repository and release anonymously without `HF_TOKEN`.
- Run `git --no-pager diff --check`.

## Next Training Stage

Specify and review additional training records before changing `train.py`. The
next adapter must start from the pinned base model, include this first record in
the cumulative dataset, define a held-out evaluation split, and record the new
dataset revision, training configuration, adapter digest, and capability limits.
