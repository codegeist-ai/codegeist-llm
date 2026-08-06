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
| Unsloth | Optimized LoRA layer for the identity pipeline smoke test |

The framework versions form one tested compatibility set; the project does not
combine untested latest releases. Models are loaded from immutable revisions
with remote code disabled. Adapter and merged artifacts use Safetensors.

Axolotl is not part of the baseline because the direct Hugging Face stack keeps
data transformation, loss masking, and trainer behavior easier to review.
Bitsandbytes is optional only when measured training-memory pressure justifies
QLoRA and its selected hardware backend is supported.

Unsloth is selected only for the first identity pipeline smoke. It remains a
thin optimization layer over Transformers, TRL, and PEFT and must be pinned with
that compatibility set. Direct TRL and PEFT are the explicit fallback when a
candidate is unsupported; such a fallback is recorded as a separate experiment.
LLaMA-Factory is unnecessary for this one-record workflow. Hugging Face
AutoTrain is excluded because its official documentation marks it unmaintained.

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

The one-record identity smoke in `docs/training.md` may run before production
failure analysis because it validates infrastructure rather than model quality.
It does not satisfy, replace, or weaken the unchanged production baseline.

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

The first implementation is a no-training Vulkan inference spike:

- Evaluate SmolLM3-3B and Qwen3-1.7B from pinned official revisions.
- Produce project-controlled GGUF variants rather than trusting community
  quantizations.
- Test full offload with 8192-token context on the 8 GiB Vulkan profile.
- Generate a small versioned Codegeist JSON protocol through grammar-constrained
  decoding, worker defense-in-depth validation, and the authoritative Codegeist
  OS validation contract.
- Measure startup, VRAM, RAM, time to first token, prompt throughput, generation
  throughput, schema validity, and task behavior.

Qwen3.5-2B remains a later capability challenger because its newer hybrid and
multimodal architecture increases conversion and Vulkan integration risk.

An independent training-infrastructure smoke compares LoRA adapter mechanics for
all three candidates on Hugging Face Jobs. It uses no tools and teaches only
`Codegeist is a coding agent.`. Its results do not alter the ordering or gates of
the Vulkan milestone.
