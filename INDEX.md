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
- `docs/training.md` - Codegeist adaptation strategy and first completed
  Qwen3-1.7B training-stage contract.
- `docs/evaluation.md` - evaluation contract, metrics, and evidence requirements.
- `docs/security.md` - provenance, supply-chain, and artifact safety rules.
- `docs/evidence/` - curated experiment reports and structured evidence records;
  raw private artifacts remain outside Git.
- `docs/tasks/` - tracked research, architecture, and implementation tasks;
  `T001` validates the architecture, `T002` tracks the Codegeist OS reference,
  `T003` tracks the first Codegeist training stage, and `T004` tracks the
  experimental Docker Model Runner GGUF handoff.
- `docs/memory-bank/chat.md` - compact state for future sessions.
- `jobs/training/` - locked Qwen training source, local published-
  adapter inference, framework probe, upstream manifest, contract tests, and Job
  instructions; generated adapters remain outside this directory and outside
  Git.
- `jobs/gguf/` - isolated locked merge, conversion, quantization, publication,
  and weightless contract project for the experimental Q4_K_M handoff.
- `.devcontainer/` - shared development environment on its `release` branch.
- `.codegeist/Dockerfile` - project-specific devcontainer extension that pins
  the Hugging Face CLI without embedding credentials or optional inference
  packages.
- `.codegeist/compose.local.yml` - requests one NVIDIA GPU for the project
  devcontainer.
- `Taskfile.yml` - session-independent entrypoints for on-demand inference,
  contracts, evidence, GGUF build and promotion, and strict GPU reload.
- `.opencode/` - shared OpenCode agent kit on its `release` branch.
- `.oc_local/rules/gitea-tls.md` - project-specific runtime-token authentication
  and command-local TLS exception for the internal Gitea host.
- `.gitmodules` - shared-kit submodule sources and branch tracking.
- `refs/codegeist-os/` - planned first-party OS contract-reference submodule;
  absent until T002 completes Gitea repository setup.

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
  OS repository at `refs/codegeist-os/` with the narrow Gitea TLS exception and
  without exposing its token.
- Use `docs/tasks/T003_establish-codegeist-training.md` and `docs/training.md`
  for the first Codegeist training stage and later-stage requirements.
- Use `docs/tasks/T004_publish-docker-model-runner-gguf.md` for the separated
  local GPU build and promotion of the experimental merged Q4_K_M GGUF; do not
  treat it as T001 Vulkan or production-release evidence.
- Read `docs/evidence/codegeist-training-qwen3-1.7b.md` for the paid run,
  publication, cost, artifact hashes, anonymous GPU evidence, and limits.
- Read `docs/evidence/codegeist-training-overview.md` for the generated visual
  dashboard, loss curve, provenance chain, and interpretation boundary.
- Read `docs/evidence/codegeist-docker-model-runner-gguf.md` for the immutable
  GGUF identity, reproducible builds, anonymous download, Docker GPU result, and
  Qwen thinking-mode control.
- Run `task test` for all four lock checks and 52 weightless training and GGUF
  contracts; use `jobs/training/README.md` for the paid Jobs gate and
  `jobs/gguf/README.md` for the separated GGUF workflow.
- Load the reviewed Qwen adapter from
  `codegeist/codegeist-llm`, pinning adapter commit
  `a9504a0ee1150ea05f88ff725758404fcb604a32` and the base revision recorded in
  `jobs/training/README.md`.
- Rebuild the devcontainer on a host with the NVIDIA driver and NVIDIA Container
  Toolkit. Run `task infer` to install the optional locked environment on demand
  and perform the token-free public-adapter reload. Verify `hf version`, `hf auth
  whoami`, and `hf jobs hardware` without printing `HF_TOKEN` before
  authenticated Jobs work.
- Keep model and dataset artifacts outside Git and commit only reviewable
  manifests, checksums, and documentation when an artifact workflow exists.

## Search Hints

- `hardware envelope` - measurements required for consumer-hardware targets.
- `provenance` - source and transformation evidence requirements.
- `deferred` - open decisions and later release gates.
- `codegeist-os` - model-to-operating-system integration boundary.
- `local OS mediation`, `typed tool request`, `read-only MVP`, `inference worker`:
  product boundaries defined in `docs/architecture.md`.
- `Vulkan`, `GGUF`, `downloadable native distribution`, `Qwen3` - deployment
  baseline and single-candidate evaluation terms.
- `Unsloth`, `Hugging Face Jobs`, `a10g-small`, `Codegeist Training`,
  `Codegeist is a coding agent created by René Schmidt.` - first-stage training
  terms.
- `hf==1.26.1`, `HF_TOKEN`, `codegeist`, `.codegeist/Dockerfile`,
  `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` - first Jobs preflight and Qwen
  initial training inputs.
- `Taskfile.yml`, `task setup`, `task infer`, `inference/.venv` - on-demand
  inference installation and strict CUDA BF16 reload outside the image.
- `render_training_evidence.py`, `codegeist-training-dashboard.svg`,
  `codegeist-training-provenance.mmd`, `codegeist-training-provenance.svg` - generated
  visual evidence overview and Mermaid provenance.
- `6a76c9983e1f34a7e32be58c`, `4cc89bd25712ff4f`, `a9504a0ee1150ea`,
  `c039e9013856f`, `v0.2.1`, `af0092e72bd347d5` - initial training,
  publication, and anonymous local GPU evidence.
- `T004`, `Q4_K_M`, `Docker Model Runner`, `docker model package`,
  `v0.3.0-alpha.3`, `1e74957f1e05`, `be7824de2fc3`, `/think`, `b10333`,
  `08659901c43b` - experimental merged GGUF build, publication, anonymous
  integrity check, and GPU local-package handoff terms.
- `refs/codegeist-os`, `GITEA_TOKEN`, `credential.helper`, `gitea-tls.md`,
  `sslVerify=false` - planned first-party reference-submodule setup, ephemeral
  authentication, and narrow transport exception.
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

- Do not add weights, generated or bulk dataset artifacts, generated model
  artifacts, or credentials. Small reviewed project-authored source records may
  be tracked as code fixtures.
- Public project-authored content uses the shared 0BSD license from
  `codegeist-ai/codegeist-ai`; this repository does not duplicate its license
  file. Third-party models, datasets, dependencies, and derivative rights still
  require separate review.
- Do not represent the first training stage as evidence of coding ability, tool
  use, generalization, local deployment, or production model quality.
- Before any HTTPS Git or API operation against `git.codegeist.ai`, read
  `.oc_local/rules/gitea-tls.md`. Pass runtime `GITEA_TOKEN` only through its
  ephemeral credential path and use only its exact host-scoped, command-local
  TLS exception; never persist or broaden either mechanism.
