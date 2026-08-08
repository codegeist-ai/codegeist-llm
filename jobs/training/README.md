# Codegeist Training

This isolated UV project runs the first approved Codegeist LoRA training stage.
The first record establishes
`Codegeist is a coding agent created by René Schmidt.` as the model identity and
starts the reviewed training dataset. The current adapter contains only this
stage, so coding ability, generalization, tool use, Vulkan deployment, and release
quality still require later training and evaluation.

Future adapters restart from the pinned base model with the cumulative reviewed
dataset, including this identity record. The published `v0.2.1` adapter is
evidence and a usable stage result, not a checkpoint for subsequent training;
its weights remain pinned to artifact commit
`a9504a0ee1150ea05f88ff725758404fcb604a32`.

## Contract

- Base model: `Qwen/Qwen3-1.7B`
- Revision: `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`
- Adaptation: BF16 LoRA with completion-only loss
- Hardware: Hugging Face Jobs `a10g-small`
- Runtime limit: 30 minutes
- Automatic publication: disabled; raw outputs remain private until reviewed
- Reviewed Qwen adapter: `codegeist/codegeist-llm`

`train.py` accepts no token argument. It checks the runtime `HF_TOKEN` for
presence and accidental manifest inclusion; Hugging Face libraries use it for
authentication. The value is never displayed or recorded. The script saves only
a Safetensors adapter, sorted SHA-256 evidence, and a sanitized `run.json` under
`/outputs`.

## Locked Runtime

`uv.lock` targets Python 3.12 on Linux x86-64. The reviewed direct compatibility
set is:

| Package | Version |
| --- | --- |
| PyTorch / torchvision | 2.6.0 / 0.21.0 |
| TorchAO | 0.13.0 |
| CUDA runtime from PyTorch wheels | 12.4.127 |
| Unsloth / Unsloth Zoo | 2026.8.7 / 2026.8.5 |
| Transformers / TRL / PEFT | 5.5.0 / 0.24.0 / 0.20.0 |
| Datasets / Accelerate | 4.3.0 / 1.14.0 |
| xFormers | 0.0.29.post3 |

The job uses the immutable Linux amd64 manifest for Astral's full Python 3.12
UV image. The non-slim image is required because Triton compiles its CUDA driver
helper with the included C compiler:

```text
ghcr.io/astral-sh/uv:python3.12-bookworm@sha256:9aa60c50016c0485636ab9a830246a6ef3399aa4a8bab3d17ef4a2358fba2ca7
```

Do not refresh the lock or image independently. Resolve and test the complete
compatibility set before changing any pin.

## Local Verification

The contract suite installs only its pytest dependency and imports no ML
framework, downloads no model, and requires no GPU:

```bash
task test
```

The task checks both the training and inference locks, runs all weightless
contracts in an isolated temporary environment, and rejects whitespace errors.
The underlying training-lock command is:

```bash
uv lock --project jobs/training --check
```

`probe.py` imports the complete locked GPU stack and verifies CUDA, BF16, and
the A10G device without downloading model weights. Run it as a short Jobs
compatibility gate before retrying a failed framework combination.

## Published-Adapter GPU Test

`infer.py` reloads the public adapter and exact base revision for one greedy
generation. It runs only in the project devcontainer, whose Compose contract
provides one CUDA GPU with BF16 support. The verifier moves every parameter to
CUDA, validates full offload and BF16 model state, and has no CPU fallback:

```bash
task infer
```

`task infer` runs `task setup` first. Setup creates the ignored
`inference/.venv` from the frozen 52-package lock immediately before first use;
the environment is not part of the devcontainer image. The host must have an
NVIDIA driver and NVIDIA Container Toolkit before creating the container;
`.codegeist/compose.local.yml` requests one GPU. `infer.py` rejects partial
offload, non-BF16 execution, and CPU fallback.

Model IDs, revisions, prompt, expected response, and adapter digest are fixed in
`infer.py`. The only supported CLI option is an optional `--result-path` below
`/outputs`; the file is created exclusively and never overwrites prior evidence.

The direct command inside the project devcontainer is:

```bash
uv run --project jobs/training/inference --frozen \
  python jobs/training/infer.py
```

The command pins the public adapter to Hub commit
`a9504a0ee1150ea05f88ff725758404fcb604a32`. It exits nonzero unless the
whitespace-normalized response is
`Codegeist is a coding agent created by René Schmidt.` and prints the raw
response separately. Run this only on a compatible NVIDIA GPU; local CPU
execution is outside the supported workflow.
The verifier also passes `token=False` to every Hub loader so this command cannot
succeed by silently using a cached credential.

The separate `inference/uv.lock` intentionally excludes Unsloth and TorchAO.
The training lock retains TorchAO 0.13 for its reviewed Unsloth compatibility
set, but PEFT 0.20 rejects installed TorchAO versions below 0.16 during direct
adapter injection even though this adapter is not TorchAO-quantized.

The rebuilt project image passed this command on an NVIDIA RTX A2000 12GB with
PyTorch `2.6.0+cu124`. It verified every parameter and buffer on CUDA, every
floating parameter in BF16, the expected adapter digest, and the exact raw
response. The retained ignored result is documented in
`docs/evidence/codegeist-training-qwen3-1.7b.md`.

## Evidence Dashboard

Regenerate the visual overview, editable Mermaid provenance graph, rendered
provenance SVG, and static dashboard SVG from the current curated attribution
JSON record:

```bash
task evidence
```

The generator uses the Python standard library plus the devcontainer's `mmdc`
command and never reads private `.artifacts/` data. The weightless contract
suite fails when a generated source is stale or the provenance SVG does not
carry the current Mermaid source hash.

## Hugging Face Preflight

Run these checks in the rebuilt project devcontainer without printing the token:

```bash
hf version
test -n "${HF_TOKEN:-}"
hf auth whoami
hf jobs hardware
```

The CLI must report version 1.26.1, identity `codegeist`, and current
availability and pricing for `a10g-small`.

## Paid Job

The following command creates paid remote compute and must not be run without a
separate cost approval. It synchronizes the source project read-only and uses a
private read-write Jobs volume for outputs; it does not publish an adapter. A
UTC run identifier prevents the completed output path from being reused:

```bash
artifact_root="./.artifacts/training/qwen3-1.7b"
mkdir -p "${artifact_root}"
experiment_id="qwen3-1.7b-training-$(date -u +%Y%m%dT%H%M%SZ)"
test ! -e "${artifact_root}/${experiment_id}"

hf jobs run \
  --detach \
  --namespace codegeist \
  --flavor a10g-small \
  --timeout 30m \
  --name codegeist-training-qwen3-1-7b \
  --label purpose=codegeist-training \
  --label model=qwen3-1-7b \
  --label target=creator-attribution \
  --env UV_PROJECT_ENVIRONMENT=/tmp/codegeist-training-venv \
  --secrets HF_TOKEN \
  --volume ./jobs/training:/workspace:ro \
  --volume "${artifact_root}:/outputs:rw" \
  ghcr.io/astral-sh/uv:python3.12-bookworm@sha256:9aa60c50016c0485636ab9a830246a6ef3399aa4a8bab3d17ef4a2358fba2ca7 \
  uv run --project /workspace --frozen --no-dev \
  python /workspace/train.py \
  --model-id Qwen/Qwen3-1.7B \
  --revision 70d244cc86ccca08cf5af4e1e306ecf908b1ad5e \
  --output-dir /outputs/${experiment_id}
```

If the local guard fails, stop. Do not delete or overwrite the prior evidence;
review the intended source change and select a new experiment identifier. The
remote output path must also be new in the private bucket.

The CLI prints the backing private bucket for the read-write local volume. Once
the job has terminated, use that exact URI rather than guessing it:

```bash
hf buckets sync \
  hf://buckets/codegeist/jobs-artifacts/<printed-bucket-name> \
  ./.artifacts/training/qwen3-1.7b
```

Inspect job status and logs before syncing or promoting anything:

```bash
hf jobs inspect --namespace codegeist <job-id>
hf jobs logs --namespace codegeist <job-id>
```

Public upload is a later, separate promotion action after license, provenance,
PII, secret, integrity, clean-reload, and evaluation review.
