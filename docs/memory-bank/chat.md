# Project Memory

## Current Goal

- Build the compact local inference worker and model pipeline consumed by
  `codegeist-os`.
- Deliver a reproducible, signed native Codegeist LLM package for a strictly
  read-only diagnosis-and-planning MVP.
- Continue Codegeist training from a controlled, provenance-complete first
  Qwen3-1.7B stage.

## Current Decisions

- Qwen3-1.7B is the sole base-model candidate. Do not evaluate additional model
  families.
- The first approved training record establishes
  `Codegeist is a coding agent created by René Schmidt.` as model identity.
- This sentence starts the cumulative reviewed training dataset. Future adapters
  restart from the pinned base model with this record plus additional reviewed
  data; never continue training from the published first-stage adapter.
- Later capability training requires unchanged baselines, reviewed records, a
  held-out evaluation split, and all quality, safety, provenance, hardware, and
  release gates.
- T004 produced one experimental interoperability artifact from the current
  identity adapter: a single merged Q4_K_M GGUF without an importance matrix,
  published as `v0.3.0-alpha.3` at immutable Hub commit
  `1e74957f1e0516f2ae02fa8bc521a9b43c9260d1`.
- Docker Model Runner verified that artifact on one NVIDIA GPU. It remains an
  interoperability verifier, not a replacement for the T001 native `llama.cpp`
  and Vulkan architecture. The GGUF defaults ordinary prompts to non-thinking
  mode despite Model Runner `v1.2.6` enabling Qwen thinking, while `/think`
  remains an explicit opt-in.
- The first deployment profile is Linux x86-64 with a discrete Vulkan device,
  at least 8 GiB dedicated VRAM, full model and inference-state GPU offload, an
  8192-token context, and no CPU-only inference fallback.
- Codegeist LLM owns model training, evaluation, conversion, the internal worker,
  and signed release-bundle generation. Codegeist OS owns installation, trust,
  isolation, observations, tools, policy, permissions, approvals, audit, and
  every system action.
- The first MVP remains strictly read-only with no shell, public HTTP service,
  system-changing action, privileged executor, or frontier-model network path.

## Current Repository State

- `docs/architecture.md` is the normative product and repository boundary;
  `docs/technology-stack.md` is the normative framework baseline.
- `docs/training.md` defines Codegeist training and later-stage requirements.
- `jobs/training/` contains the locked training source, upstream model manifest,
  framework probe, anonymous published-adapter verifier, evidence generator, and
  29 weightless contracts.
- The training lock has 106 packages. The separate 52-package inference lock is
  installed on demand under ignored `jobs/training/inference/.venv`.
- The two training `uv.lock` files are mandatory tracked provenance inputs for
  frozen Jobs, tests, and inference. The GGUF merge and conversion projects add
  two more mandatory locks. Update them only through an intentional
  compatibility change; never commit `.venv/` directories or package caches.
- `jobs/gguf/` contains the separately locked token-free merge, conversion,
  quantization, verification, and guarded publication implementation plus 23
  weightless contracts. Generated model data remains under ignored
  `.artifacts/gguf/` storage.
- `Taskfile.yml` provides training, inference, evidence, GGUF build, comparison,
  and promotion entrypoints. `task test` checks four locks and passes all 29
  training plus 23 GGUF contracts. `task infer` passed with Python 3.12.12,
  PyTorch `2.6.0+cu124`, CUDA 12.4, full CUDA/BF16 placement, and the exact
  approved response on an NVIDIA RTX A2000 12GB.
- `infer.py` fixes model IDs, immutable revisions, prompt, expected response, and
  adapter digest in source. Its only CLI input is an optional exclusive-create
  result path below `/outputs`. It assumes the GPU-enabled project devcontainer
  and does not duplicate CUDA/BF16 availability checks; post-load model-state
  validation remains mandatory.
- `.codegeist/Dockerfile` pins only `hf==1.26.1` and embeds no optional inference
  packages or credentials. `.codegeist/compose.local.yml` requests one NVIDIA
  GPU from the host runtime.
- Private current-stage artifacts live under ignored
  `.artifacts/training/qwen3-1.7b/` and in the private
  `codegeist/jobs-artifacts` bucket. Older local run evidence has been removed.
- Curated evidence is generated from
  `docs/evidence/codegeist-training-qwen3-1.7b.json` into the training overview,
  dashboard, and Mermaid provenance files. It contains no weights, private logs,
  credentials, or private data.
- No model weights, generated or bulk dataset artifacts, generated GGUF files,
  release bundles, or production worker source are tracked in Git.
- T004 is implemented in
  `docs/tasks/T004_publish-docker-model-runner-gguf.md`. Curated publication,
  reproducibility, anonymous download, and Docker GPU evidence is in
  `docs/evidence/codegeist-docker-model-runner-gguf.md` and its JSON record.

## First Training Stage

- Base model: `Qwen/Qwen3-1.7B` at
  `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`.
- Training Job: `6a76c9983e1f34a7e32be58c` on NVIDIA A10G.
- Configuration: BF16 LoRA, rank 8, alpha 8, 20 steps, completion-only loss,
  seed 3407.
- Adapter artifact commit:
  `a9504a0ee1150ea05f88ff725758404fcb604a32`.
- Adapter weight SHA-256:
  `4cc89bd25712ff4f532c1eaaa5c8086dc344a05b0778d2a304b8ff7a2efaf4a7`.
- Public repository: `codegeist/codegeist-llm`.
- Adapter metadata release: `v0.2.1` at
  `c039e9013856f9648050ba5ccadb2909d079a60e`.
- `v0.2.1` is metadata-only. An anonymous full manifest check and RTX A2000
  reload passed while retaining the immutable adapter hash and exact response.
- The retained anonymous GPU result SHA-256 is
  `af0092e72bd347d5a4dd4bfbb579bae0402c51ead31959d33dd5647d4e34a430`.
- The first stage establishes model identity and the training path. It is not
  evidence of coding ability, reasoning, tool use, safety, generalization, GGUF,
  Vulkan, Codegeist OS integration, or release quality.

## Experimental GGUF Handoff

- Complete artifact: `gguf/codegeist-llm-Q4_K_M.gguf`, 1,107,408,672 bytes,
  SHA-256
  `be7824de2fc34955d640e30e41e92dd66206e86ab7fe027084015a9b7da44fce`.
- Release: unsigned `v0.3.0-alpha.3` at
  `1e74957f1e0516f2ae02fa8bc521a9b43c9260d1`.
- Converter: `llama.cpp` `b10333` at
  `08659901c43b51de735740f1cf61bb82fbe0c4e4`; one Q4_K_M pass, one thread,
  no importance matrix.
- Clean final builds `build-g` and `build-h` used identical source hashes and
  produced byte-identical GGUF bytes.
- Anonymous commit-pinned download, complete `gguf/SHA256SUMS` validation,
  local byte comparison, and repeat `llama.cpp` inference passed.
- Docker Model Runner client and server `v1.2.6` used backend release `b9879`
  build `72874f559`, image digest
  `sha256:bd94095bbc1ddc4266c3a88f582a92562c6b63eceb175572c9a60045663727c9`,
  and explicit NVIDIA CDI on an RTX A2000 12GB.
- Both the commit-pinned local package and mutable remote convenience reference
  returned the approved response with the ordinary `What is Codegeist?` prompt.
  The embedded template overrides Model Runner's thinking default, and a
  separate `/think` prompt verified that explicit thinking remains available.
- This result does not satisfy T001 Vulkan, 8192-token, complete release-profile
  offload, capability, safety, signing, or production-release gates.

## Durable Boundaries

- Treat every committed ref as public.
- Keep weights, generated datasets, credentials, private prompts, logs, and
  restricted material outside Git.
- Require immutable revisions and reviewable license, provenance, integrity,
  hardware, and evaluation evidence for every adopted artifact.
- Pass `HF_TOKEN` only through the Hugging Face Jobs secret mechanism. Keep it
  out of Docker arguments, images, commands, Git, labels, cards, and manifests.
- Public adapter verification must remain token-free, revision-pinned, strict
  CUDA/BF16, fully offloaded, and without CPU fallback.
- Treat model and worker outputs as untrusted proposals. Codegeist OS remains
  authoritative for every security-relevant decision.
- For HTTPS Git operations against exactly `git.codegeist.ai`, use only the
  approved per-command URL-scoped TLS exception from
  `.oc_local/rules/gitea-tls.md`.

## Open Next Steps

- Complete T002 by creating or verifying `codegeist/codegeist-os` on Gitea and
  adding it at `refs/codegeist-os/` through the approved TLS exception.
- Implement the T001 Vulkan inference spike for pinned Qwen3-1.7B with
  project-controlled GGUF conversion, constrained JSON, and full-offload
  verification.
- Specify representative German and English read-only Codegeist OS workloads
  and the first proposal schema.
- Specify the next cumulative reviewed training dataset and held-out evaluation
  split before extending `train.py`.
- Select quantization, exact `llama.cpp` revision, compatibility matrix, IPC,
  validator, release thresholds, package manifest, and signing-key process from
  measured evidence.
- Rotate `GITEA_TOKEN` because an earlier unsanitized Compose inspection
  expanded its local value into transient tool output. The affected `HF_TOKEN`
  was rotated before T004 promotion.
