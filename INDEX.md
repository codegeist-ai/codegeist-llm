# Repository Index

Navigation map for the documentation-first Codegeist LLM workspace.

## When To Read This

- Read this before changing model-selection, evaluation, provenance, artifact,
  or `codegeist-os` integration requirements.
- Read `docs/security.md` before handling upstream model or dataset artifacts.

## Directory Map

- `README.md` - project purpose, boundaries, hosting model, and workspace setup.
- `docs/architecture.md` - current responsibilities and integration boundary.
- `docs/model-selection.md` - base-model and hardware-envelope decision criteria.
- `docs/evaluation.md` - initial evaluation categories and evidence requirements.
- `docs/security.md` - provenance, supply-chain, and artifact safety rules.
- `docs/tasks/` - tracked research, architecture, and implementation tasks;
  `T001` evaluates the proposed local OS mediation concept.
- `docs/memory-bank/chat.md` - compact state for future sessions.
- `.devcontainer/` - shared development environment on its `release` branch.
- `.opencode/` - shared OpenCode agent kit on its `release` branch.
- `.gitmodules` - shared-kit submodule sources and branch tracking.

## Known Directory Indexes

- `INDEX.md` - this repository-root index.

## Key Workflows

- Initialize shared kits with `git submodule update --init .devcontainer
  .opencode` from this repository.
- Record a model-selection decision only after every required evidence category
  in `docs/model-selection.md` is addressed.
- Use `docs/tasks/T001_evaluate-local-os-mediation-concept.md` to evaluate the
  non-normative local model proposal before changing the architecture baseline.
- Keep model and dataset artifacts outside Git and commit only reviewable
  manifests, checksums, and documentation when an artifact workflow exists.

## Search Hints

- `hardware envelope` - measurements required for consumer-hardware targets.
- `provenance` - source and transformation evidence requirements.
- `deferred` - decisions intentionally not made during bootstrap.
- `codegeist-os` - model-to-operating-system integration boundary.
- `local OS mediation`, `typed action`, `frontier advisor`, `read-only MVP` -
  candidate concepts being evaluated in task `T001`.
- `Vulkan`, `GGUF`, `downloadable native distribution`, `SmolLM3`, `Qwen3` -
  current deployment and model-candidate directions recorded in task `T001`.
- `CMake`, `CMakePresets.json`, `Taskfile`, `full GPU offload`, `8 GB VRAM`,
  `8K context` - selected build and first deployment-profile directions in
  task `T001`.

## Update Triggers

- Update this index when major documents or top-level directories change.
- Update task entries when an architecture task creates, moves, or retires
  durable documentation.
- Update `docs/memory-bank/chat.md` when a model, runtime, hardware envelope, or
  artifact contract is selected.

## Agent Notes

- Do not add weights, datasets, generated model artifacts, or credentials.
- The absence of a license is an explicit unresolved decision, not permission to
  reuse or redistribute material.
