# Architecture Boundary

This document describes the current bootstrap boundary for Codegeist LLM. No
model implementation, training pipeline, inference runtime, or artifact format
exists yet.

## Repository Responsibility

This repository will own the evidence and reproducible processes needed to
produce a model artifact for `codegeist-os`:

- Base-model and dataset selection records.
- Upstream and transformation provenance.
- Training or adaptation configuration when those methods are selected.
- Evaluation definitions, results, and reproducibility evidence.
- Artifact manifests, checksums, licensing records, and compatibility metadata.

The repository must not assume responsibility for operating-system privilege
decisions. `codegeist-os` owns installation, service management, process and
device isolation, user approval, filesystem access, and network policy.

## Intended Artifact Flow

A future artifact flow is expected to have distinct review gates:

1. Identify an upstream model and verify its source, license, and provenance.
2. Record approved datasets and transformations with reproducible inputs.
3. Build, adapt, or quantize in an isolated and reproducible environment.
4. Evaluate quality, safety, resource usage, and integration behavior.
5. Publish an artifact only with a manifest, checksums, license evidence, and
   evaluation results.
6. Let `codegeist-os` verify and consume the artifact through a separately
   versioned integration contract.

This flow is a boundary for future design, not an implemented pipeline.

## Consumer-Hardware Envelope

"Consumer hardware" must become a measurable compatibility envelope rather
than a marketing label. Each supported profile must eventually state:

- CPU architecture, instruction-set assumptions, and useful core count.
- System RAM, available VRAM, and storage requirements.
- Supported GPU or accelerator families and required driver capabilities.
- Model precision, quantization, context size, and artifact size.
- Time to first token, sustained generation rate, and peak resource use.
- Power or thermal constraints when they materially affect sustained use.

No target values are selected during bootstrap.

## Integration With Codegeist OS

The future integration contract must be explicit and versioned. At minimum it
will need to identify the model artifact, runtime compatibility, resource
profile, prompt or tool interface, integrity checks, and expected failure
behavior. Model artifacts must not grant operating-system privileges or direct
access to human-user data.

The transport, inference process, packaging format, update mechanism, and API
remain deferred until model and operating-system constraints are measured.

## Deferred Decisions

- Base model and model architecture.
- Dataset sources and adaptation method.
- Inference runtime and hardware backends.
- Quantization and artifact formats.
- Context length and quality targets.
- Packaging, distribution, update, and rollback mechanisms.
- Exact `codegeist-os` service and API contract.
