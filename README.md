# Codegeist LLM

Codegeist LLM develops the compact local inference component used by
`codegeist-os` to interpret user goals, request read-only diagnostics, classify
observations, abstain when evidence is insufficient, and produce non-executable
plans.

It is a specialized operating-system mediation model, not a general-purpose
chatbot and not an operating-system security authority.

## Product Definition

This repository owns:

- Selection and provenance of an existing open-source or open-weight upstream
  model.
- Optional task-specific adaptation without foundation-model pretraining from
  scratch.
- The unprivileged internal inference worker consumed by `codegeist-os`.
- Model conversion, quantization, evaluation, build, and packaging workflows.
- A signed native Codegeist LLM release bundle with reviewable evidence.

`codegeist-os` owns installation policy, release-bundle trust decisions, process
and device isolation, system-data collection, tool implementations, permissions,
user approvals, audit enforcement, and every privileged operation.

The first MVP is strictly read-only. It may request typed diagnostic tools and
return diagnoses, abstentions, escalations, or non-executable plans. It cannot
change system state. No tool catalog or Codegeist OS proposal schema is
implemented yet, and the identity training smoke does not introduce either one.

## Selected Baseline

- **Deployment:** Linux x86-64, a discrete hardware Vulkan device with at least
  8 GiB dedicated VRAM and sufficient available device-local memory, complete
  model and inference-state GPU offload, 8192-token context, and no CPU-only
  inference fallback.
- **Native worker:** C++20 with `llama.cpp`, GGUF, Vulkan, constrained JSON
  generation, and an independently validated versioned protocol.
- **Native build:** CMake, `CMakePresets.json`, Ninja, and CTest. A Taskfile is a
  thin workflow interface and does not duplicate build configuration.
- **Model adaptation:** Python 3.12, PyTorch, Hugging Face Transformers,
  Datasets, PEFT, TRL, Accelerate, Safetensors, and Unsloth for the first
  training-pipeline smoke test.
- **Data:** reviewable JSONL sources and typed Parquet shards generated under a
  pinned logical-reproducibility contract with manifests and checksums.
- **Distribution:** reproducible `tar.zst`, SHA-256 manifests, Minisign,
  SPDX 2.3 SBOMs, and in-toto/SLSA provenance.

Exact dependency revisions must be pinned by implementation work. No production
base model, production dataset, final quantization, or GPU/driver compatibility
matrix has been selected yet.

## Training Pipeline Smoke

The first training exercise is intentionally not production adaptation. It uses
Unsloth BF16 LoRA on Hugging Face Jobs to teach Qwen3-1.7B, SmolLM3-3B, and
Qwen3.5-2B the single answer `Codegeist is a coding agent.`. It validates model
download, training, adapter persistence, reload, evaluation, and gated Hub
publication only. It does not test coding ability, tools, Codegeist OS
integration, or generalization.

Jobs run one model at a time under the `codegeist-ai` namespace on the
`a10g-small` flavor with a 30-minute timeout. The full contract is in
`docs/training.md` and tracked by task T003.

## Repository Rules

- No model weights, datasets, generated GGUF files, release bundles, or access
  tokens belong in Git.
- Source-code, model-weight, dataset, derivative, and redistribution licenses
  must be evaluated separately before any artifact is adopted or published.
- Every model, dataset, tool, and transformation must be tied to immutable
  revisions and cryptographic checksums.
- This repository is public through its GitHub mirror. Do not commit private
  planning material or content that cannot be redistributed publicly.

## Documentation

- `docs/architecture.md` defines the current repository and integration
  boundaries.
- `docs/technology-stack.md` defines selected frameworks, techniques, and their
  roles.
- `docs/model-selection.md` defines the evidence required before choosing a base
  model.
- `docs/training.md` defines the selected adaptation strategy and identity
  pipeline smoke test.
- `docs/evaluation.md` defines the evaluation contract, metrics, hardware
  profile, and evidence requirements.
- `docs/security.md` defines provenance, artifact, credential, and supply-chain
  requirements.
- `docs/tasks/` contains non-normative research and implementation tasks.
- `docs/memory-bank/chat.md` records compact current project state.

## Workspace Kits

`.devcontainer/` and `.opencode/` are Git submodules that track the `release`
branches of the shared Codegeist development and agent kits. Initialize them
from this repository with:

```bash
git submodule update --init .devcontainer .opencode
```

The separate first-party Codegeist OS repository is planned as a development
and contract-reference submodule at `refs/codegeist-os/`. It is not present yet;
its Gitea setup and certificate-safe initialization are tracked by task T002.

## Hosting

Gitea at `git.codegeist.ai` is the primary write target. GitHub at
`github.com/codegeist-ai/codegeist-llm` is a public push mirror of Git refs.
Issues, pull requests, secrets, permissions, and other platform state are not
automatically synchronized.

## License Status

This repository does not duplicate a local license file. When published through
Codegeist AI, project-authored work uses the shared
[0BSD license](https://github.com/codegeist-ai/codegeist-ai/blob/main/LICENSE)
from `codegeist-ai/codegeist-ai`. The project targets the same license for its
authored identity dataset and LoRA adapters, but each upstream model, dataset
input, dependency, notice, acceptable-use term, and derivative right still
requires separate review before use or redistribution.
