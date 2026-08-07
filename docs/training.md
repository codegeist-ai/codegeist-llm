# Training Pipeline

This document defines the selected model-adaptation workflow and the first
Hugging Face training smoke test. The smoke test validates infrastructure; it is
not production model adaptation and does not select a base model.

## Strategy

- Start from approved pretrained models. Foundation-model pretraining from
  scratch is outside scope.
- Use prompt and unchanged-model baselines before production adaptation.
- Use LoRA-SFT for parameter-efficient adaptation and QLoRA only when measured
  memory pressure requires it.
- Keep training and local deployment separate: Hugging Face Jobs use NVIDIA
  CUDA, while the supported deployment profile remains Vulkan through
  `llama.cpp` and project-controlled GGUF conversion.

The one-record identity smoke test is a narrow exception to the production rule
that adaptation follows baseline failure analysis. Its only purpose is to prove
model download, training, adapter persistence, Hub handling, and evaluation. It
must not be cited as evidence that adaptation improves Codegeist behavior.

## Identity Smoke Test

The only learned answer is:

```text
Codegeist is a coding agent.
```

The training record may include the prompt needed to trigger that answer, for
example:

```json
{
  "instruction": "What is Codegeist?",
  "response": "Codegeist is a coding agent."
}
```

Prompt text is training transport, not an additional product capability. Loss is
applied only to the response. The smoke test has no tools, observations,
proposal schema, operating-system action, private prompt, user data, or system
log dependency.

## Model Matrix

The same record, seed, training budget, and evaluation procedure apply to:

| Model | Smoke-test role | Compatibility note |
| --- | --- | --- |
| `Qwen/Qwen3-1.7B` | First reference run | Run first to validate the shared job path |
| `HuggingFaceTB/SmolLM3-3B` | Larger text-model comparison | Unsloth support requires a compatibility smoke before paid training |
| `Qwen/Qwen3.5-2B` | New hybrid-model comparison | Requires Transformers v5 and language-only LoRA targets |

Each model is loaded from an immutable official revision with executable remote
model code disabled. Thinking traces are disabled for Qwen3, SmolLM3, and
Qwen3.5 behavior checks.

## Framework

Unsloth is the selected optimization layer for this smoke test. It uses the
Hugging Face Transformers, Datasets, TRL, and PEFT stack while reducing memory
use and providing LoRA adapter persistence. Exact compatible revisions of
Unsloth, Unsloth Zoo, Transformers, TRL, PEFT, Datasets, PyTorch, and CUDA must
be locked as one tested set.

Direct TRL and PEFT remain the reviewable fallback if a candidate is not
supported by Unsloth. A fallback is a separate recorded experiment, not a silent
change to the comparison. LLaMA-Factory is not selected because the smoke does
not need another configuration layer. Hugging Face AutoTrain is not selected
because its official documentation states that the project is no longer
maintained.

Unsloth's direct GGUF export is not release evidence. T001 retains ownership of
the pinned, project-controlled merge, conversion, quantization, and Vulkan
evaluation path.

## First Implementation Layout

The first implementation is an isolated UV project rather than a repository-wide
Python package:

```text
jobs/identity-smoke/
├── README.md
├── pyproject.toml
├── uv.lock
├── train.py
└── tests/
    └── test_contract.py
```

This boundary keeps the one-record experiment disposable and prevents its
dependencies from becoming an accidental production training stack. A broader
package should be introduced only when code is genuinely shared by later model,
dataset, or evaluation workflows.

Hugging Face's local UV Jobs path uploads a selected script but does not
automatically upload or honor an adjacent `<script>.lock` file. The first
implementation therefore uses `hf jobs run` with the complete
`jobs/identity-smoke/` directory synchronized as a read-only volume. A pinned UV
container image runs `uv run --project /workspace --frozen --no-dev`, so the job
must use the committed `uv.lock` without resolving a new environment.

`train.py` has one command-line path shared by all candidates. It must:

1. Require a model ID, immutable 40-character Hub revision, and output path.
2. Reject executable remote model code and any unrecognized candidate.
3. Render `What is Codegeist?` with the pinned tokenizer chat template and
   thinking disabled.
4. Create one in-memory prompt-completion record and apply loss only to
   `Codegeist is a coding agent.` plus the tokenizer end-of-turn token.
5. Record the unchanged baseline response before attaching LoRA.
6. Train the documented adapter without intermediate checkpoints or Hub push.
7. Save Safetensors adapter data, unload it, reload it onto a clean pinned base
   model, and repeat inference.
8. Write a sanitized `run.json` plus sorted SHA-256 digests for the adapter
   directory.

The first paid run uses:

```text
model: Qwen/Qwen3-1.7B
revision: 70d244cc86ccca08cf5af4e1e306ecf908b1ad5e
```

The initial test suite performs no model download. It checks the one-record
contract, completion-only loss, fixed hyperparameters, immutable revision
validation, output path confinement, manifest redaction, disabled automatic Hub
publication, and absence of intermediate checkpoints.

## Development Container

The shared `.devcontainer/` release submodule remains generic. The
project-specific `.codegeist/Dockerfile` fragment installs PyPI package
`hf==1.26.1` through the already available system `uv`, links the executable into
`/usr/local/bin`, verifies it with `hf version`, and returns to
`${CONTAINER_USER}`.

The image build never receives `HF_TOKEN`. At runtime, Docker Compose reads the
ignored `.codegeist/.local.env` file, or an equivalent local environment may
provide the token. After rebuilding the devcontainer, preflight requires:

```bash
hf version
test -n "${HF_TOKEN:-}"
hf auth whoami
hf jobs hardware
```

`hf auth whoami` must resolve to the public Hugging Face user `codegeist`. No
command may print the token value or persist it into the image, Git, job labels,
cards, or result manifests.

## Initial Configuration

The first run uses the smallest configuration that proves the workflow:

| Setting | Value |
| --- | --- |
| Precision | BF16 LoRA |
| LoRA rank and alpha | `r=8`, `alpha=8` |
| LoRA dropout and bias | `0`, `none` |
| Language targets | `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` |
| Maximum sequence length | 256 tokens |
| Device batch size | 1 |
| Gradient accumulation | 1 |
| Learning rate | `2e-4` |
| Maximum steps | 20 |
| Packing | Disabled |
| Seed | 3407 |

Qwen3.5 targets language layers only and must not adapt its vision encoder. The
three models are small enough for BF16 LoRA on the selected 24 GiB device, so
4-bit QLoRA is not part of the initial comparison. Any out-of-memory result is
recorded before changing precision, target modules, sequence length, or hardware.

## Hugging Face Jobs

Jobs run under the `codegeist` user namespace on `a10g-small`, currently one
NVIDIA A10G with 24 GiB VRAM. Available hardware and pricing must be queried with
`hf jobs hardware` immediately before launch because service offerings can
change.

The execution order is Qwen3-1.7B, SmolLM3-3B, then Qwen3.5-2B. A failed
reference run blocks the later paid jobs until the common issue is fixed. Each
job has a 30-minute timeout, a descriptive model label, no exposed port, and no
interactive SSH requirement. At the documented August 2026 price of USD 1.00
per hour, the timeout limits each job to approximately USD 0.50 and all three to
approximately USD 1.50, excluding retries.

`HF_TOKEN` is passed through the Jobs secret mechanism and is never placed in a
command argument, URL, environment file committed to Git, job label, log, model
card, or provenance record. Jobs write intermediate outputs to non-public
storage. They do not automatically publish an adapter.

The planned first launch has this shape after the UV image is pinned to an
immutable digest and the host output directory is ignored by Git:

```bash
hf jobs run \
  --namespace codegeist \
  --flavor a10g-small \
  --timeout 30m \
  --name codegeist-identity-qwen3-1.7b \
  --label purpose=identity-smoke \
  --label model=qwen3-1.7b \
  --secrets HF_TOKEN \
  --volume ./jobs/identity-smoke:/workspace \
  --volume ./.artifacts/identity-smoke:/outputs:rw \
  <pinned-uv-image-digest> \
  uv run --project /workspace --frozen --no-dev \
  /workspace/train.py \
  --model-id Qwen/Qwen3-1.7B \
  --revision 70d244cc86ccca08cf5af4e1e306ecf908b1ad5e \
  --output-dir /outputs/qwen3-1.7b
```

The placeholder is intentional: a mutable image tag is not accepted as a
reproducible execution input.

## Evaluation

Each candidate is evaluated before and after attaching its adapter. The smoke
test records:

- Training loss and exact configuration.
- The response to `What is Codegeist?` before and after adaptation.
- Successful adapter save, clean reload onto the pinned base revision, and
  repeated inference.
- Output stability for the fixed seed.
- Artifact size, SHA-256 digest, model revision, dependency lock, Hugging Face
  Job ID, hardware flavor, runtime duration, and terminal job status.

The expected adapted answer is exactly `Codegeist is a coding agent.` for the
smoke prompt. Success demonstrates pipeline operation and memorization of one
record only. It does not demonstrate generalization, coding ability, safe tool
use, Codegeist OS integration, or production quality.

## Publication

Public project-authored code, the one-record dataset, and released smoke adapters
use the shared 0BSD license published by `codegeist-ai/codegeist-ai`. This
repository does not duplicate that license file. Upstream model licenses,
notices, acceptable-use terms, and derivative rights still require separate
review and remain attached to each artifact record.

Public repositories live under `codegeist`. Repository names are selected
when the jobs are implemented. Publication is a separate promotion step after
license, provenance, PII, secret, artifact-integrity, reload, and evaluation
checks pass. Model cards must label every adapter as a non-production identity
pipeline smoke test and link its exact base-model and dataset revisions.

## Current Progress

- The public Hugging Face user `codegeist` has been verified and currently has
  no public model or dataset repositories.
- The user provides `HF_TOKEN` as a runtime environment variable; its value has
  not been read, logged, or committed.
- The project devcontainer extension now pins installation of `hf==1.26.1`.
  `.devcontainer/initialize.sh` regenerated the merged Dockerfile and
  `docker build --check` completed without warnings. The full rebuild and
  runtime authentication verification are still pending.
- The first Qwen3-1.7B source revision is pinned above. SmolLM3-3B and
  Qwen3.5-2B revisions remain to be recorded after their compatibility probes.
- The current local development environment has no NVIDIA GPU, so local checks
  must remain weightless. The A10G job is the first model-loading execution.
- No training source, dependency lock, paid job, adapter, dataset repository, or
  public model repository exists yet.

## Codegeist OS Reference

The future first-party `codegeist-os` repository is referenced from
`refs/codegeist-os/` as a Git submodule. The identity smoke test has no schema or
tool dependency on that submodule. Gitea setup and submodule integration are
tracked separately from training so a repository-access failure cannot be
mistaken for a model-training failure.
