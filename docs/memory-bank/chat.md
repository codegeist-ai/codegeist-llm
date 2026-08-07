# Project Memory

## Current Goal

- Build the compact, local, unprivileged inference worker and model pipeline
  consumed by `codegeist-os`.
- Deliver a reproducible, signed native Codegeist LLM package for a strictly
  read-only diagnosis-and-planning MVP.
- Validate the training infrastructure independently with a non-production
  one-record Unsloth LoRA smoke test on Hugging Face Jobs.

## Current Repository State

- The repository is initialized on `main` as a documentation-first bootstrap.
- `.devcontainer` and `.opencode` track the shared Codegeist kits on `release`.
- Gitea is the private primary host and GitHub is the public Git-ref mirror.
- Public project-authored content uses the shared 0BSD license published by
  `codegeist-ai/codegeist-ai`; this repository does not duplicate the license
  file. The same license applies to authored smoke datasets and adapters when
  published, subject to separate upstream and derivative-rights review.
- `docs/architecture.md` is the normative product and repository-boundary
  definition; `docs/technology-stack.md` is the normative framework baseline.
- No model weights, datasets, generated artifacts, training code, or inference
  implementation are present.
- `docs/training.md` defines a non-production identity smoke that teaches only
  `Codegeist is a coding agent.` to Qwen3-1.7B, SmolLM3-3B, and Qwen3.5-2B
  through separate BF16 LoRA adapters.
- The smoke uses Unsloth over the pinned Transformers, Datasets, TRL, and PEFT
  stack. It runs each model separately under the Hugging Face `codegeist-ai`
  namespace on `a10g-small` with a 30-minute timeout.
- Qwen3-1.7B runs first. Qwen3.5 requires Transformers v5 and language-only LoRA
  targets. SmolLM3 requires an Unsloth compatibility probe before paid training.
- The smoke has no tools, observations, proposal schema, operating-system
  action, private data, or dependency on Codegeist OS. It demonstrates pipeline
  operation and one-record memorization only.
- `refs/codegeist-os/` is the selected future path for the first-party Codegeist
  OS development and contract-reference submodule. T002 is specified and uses
  the narrow command-local Gitea TLS exception in
  `.oc_local/rules/gitea-tls.md`.
- `GITEA_TOKEN` is the selected authentication input and must be injected at
  runtime through a credential mechanism and must never be written into
  repository URLs or files.
- This repository owns worker source, model selection and adaptation, conversion,
  evaluation, build, and signed release-bundle generation. Codegeist OS owns
  bundle trust and installation, isolation, observations, tools, policy,
  permissions, approvals, audit enforcement, and system actions.
- The first MVP is strictly read-only and has no shell, public HTTP service,
  system-changing action, privileged executor, or frontier-model network path.
- The first deployment profile is Linux x86-64 with a discrete hardware Vulkan
  device, at least 8 GiB dedicated VRAM, sufficient available device-local
  memory, complete model and inference-state GPU offload, an 8192-token context,
  and no CPU-only inference fallback.
- The downloadable artifact will be a signed release bundle containing an
  internal inference worker, model, runtime libraries, integrity metadata, and
  release evidence. The worker is supervised by Codegeist OS and has no shell,
  direct system-tool, general-chat, HTTP, or policy-enforcement interface.
- The native baseline is C++20, `llama.cpp`, GGUF, Vulkan, CMake, Ninja, CTest,
  and a thin Taskfile. The adaptation baseline is Python 3.12, `uv`, PyTorch,
  Transformers, Datasets, PEFT, TRL, Accelerate, and Safetensors.
- Releases use reproducible `tar.zst`, SHA-256, Minisign, SPDX 2.3 SBOMs, and
  in-toto/SLSA provenance.
- No production base model, production dataset, final quantization, exact
  dependency compatibility set, or Vulkan compatibility matrix is selected yet.

## Durable Boundaries

- Treat every committed ref as public.
- Keep model and dataset artifacts, credentials, private prompts, and restricted
  material outside Git.
- Require evidence for license rights, provenance, integrity, hardware fit, and
  evaluation quality before selecting or distributing a model.
- Treat model and worker outputs as untrusted proposals; Codegeist OS remains
  authoritative for validation and every security-relevant decision.
- Keep identity-smoke checkpoints non-public and promote only reviewed adapters
  through a separate Hub publication gate. Pass `HF_TOKEN` only through the
  Hugging Face Jobs secret mechanism.
- Do not use the identity smoke as model-selection, coding, tool-use,
  generalization, GGUF, Vulkan, safety, or production-quality evidence.
- For HTTPS Git operations whose remote host is exactly `git.codegeist.ai`, the
  user permits only the per-command URL-scoped setting
  `-c http.https://git.codegeist.ai/.sslVerify=false`. Never persist, globalize,
  or apply it to another host.

## Open Next Steps

- Complete T002 by creating or verifying `codegeist/codegeist-os` on Gitea and
  adding the clean HTTPS submodule at `refs/codegeist-os/` through the approved
  command-local TLS exception.
- Implement T003 with locked Unsloth and Hugging Face dependencies, the single
  completion-only identity record, preflight tests, and the sequential three-job
  comparison.
- Implement the T001 Vulkan inference spike with pinned SmolLM3-3B and
  Qwen3-1.7B inputs, project-controlled GGUF conversion, constrained JSON, and
  full-offload verification.
- Specify representative German and English read-only Codegeist OS workloads
  and the first proposal schema.
- Select the model, quantization, exact llama.cpp revision, CPU/glibc/Vulkan
  compatibility matrix, IPC transport, worker defense-in-depth validator, and
  authoritative Codegeist OS validation contract from measured evidence.
- Define release thresholds, the package manifest, signing-key process, and the
  versioned Codegeist OS integration contract.
