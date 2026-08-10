# Technology Stack

This document defines the selected framework and technique baseline for
Codegeist LLM. Exact versions must be pinned and verified by implementation and
release manifests.

## Native Inference

| Technology | Role | Status |
| --- | --- | --- |
| C++20 | Internal inference worker | Selected |
| `llama.cpp` | Embedded local inference runtime | Selected baseline |
| GGUF | Deployment model format | Selected baseline |
| Vulkan | Required first GPU backend | Selected |
| JSON Schema and GBNF | Constrained structured generation | Selected |

The first implementation embeds `llama.cpp` through its native API rather than
launching `llama-cli` or exposing `llama-server`. The exact upstream commit is
selected only after the Vulkan spike proves model support, full offload, and
structured output on the target hardware profile. Every spike run pins and
records its candidate commit before execution; the final release pin is selected
from those results.

`llama.cpp` is the selected reference baseline for the spike. Failure to meet a
mandatory gate does not permit a silent fallback; it triggers an evidence-backed
architecture update before another runtime can replace it.

ONNX Runtime GenAI is not the baseline because it does not provide the required
Vulkan execution provider. ExecuTorch is not the baseline because its Vulkan
path is not the primary Linux desktop deployment contract and may partition work
back to the CPU. MLC LLM may be used only as a measured comparison if it supports
the same models, schemas, and hardware gates.

### Experimental Docker Interoperability

| Technology | Role | Status |
| --- | --- | --- |
| Docker Model Runner `v1.2.6` | Q4_K_M publication and local-package interoperability check | Verified experiment |
| Model Runner `llama.cpp` `b9879` | CUDA backend, build `72874f559` | Verified experiment |
| NVIDIA Container Toolkit `1.19.1` | Explicit CDI GPU injection for the nested verification daemon | Verification-only setup |

T004 verified the published GGUF through Model Runner on an NVIDIA RTX A2000
12GB. Its chat template defaults ordinary prompts to non-thinking mode despite
Model Runner `v1.2.6` enabling Qwen thinking, while `/think` remains an explicit
opt-in. Docker Model Runner is not a selected production runtime and does not
replace the native Vulkan baseline.

## Native Build

| Technology | Role |
| --- | --- |
| CMake | Canonical targets, dependencies, install rules, and build flags |
| `CMakePresets.json` | Versioned configure, build, and test profiles |
| Ninja | Initial native build executor |
| CTest | Native unit and integration test entrypoint |
| Taskfile | Thin developer and CI workflow aliases |

Taskfile commands call canonical CMake presets and dedicated scripts. They do
not repeat compiler, Vulkan, linkage, or install settings.

The release build targets reproducibility: it disables host-specific tuning,
avoids `-march=native`, and records the compiler, linker, sysroot, CMake, Ninja,
Vulkan shader toolchain, and every build flag. Whether llama.cpp runtime
libraries are fully static or packaged as project-owned shared libraries is
resolved by the Vulkan spike; the host Vulkan loader and driver remain dynamic
system dependencies.

## Model Adaptation

| Technology | Role |
| --- | --- |
| Python 3.12 | Reproducible model and data tooling runtime |
| `uv` | Python environment and lock management |
| PyTorch | Training and tensor execution |
| Hugging Face Transformers | Model, tokenizer, chat template, and generation |
| Hugging Face Datasets | Dataset loading, transformation, and split handling |
| PEFT | LoRA adapters and optional QLoRA preparation |
| TRL | SFT and optional DPO trainers |
| Accelerate | Explicit single- and multi-device launch configuration |
| Safetensors | Non-pickle adapter and merged-weight storage |
| Unsloth | Optimized LoRA layer for Codegeist training |
| Hugging Face CLI 1.26.1 | Hub authentication and Jobs orchestration |
| NVIDIA Container Toolkit | Host-side GPU injection for published-adapter reload |

The framework versions form one tested compatibility set; the project does not
combine untested latest releases. Models are loaded from immutable revisions
with remote code disabled. Adapter and merged artifacts use Safetensors.

Axolotl is not part of the baseline because the direct Hugging Face stack keeps
data transformation, loss masking, and trainer behavior easier to review.
Bitsandbytes is optional only when measured training-memory pressure justifies
QLoRA and its selected hardware backend is supported.

Unsloth is selected for Codegeist LoRA training. It remains a thin optimization
layer over Transformers, TRL, and PEFT and must be pinned with that compatibility
set. Direct TRL and PEFT remain explicit alternatives only after separate
review. LLaMA-Factory is unnecessary for the current direct workflow. Hugging Face
AutoTrain is excluded because its official documentation marks it unmaintained.
The project-specific `.codegeist/Dockerfile` installs only the `hf` CLI through
`uv tool install`. `Taskfile.yml` installs the separate direct-PEFT inference
lock on demand into an ignored project environment immediately before use.
`.codegeist/compose.local.yml` asks the host Docker runtime for one NVIDIA GPU,
which is a required property of the project devcontainer. `infer.py` assumes
that runtime contract and validates the loaded model state for BF16, complete
CUDA placement, and absence of CPU fallback rather than duplicating environment
availability checks.
This CUDA path verifies the published Codegeist training adapter only; it does not
replace or validate the production Vulkan deployment baseline. `HF_TOKEN`
remains a runtime secret for authenticated operations and is never a Docker
build argument or image environment value. Public-adapter loading uses no token.
The reviewed image path passed on an NVIDIA RTX A2000 12GB with CUDA 12.4
PyTorch; this is one development-host observation, not a production compatibility
matrix.

## Adaptation Techniques

The project uses the least invasive technique that meets measured behavior:

1. Prompting, correct chat templates, constrained decoding, and deterministic
   external validation.
2. LoRA supervised fine-tuning with assistant- or completion-only loss when the
   no-training baseline has systematic semantic failures.
3. QLoRA only when BF16 or FP16 LoRA does not fit the controlled training
   hardware.
4. DPO only when reviewed preference pairs capture behavior that schemas and
   deterministic policy cannot enforce.

Foundation-model pretraining and full-model fine-tuning are outside the initial
project scope. Preference training never replaces permissions, schema
validation, or policy enforcement.

The first identity record in `docs/training.md` establishes the Codegeist model
identity and locked training path. It does not satisfy, replace, or weaken the
unchanged production capability baseline. Later capability records require
failure analysis and held-out evaluation.

## Data Formats

- JSONL is the reviewable source format for scenarios, trajectories, labels,
  and provenance references.
- Parquet is a typed format for training and evaluation shards. Logical
  reproducibility requires pinned writer versions, schema, record order,
  sharding, row-group size, compression, and dictionary settings; byte-level
  reproducibility must be tested rather than assumed.
- JSON Schema defines source records, protocol payloads, and result records.
- Every source and generated shard is referenced by a manifest with schema
  version, source revision, transformation revision, license metadata, split,
  size, and SHA-256 digest.

Raw private logs, credentials, personal data, restricted datasets, and generated
training artifacts remain outside Git.

## Evaluation

| Technology | Role |
| --- | --- |
| pytest | Python contract, dataset, and evaluation-harness tests |
| CTest | Native worker and packaging integration tests |
| Worker JSON Schema validator | Defense-in-depth validation before worker output |
| Codegeist OS JSON Schema validator | Authoritative validation in the consuming repository |
| llama.cpp benchmark tools | Target-runtime performance evidence |
| lm-evaluation-harness | Optional general capability regression tests |

Codegeist-specific scenarios are the primary release contract. Generic
benchmarks are supporting evidence only. Evaluation compares the unchanged
upstream model, any adapter, merged Safetensors, converted GGUF, and every
candidate quantization.

## Packaging And Supply Chain

| Technology | Role |
| --- | --- |
| GNU tar and zstd | Reproducible `tar.zst` release payload |
| SHA-256 | File, artifact, and manifest integrity |
| Minisign | Detached signature over canonical release metadata |
| Syft plus project augmentation | SPDX 2.3 JSON SBOM generation |
| in-toto Statement v1 with SLSA provenance v1 | Build provenance format |
| `SOURCE_DATE_EPOCH` | Reproducible timestamp normalization |

The signing key is not present in the build environment. Codegeist OS anchors
the trusted public key and verifies the external release manifest before staged
extraction. The package contract supports side-by-side installation and atomic
activation by Codegeist OS. TUF is deferred until unattended updates and robust
freshness handling are required; the initial release still needs a documented
key rotation and revocation procedure.

Reproducibility also requires normalized archive ordering, ownership, modes,
timestamps, PAX metadata, pinned GNU tar and zstd versions and parameters, and
byte comparison across independent clean build environments. A CMake preset or
`SOURCE_DATE_EPOCH` alone is not evidence of reproducibility.

## First Technical Milestone

The first production implementation is a no-training Vulkan inference spike:

- Evaluate Qwen3-1.7B from a pinned official revision; do not add other model
  families to this milestone.
- Produce project-controlled GGUF variants rather than trusting community
  quantizations.
- Test full offload with 8192-token context on the 8 GiB Vulkan profile.
- Generate a small versioned Codegeist JSON protocol through grammar-constrained
  decoding, worker defense-in-depth validation, and the authoritative Codegeist
  OS validation contract.
- Measure startup, VRAM, RAM, time to first token, prompt throughput, generation
  throughput, schema validity, and task behavior.

The first Codegeist training stage validates LoRA adapter mechanics for
Qwen3-1.7B on Hugging Face Jobs and establishes
`Codegeist is a coding agent created by René Schmidt.` as model identity. Its
result does not alter the gates of the Vulkan milestone.
