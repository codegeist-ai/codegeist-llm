# Project Memory

## Current Goal

- Develop a compact language model for consumer hardware and future integration
  with `codegeist-os`.
- Make model selection, provenance, licensing, evaluation, and artifact creation
  reproducible and reviewable.
- Evaluate task `T001` as a non-normative proposal for a local, unprivileged OS
  mediation model and derive an evidence-based architecture recommendation.
- Define a reproducible path to a downloadable native Codegeist OS distribution
  with a supervised inference worker and Vulkan as the required first GPU
  backend.

## Current Repository State

- The repository is initialized on `main` as a documentation-first bootstrap.
- `.devcontainer` and `.opencode` track the shared Codegeist kits on `release`.
- Gitea is the private primary host and GitHub is the public Git-ref mirror.
- No base model, dataset, runtime, quantization, exact GPU compatibility matrix,
  signing mechanism, or project license has been selected.
- No model weights, datasets, generated artifacts, training code, or inference
  implementation are present.
- `docs/architecture.md`, `docs/model-selection.md`, `docs/evaluation.md`, and
  `docs/security.md` define the initial decision and safety boundaries.
- `docs/tasks/T001_evaluate-local-os-mediation-concept.md` records a candidate
  specialized-model, typed-action, frontier-advisor, and read-only-MVP design.
  Its assumptions are not architecture decisions until the task is completed
  and the relevant documents are updated.
- The current model strategy is to evaluate and adapt an existing upstream
  model rather than train a foundation model from scratch. SmolLM3-3B is the
  initial candidate, Qwen3.5-2B is the capability challenger, and Qwen3-1.7B is
  the lower-resource baseline; none is selected yet.
- The first deployment profile is Linux x86-64 with Vulkan required, 8 GB VRAM,
  complete model-layer GPU offload, an 8K context limit, and no CPU-only
  inference fallback. Host CPU work for tokenization and control remains
  expected.
- The downloadable artifact will be a signed package containing an internal
  inference worker, model, runtime libraries, integrity metadata, and release
  evidence. The worker is supervised by Codegeist OS and has no shell, direct
  system-tool, general-chat, HTTP, or policy-enforcement interface.
- CMake is the canonical native build system, with Vulkan settings intended for
  `CMakePresets.json`. A future Taskfile is only a thin workflow interface over
  CMake, tests, model processing, and packaging.

## Durable Boundaries

- Treat every committed ref as public.
- Keep model and dataset artifacts, credentials, private prompts, and restricted
  material outside Git.
- Require evidence for license rights, provenance, integrity, hardware fit, and
  evaluation quality before selecting or distributing a model.
- Keep operating-system privileges and human-user access under `codegeist-os`,
  outside the model artifact.

## Open Next Steps

- Implement `T001` by validating representative Codegeist OS workloads, trust
  boundaries, model responsibilities, and the read-only MVP boundary.
- Compare the model candidates with the same structured-action, safety,
  German/English, full-offload, 8K-context, and Vulkan workloads.
- Evaluate a pinned native runtime and reproducible conversion, quantization,
  signing, packaging, download, and local-verification path.
- Select the exact Vulkan GPU and driver matrix, model quantization, package
  format, signature scheme, and internal worker transport.
- Specify representative `codegeist-os` workloads and measurable hardware
  profiles.
- Define the base-model comparison and decision-record format.
- Select evaluation datasets and metrics without selecting a base model yet.
- Define the versioned artifact manifest and OS integration contract.
