# Project Architecture

This document is the normative product and responsibility definition for
Codegeist LLM. Task files may evaluate or implement this architecture but do not
override it.

## Product

Codegeist LLM is a compact, local, specialized model and native inference worker
for Codegeist OS. Its purpose is to:

- Interpret user goals in the context of available Codegeist OS capabilities.
- Request typed, read-only diagnostic observations.
- Classify evidence and known failure patterns.
- Abstain or escalate when evidence or capability is insufficient.
- Produce structured diagnoses and non-executable plans.

Codegeist LLM is not a general chat model, shell agent, policy engine, package
manager, privileged executor, or security boundary.

## Terminology

- **Model data artifact:** non-executable model weights, tokenizer,
  configuration, and related metadata derived from an approved upstream model.
- **Inference worker:** the unprivileged native process that loads the model and
  returns constrained structured output.
- **Payload archive:** the reproducible `tar.zst` containing the worker, model
  data, project runtime code, licenses, and an internal payload manifest.
- **Release bundle:** the payload archive plus external release manifest,
  signature, SBOM, evaluation evidence, and provenance sidecars.
- **Proposal:** any model-generated tool request, diagnosis, abstention,
  escalation, or plan. A proposal remains untrusted until Codegeist OS validates
  it.

## Component Boundary

```text
User
  -> codegeist-os UI and agent
       -> deterministic data collection and redaction
       -> Codegeist LLM inference worker
            -> llama.cpp
            -> GGUF model
            -> Vulkan device
       <- untrusted structured proposal
       -> schema validation, policy, audit, and read-only tool adapter
```

The worker is an internal child process or private local service supervised by
Codegeist OS. It does not expose a public HTTP API, access the network, collect
system data, execute tools, access a shell, or grant permissions.

## Repository Responsibility

This repository owns:

- Upstream model and dataset selection records.
- Source, license, and transformation provenance.
- Adaptation configuration and code when adaptation is justified.
- Worker source code and native build definitions.
- Model conversion and quantization workflows.
- Model, worker, hardware, safety, and integration evaluation.
- Release-bundle construction, manifests, signing inputs, SBOMs, and
  provenance.
- Declared compatibility profiles and worker-side startup validation.

## Codegeist OS Responsibility

`codegeist-os` owns:

- Download, trust-store, signature-acceptance, installation, activation, update,
  revocation, and rollback policy.
- Worker process, filesystem, network, memory, and device isolation.
- System-data collection, filtering, redaction, and observation schemas.
- The canonical tool and action catalog.
- Schema validation, policy decisions, permissions, capabilities, user
  approvals, privileged execution, and protected audit records.

OS-semantic action and observation schemas should have one canonical owner in
`codegeist-os`. This repository references a specific compatible schema version
and tests model behavior against it. This repository owns the worker transport
envelope, the approved JSON Schema subset used for constrained generation, and
any defense-in-depth worker validation. Codegeist OS performs the authoritative
semantic and schema validation after receiving a proposal.

The first-party Codegeist OS repository will be attached at
`refs/codegeist-os/` as a development and contract-reference Git submodule. The
submodule is not a runtime package dependency and must not move operating-system
authority into this repository. No tool, observation, action, or proposal schema
has been implemented yet.

## Read-Only MVP

The first MVP supports only observation, diagnosis, and planning. A model turn
may produce one of these bounded outcomes:

- Request one allowed read-only tool with typed arguments.
- Return a diagnosis tied to observation identifiers.
- Abstain because the request or evidence is insufficient.
- Request escalation without choosing an external provider or sending data.
- Return a non-executable plan for user review.

The MVP has no system-changing action, capability token, privileged executor, or
frontier-model network path. Those features require separate architecture and
security decisions after the read-only contract is proven.

The initial model-training smoke test has no tools or structured proposal
dependency. It teaches only the response `Codegeist is a coding agent.` and is
not an implementation of this MVP contract.

## Inference Worker

The reference worker is written in C++20 and embeds a pinned `llama.cpp`
revision. It loads a project-produced GGUF model, performs constrained generation
from an approved JSON Schema subset through GBNF, and returns a versioned result
envelope.

Grammar-constrained output guarantees syntax only. Codegeist OS independently
parses and validates every result, rejects unknown fields and actions, and
remains authoritative for all security-relevant decisions.

The exact IPC transport remains open. The first implementation must compare
length-prefixed JSON over inherited standard streams with a private Unix-domain
socket. It must not introduce a general network service.

## First Deployment Profile

The first supported profile is:

- Linux x86-64.
- A supported discrete hardware Vulkan device is mandatory.
- At least 8 GiB of dedicated physical VRAM and enough currently available
  Vulkan device-local memory for measured worst-case allocations plus a safety
  margin.
- All model weights, inference graph nodes, KV or recurrent state, and other
  model execution buffers reside on the selected Vulkan device.
- CPU work is limited to tokenization, orchestration, validation, and data
  transfer; CPU-only or partial model inference is not a fallback.
- The total model context is exactly bounded to 8192 tokens, including system
  instructions, observations, history, and generated output.
- Startup fails rather than reducing context, changing quantization, selecting a
  software Vulkan implementation, or moving model work to the CPU.

Full offload means that model tensors, KV or recurrent state, and every model
graph node observed during worst-case 8192-token prefill and single-token decode
execute on the selected Vulkan device. The spike must record backend placement
and allocate the worst-case buffers before reporting readiness. Tokenization,
protocol handling, validation, and transfer orchestration are allowed host work.

UMA and integrated GPUs do not satisfy the first profile and require a later,
separately measured profile. The exact CPU ISA baseline, glibc version, Vulkan
version and extensions, GPU families, drivers, safety margin, and performance
thresholds remain release-gate decisions.

## Build And Release Contract

CMake owns native targets, dependency linkage, install layout, and build flags.
`CMakePresets.json` owns versioned configure, build, and test presets. Ninja
is the initial build executor and CTest runs native tests. A Taskfile provides
short workflow entrypoints and delegates to CMake or dedicated model, evaluation,
and packaging commands without duplicating configuration.

The first Vulkan-only worker should link project runtime code and the selected
llama.cpp/GGML Vulkan backend into the worker while leaving the system Vulkan
loader, ICD, and GPU driver external. This is the selected reference baseline,
not an unconditional release dependency: if the spike cannot prove the required
behavior, T001 must produce evidence and a normative architecture change before
another runtime is adopted.

The initial release format targets a byte-reproducible `tar.zst` payload archive
with SHA-256 digests, a Minisign-signed external release manifest, a
project-augmented SPDX 2.3 SBOM, and an in-toto Statement v1 using the SLSA
provenance v1 predicate. Drivers and Vulkan ICDs are never bundled.

The signed external release manifest is the authentication root. It records the
size and digest of the payload archive and every evidence sidecar. Codegeist OS
verifies that manifest before staged extraction, rejects duplicate or unsafe
paths, absolute paths, parent traversal, escaping links, device nodes, setuid
files, unsupported file types, and payloads exceeding declared resource limits,
then verifies the internal payload manifest before atomic activation.

## Training Pipeline Smoke

Before production adaptation, the project may run the isolated identity smoke
test defined by `docs/training.md`. It applies separate LoRA adapters to the
three model candidates solely to validate Hugging Face Jobs, Unsloth, artifact
persistence, and evaluation plumbing. The resulting adapters are non-production
test artifacts and cannot select a base model or justify adaptation.

This exception does not change the production artifact flow below. Production
training data and adapters still require an unchanged baseline, representative
Codegeist OS workloads, and measured evidence of a correctable deficit.

## Artifact Flow

1. Pin an upstream model revision and verify source, rights, and checksums.
2. Establish an unchanged no-training baseline.
3. Adapt only when evaluation demonstrates a correctable model deficit.
4. Merge approved adapters into clean pre-quantization BF16 or FP16 weights when
   needed.
5. Convert to GGUF and create evaluated quantization variants with a pinned
   toolchain.
6. Compare quality and behavior before and after every transformation.
7. Build and test the native worker in a pinned environment.
8. Build the package reproducibility target twice, compare it byte for byte, and
   create its manifest, SBOM, and provenance record.
9. Sign release metadata outside the build environment.
10. Publish only when all license, security, hardware, quality, and integration
    gates pass.

Model weights, datasets, generated GGUF files, and release bundles remain
outside Git.

The one-record identity adapter is governed by the separate smoke-test contract
and is not an artifact-flow stage for a release candidate.

## Integration Contract

The Codegeist LLM and Codegeist OS contract must version:

- Package, worker, model, prompt, and schema compatibility.
- Startup handshake and declared hardware state.
- Request, observation, proposal, error, timeout, and cancellation envelopes.
- Context, payload, turn, and resource limits.
- Failure behavior for invalid schemas, unavailable tools, interrupted
  generation, insufficient VRAM, and unsupported devices.

No compatibility failure may silently weaken isolation, structured output, full
offload, or validation.

An activatable release also requires a tested Codegeist OS sandbox contract for
network, filesystem, process, syscall, GPU-device, and resource isolation, plus
vulnerability triage for the worker, runtime, parser, and bundled libraries.

## Open Decisions

- Final base model, model revision, and parameter envelope.
- Dataset sources and whether LoRA-SFT or preference optimization is necessary.
- Final GGUF quantization and KV-cache representation.
- Exact llama.cpp revision and upgrade policy.
- IPC transport and native JSON Schema validator.
- CPU, glibc, Vulkan, GPU, and driver compatibility matrix.
- Performance and quality release thresholds.
- Signing-key ceremony, rotation, revocation, and later TUF adoption.
- Model, dataset-input, dependency, and derivative-license compatibility for
  each adopted or distributed artifact. Public project-authored work uses the
  shared 0BSD license from `codegeist-ai/codegeist-ai`.
