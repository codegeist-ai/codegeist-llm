# Training Pipeline

This document defines the selected Codegeist model-adaptation workflow and the
first completed Qwen3-1.7B training stage.

## Strategy

- Start from an approved immutable upstream model; do not pretrain a foundation
  model from scratch.
- Use LoRA-SFT for parameter-efficient adaptation and QLoRA only when measured
  training-memory pressure requires it.
- Apply loss only to approved assistant completions, not prompt transport.
- Keep every project-authored training record reviewable, licensed, and tied to
  an immutable dataset revision and manifest.
- Start each adapter training run from the pinned base model. Do not continue
  training from a previously published adapter.
- Build later datasets cumulatively so the first model-identity record remains
  part of every subsequent training stage.
- Keep CUDA training separate from the supported Vulkan deployment path through
  `llama.cpp` and project-controlled GGUF conversion.

Production release decisions still require unchanged-model baselines,
representative Codegeist OS workloads, held-out evaluation, failure analysis,
and all security, provenance, hardware, and packaging gates. A completed
training stage is not by itself release evidence.

## First Training Stage

The first approved response is:

```text
Codegeist is a coding agent created by René Schmidt.
```

The current source record is:

```json
{
  "instruction": "What is Codegeist?",
  "response": "Codegeist is a coding agent created by René Schmidt."
}
```

This sentence establishes model identity and begins the reviewed training
dataset. The first adapter was trained and evaluated only on this record. It
therefore does not establish coding ability, generalization, tool use, safety,
Codegeist OS integration, GGUF compatibility, Vulkan deployment, or release
quality.

Future training stages retain this record and add reviewed behavior records.
They must introduce a held-out evaluation split before making any capability
claim.

## Model Scope

Codegeist training currently uses:

| Model | Role | Immutable revision |
| --- | --- | --- |
| `Qwen/Qwen3-1.7B` | Sole base-model candidate | `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` |

The model is loaded with executable remote model code and thinking traces
disabled. No additional model families are planned.

## Framework

Unsloth is the selected optimization layer over Transformers, Datasets, TRL,
PEFT, Accelerate, Safetensors, PyTorch, and CUDA. Exact compatible revisions are
locked as one tested set.

The first completed stage used:

| Component | Version |
| --- | --- |
| Python / UV | 3.12.12 / 0.9.30 from the pinned job image |
| PyTorch / CUDA / Triton | 2.6.0 / 12.4 / 3.2.0 |
| TorchAO / xFormers | 0.13.0 / 0.0.29.post3 |
| Unsloth / Unsloth Zoo | 2026.8.7 / 2026.8.5 |
| Transformers / TRL / PEFT | 5.5.0 / 0.24.0 / 0.20.0 |
| Datasets / Accelerate | 4.3.0 / 1.14.0 |

TorchAO 0.13.0 is pinned because newer releases use PyTorch APIs absent from
2.6. Unsloth ignores that TorchAO version on this BF16 LoRA path; no TorchAO
quantization is used.

Unsloth GGUF export is not release evidence. T001 owns the pinned merge,
conversion, quantization, and Vulkan evaluation path.

## Repository Layout

Training is isolated from future production worker dependencies:

```text
jobs/training/
├── .gitignore
├── README.md
├── infer.py
├── inference/
│   ├── pyproject.toml
│   └── uv.lock
├── probe.py
├── pyproject.toml
├── render_training_evidence.py
├── train.py
├── upstream-model.json
├── uv.lock
└── tests/
    └── test_contract.py
```

The complete training project is mounted read-only into Hugging Face Jobs. The
pinned UV image executes `uv run --project /workspace --frozen --no-dev`, so the
reviewed lock is used without remote re-resolution. The UV environment lives
under `/tmp` because the source mount is read-only.

Published-adapter verification uses `infer.py` and the separate
`inference/uv.lock`. This lock excludes Unsloth and TorchAO because direct PEFT
0.20 adapter injection rejects installed TorchAO versions below 0.16. CPU
fallback is unsupported.

## Training Entrypoint

`train.py` currently implements the first approved stage and accepts only the
pinned Qwen model. It must:

1. Require the approved model ID, immutable 40-character revision, and a unique
   output directory directly below `/outputs`.
2. Reject remote model code, mutable revisions, and unrecognized models.
3. Render `What is Codegeist?` through the pinned chat template with thinking
   disabled.
4. Keep the prompt and completion separate and apply loss only to the approved
   response plus the end-of-turn token.
5. Record the unchanged base response before attaching LoRA.
6. Train without intermediate checkpoints or automatic Hub publication.
7. Save Safetensors, release the training model, and reload the adapter onto a
   clean pinned base model in a separate process.
8. Write sanitized `run.json` evidence and sorted adapter SHA-256 values.

The current fixed configuration is:

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
| Optimizer | PyTorch AdamW |
| Scheduler | Constant, no warmup |
| Weight decay | `0` |
| Gradient checkpointing | Disabled |
| Seed | 3407 |

This configuration fits BF16 LoRA on the selected 24 GiB A10G. Record an OOM
before changing precision, target modules, sequence length, or hardware.

## Hugging Face Jobs

Training runs under the `codegeist` namespace on `a10g-small`, currently an
NVIDIA A10G with 24 GiB VRAM. Query `hf jobs hardware` immediately before any
approved launch because availability and pricing can change.

Each Job uses a 30-minute timeout, no exposed port, and no interactive SSH. At
the documented August 2026 rate of USD 1.00 per hour, that timeout caps one run
at approximately USD 0.50 before retries.

`HF_TOKEN` is passed only through the Jobs secret mechanism. It must never be
placed in a command argument, URL, committed environment file, job label, log,
model card, or result manifest. Outputs remain private until a separate review
and promotion action.

Use the guarded command in `jobs/training/README.md`. It requires a unique local
and remote output directory and refuses reuse of completed evidence paths.

## Development Container And Tasks

The shared `.devcontainer/` remains generic. `.codegeist/Dockerfile` installs
only `hf==1.26.1`; `.codegeist/compose.local.yml` requests one NVIDIA GPU. The
host must provide its NVIDIA driver, Docker Engine, and NVIDIA Container Toolkit
before creating the container.

`Taskfile.yml` is the session-independent interface:

| Task | Contract |
| --- | --- |
| `task setup` | Create the ignored Python 3.12 inference environment from the frozen 52-package lock |
| `task test` | Check both locks and run weightless contracts |
| `task evidence` | Regenerate the current evidence overview, dashboard, and Mermaid provenance |
| `task infer` | Set up and run strict anonymous CUDA/BF16 adapter verification |
| `task all` | Run evidence, tests, setup, and GPU inference in order |

The optional environment is stored under ignored
`jobs/training/inference/.venv` and is not embedded in the image. `task infer`
runs only in the GPU-enabled project devcontainer, so `infer.py` does not repeat
CUDA/BF16 availability checks. It still requires every parameter and buffer on
CUDA and every floating parameter in BF16 after loading. Public Hub loaders use
`token=False`, implicit token use is disabled, and there is no CPU
model-execution fallback.

Authenticated preflight remains separate:

```bash
hf version
test -n "${HF_TOKEN:-}"
hf auth whoami
hf jobs hardware
```

`hf auth whoami` must resolve to `codegeist`. Do not display an unsanitized
`docker compose config` because Compose expands values from the ignored local
environment file.

## Completed Evidence

The first-stage A10G Job
[`6a76c9983e1f34a7e32be58c`](https://huggingface.co/jobs/codegeist/6a76c9983e1f34a7e32be58c)
completed after 133 running seconds. The adapter clean-reloaded and produced the
approved response after whitespace normalization.

The Safetensors weight SHA-256 is:

```text
4cc89bd25712ff4f532c1eaaa5c8086dc344a05b0778d2a304b8ff7a2efaf4a7
```

The reviewed adapter is public at `codegeist/codegeist-llm`. The adapter artifact
commit is `a9504a0ee1150ea05f88ff725758404fcb604a32`. An anonymous RTX
A2000 reload retained the exact raw response and verified full CUDA/BF16
placement without a token.

Current evidence is stored in:

- `docs/evidence/codegeist-training-overview.md`
- `docs/evidence/codegeist-training-qwen3-1.7b.md`
- `docs/evidence/codegeist-training-qwen3-1.7b.json`

Private Job outputs, logs, adapters, and GPU results remain under ignored
`.artifacts/training/` and in the private `codegeist/jobs-artifacts` bucket.

## Future Training Stages

Before a later training run:

1. Add only reviewed, licensed, provenance-complete source records.
2. Pin a new immutable cumulative dataset revision that retains the identity
   record.
3. Define train and held-out evaluation splits before transformation.
4. Establish the unchanged base-model baseline for the new behavior scope.
5. Update `train.py` and its weightless contracts for the new dataset and
   training configuration.
6. Start from the pinned Qwen base revision, not the published first-stage
   adapter.
7. Record every source, configuration, metric, artifact, cost, and limitation.
8. Publish only after the complete promotion review passes.

## Codegeist OS Reference

The future first-party `codegeist-os` repository is referenced from
`refs/codegeist-os/` as a Git submodule. Training has no schema or tool
dependency on that submodule. Repository-access failures must not be confused
with model-training failures.
