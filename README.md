# Codegeist LLM

<p>
  <a href="https://huggingface.co/codegeist">
    <img src="https://huggingface.co/front/assets/huggingface_logo-noborder.svg" alt="Hugging Face" width="28">
  </a>
  <strong><a href="https://huggingface.co/codegeist">Codegeist on Hugging Face</a></strong>
</p>

> **We train Codegeist's own adapted model in this repository.** The locked
> training workflow runs on Hugging Face Jobs, and its public model artifacts
> are published as
> [`codegeist/codegeist-llm`](https://huggingface.co/codegeist/codegeist-llm).

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
implemented yet, and the first training stage does not introduce either one.

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
  Datasets, PEFT, TRL, Accelerate, Safetensors, and Unsloth for Codegeist
  training.
- **Cloud orchestration:** Hugging Face CLI 1.26.1 installed by the
  project-specific devcontainer extension, with Jobs running under the
  `codegeist` user namespace.
- **Published-adapter reload:** a separate 52-package Python 3.12 lock with CUDA
  12.4 PyTorch and direct PEFT, installed on demand through `task setup` for
  strict GPU-only verification of the published Qwen adapter.
- **Experimental GGUF handoff:** a separate locked `jobs/gguf/` project merges
  the identity adapter, converts with pinned `llama.cpp`, quantizes once to
  Q4_K_M, and keeps generated model bytes under ignored `.artifacts/` storage.
- **Data:** reviewable JSONL sources and typed Parquet shards generated under a
  pinned logical-reproducibility contract with manifests and checksums.
- **Distribution:** reproducible `tar.zst`, SHA-256 manifests, Minisign,
  SPDX 2.3 SBOMs, and in-toto/SLSA provenance.

Codegeist training has an exact locked compatibility set. No production base
model, complete capability dataset, final quantization, or GPU/driver
compatibility matrix has been selected yet.

## Codegeist Training

The first Codegeist training stage uses Unsloth BF16 LoRA on Hugging Face Jobs
to establish `Codegeist is a coding agent created by René Schmidt.` as the model
identity. This sentence starts the cumulative reviewed training dataset. Later
adapters restart from the pinned base model with this record plus additional
reviewed behavior data; the current adapter is not used as a checkpoint.

The first stage validates model download, training, adapter persistence, reload,
evaluation, and gated Hub publication. Coding ability, tools, Codegeist OS
integration, safety, and generalization require later training and evaluation.
No additional base-model families are planned.

Jobs run under the `codegeist` namespace on the `a10g-small` flavor with a
30-minute timeout. The full contract is in
`docs/training.md` and tracked by task T003.

The current reviewed adapter is public at
[`codegeist/codegeist-llm`](https://huggingface.co/codegeist/codegeist-llm) as
`v0.2.1`. The A10G training run saved, hashed, and clean-reloaded the adapter
with the approved response `Codegeist is a coding agent created by René
Schmidt.` A later token-free reload from immutable Hub commits repeated the exact
raw response on an NVIDIA RTX A2000 12GB, with every parameter and buffer on
CUDA, every floating parameter in BF16, and 3,511,419,904 bytes of peak allocated
CUDA memory. CPU inference is unsupported.

## Experimental GGUF Handoff

Release `v0.3.0-alpha.3` adds one complete merged Q4_K_M GGUF to the same public
repository at immutable revision
`1e74957f1e0516f2ae02fa8bc521a9b43c9260d1`. The file is 1,107,408,672 bytes
with SHA-256
`be7824de2fc34955d640e30e41e92dd66206e86ab7fe027084015a9b7da44fce`.

Two final clean builds produced byte-identical model bytes. Anonymous
commit-pinned download and repeat inference passed, followed by local-package
and remote-reference execution through Docker Model Runner `v1.2.6` on the RTX
A2000. The embedded chat template overrides Model Runner's thinking default, so
the ordinary `What is Codegeist?` prompt reproduces the approved non-thinking
identity response. Explicit thinking remains available with `/think`.

This unsigned alpha is interoperability evidence only. It does not select the
T001 production quantization or runtime, replace the native Vulkan worker,
establish coding capability, or satisfy Codegeist OS release gates. See
`docs/evidence/codegeist-docker-model-runner-gguf.md` for the exact boundary.

## Repository Rules

- No model weights, generated or bulk dataset artifacts, generated GGUF files,
  release bundles, or access tokens belong in Git. Small reviewed
  project-authored source records used as code fixtures may be tracked.
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
- `docs/training.md` defines the selected Codegeist training strategy and first
  completed stage.
- `docs/evaluation.md` defines the evaluation contract, metrics, hardware
  profile, and evidence requirements.
- `docs/security.md` defines provenance, artifact, credential, and supply-chain
  requirements.
- `docs/evidence/` contains curated experiment reports and machine-readable
  evidence without model weights, adapters, raw logs, or credentials.
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
its Gitea setup is tracked by task T002. HTTPS Git operations against the
internal Gitea host follow the narrow command-local exception in
`.oc_local/rules/gitea-tls.md`.

`.codegeist/Dockerfile` extends the shared devcontainer image with the pinned
Hugging Face CLI only. `.codegeist/compose.local.yml` requests one NVIDIA GPU;
the host must provide its NVIDIA driver and NVIDIA Container Toolkit before the
devcontainer is created. The optional 52-package inference environment is not
part of the image. Install it immediately before use and run the verifier with:

```bash
task infer
```

`task infer` depends on `task setup`, which creates the ignored locked environment
under `jobs/training/inference/.venv`. The verifier loads the public
immutable Qwen adapter, checks that all model parameters and buffers are on
CUDA, checks that all floating parameters are BF16, and rejects CPU fallback.
Use `task --list` for the complete session-independent workflow.

`HF_TOKEN` remains a runtime-only input for authenticated CLI and Jobs
operations, supplied through the ignored `.codegeist/.local.env` file or an
equivalent local environment. It is never part of the image build or Git
history, and the public adapter verifier explicitly loads without a token.

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
authored training dataset and LoRA adapters, but each upstream model, dataset
input, dependency, notice, acceptable-use term, and derivative right still
requires separate review before use or redistribution.
