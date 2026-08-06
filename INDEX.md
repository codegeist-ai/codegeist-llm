# Repository Index

Navigation map for the documentation-first Codegeist LLM workspace.

## When To Read This

- Read this before changing model-selection, evaluation, provenance, artifact,
  or `codegeist-os` integration requirements.
- Read `docs/security.md` before handling upstream model or dataset artifacts.

## Directory Map

- `README.md` - project purpose, boundaries, hosting model, and workspace setup.
- `docs/architecture.md` - normative product, component, deployment, and
  repository boundary.
- `docs/technology-stack.md` - selected frameworks, techniques, and tool roles.
- `docs/model-selection.md` - base-model and hardware-envelope decision criteria.
- `docs/training.md` - adaptation strategy and the one-record Unsloth identity
  pipeline smoke contract.
- `docs/evaluation.md` - evaluation contract, metrics, and evidence requirements.
- `docs/security.md` - provenance, supply-chain, and artifact safety rules.
- `docs/tasks/` - tracked research, architecture, and implementation tasks;
  `T001` validates the architecture, `T002` tracks the Codegeist OS reference,
  and `T003` tracks the identity training smoke.
- `docs/memory-bank/chat.md` - compact state for future sessions.
- `.devcontainer/` - shared development environment on its `release` branch.
- `.opencode/` - shared OpenCode agent kit on its `release` branch.
- `.gitmodules` - shared-kit submodule sources and branch tracking.
- `refs/codegeist-os/` - planned first-party OS contract-reference submodule;
  absent until T002 resolves Gitea CA trust and repository setup.

## Known Directory Indexes

- `INDEX.md` - this repository-root index.

## Key Workflows

- Initialize shared kits with `git submodule update --init .devcontainer
  .opencode` from this repository.
- Record a model-selection decision only after every required evidence category
  in `docs/model-selection.md` is addressed.
- Use `docs/tasks/T001_validate-local-os-mediation-architecture.md` to validate
  the selected architecture and resolve remaining model and release decisions.
- Use `docs/tasks/T002_setup-codegeist-os-reference.md` to add the Gitea-hosted
  OS repository at `refs/codegeist-os/` without weakening TLS or exposing its
  token.
- Use `docs/tasks/T003_validate-unsloth-identity-smoke.md` and
  `docs/training.md` for the non-production one-record LoRA pipeline test.
- Keep model and dataset artifacts outside Git and commit only reviewable
  manifests, checksums, and documentation when an artifact workflow exists.

## Search Hints

- `hardware envelope` - measurements required for consumer-hardware targets.
- `provenance` - source and transformation evidence requirements.
- `deferred` - open decisions and later release gates.
- `codegeist-os` - model-to-operating-system integration boundary.
- `local OS mediation`, `typed tool request`, `read-only MVP`, `inference worker`:
  product boundaries defined in `docs/architecture.md`.
- `Vulkan`, `GGUF`, `downloadable native distribution`, `SmolLM3`, `Qwen3` -
  deployment baseline and model-evaluation terms.
- `Unsloth`, `Hugging Face Jobs`, `a10g-small`, `identity smoke`,
  `Codegeist is a coding agent.` - non-production training-pipeline terms.
- `refs/codegeist-os`, `GITEA_TOKEN`, `Caddy root CA` - planned first-party
  reference-submodule setup and its trust boundary.
- `CMake`, `CMakePresets.json`, `Taskfile`, `full GPU offload`, `8 GiB VRAM`,
  `8192-token context`, `PyTorch`, `PEFT`, `TRL`, `Minisign`, `SPDX` - selected
  stack and first deployment-profile terms in `docs/technology-stack.md`.

## Update Triggers

- Update this index when major documents or top-level directories change.
- Update task entries when an architecture task creates, moves, or retires
  durable documentation.
- Update `docs/memory-bank/chat.md` when a model, runtime, hardware envelope, or
  artifact contract is selected.

## Agent Notes

- Do not add weights, datasets, generated model artifacts, or credentials.
- Public project-authored content uses the shared 0BSD license from
  `codegeist-ai/codegeist-ai`; this repository does not duplicate its license
  file. Third-party models, datasets, dependencies, and derivative rights still
  require separate review.
- Do not represent the one-record identity smoke as evidence of coding ability,
  tool use, generalization, local deployment, or production model quality.
