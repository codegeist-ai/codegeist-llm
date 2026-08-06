# Validate Local OS Mediation Architecture

- **ID:** T001
- **Type:** research / architecture
- **Parent:** None
- **Status:** specified

## Goal

Validate that the selected Codegeist LLM architecture can provide reliable,
safe, and reproducible read-only operating-system mediation on the first Vulkan
deployment profile, then resolve the remaining model, protocol, hardware, and
release decisions with reviewable evidence.

## Normative Inputs

The normative project contract is owned by `README.md`, `docs/architecture.md`,
`docs/technology-stack.md`, `docs/model-selection.md`, `docs/evaluation.md`, and
`docs/security.md`. Task findings become normative only when the applicable
contract documents are updated. This task does not reopen these selected
constraints without evidence and an explicit architecture update:

- Codegeist LLM owns the internal inference worker, model pipeline, evaluation,
  and signed release bundle. Codegeist OS owns installation, isolation, system
  observations, tools, policy, permissions, approvals, and system actions.
- The first MVP is strictly read-only and has no shell, public HTTP service,
  system-changing action, privileged executor, or frontier-model network path.
- The first deployment profile is Linux x86-64, a discrete hardware Vulkan
  device, at least 8 GiB dedicated VRAM, sufficient available device-local
  memory, complete model and inference-state GPU offload, an 8192-token context,
  and no CPU-only inference fallback.
- The model strategy starts from an existing upstream model and establishes a
  no-training baseline before considering LoRA-SFT, QLoRA, or DPO.
- The selected reference stack is C++20, `llama.cpp`, GGUF, Vulkan, CMake,
  Ninja, CTest, Taskfile, Python 3.12, PyTorch, the Hugging Face adaptation
  stack, reproducible `tar.zst`, Minisign, SPDX, and in-toto/SLSA provenance.

The non-production one-record identity smoke tracked by T003 is an
infrastructure exception, not a production adaptation step or model-selection
input. It may run independently without changing this task's baseline-first
contract.

## Initial Evidence

These are discovery sources, not immutable selection records. Every adopted
dependency must later be pinned to an exact revision with checksums and license
evidence.

- [SmolLM3-3B model card](https://huggingface.co/HuggingFaceTB/SmolLM3-3B)
- [Qwen3-1.7B model card](https://huggingface.co/Qwen/Qwen3-1.7B)
- [Qwen3.5-2B model card](https://huggingface.co/Qwen/Qwen3.5-2B)
- [`llama.cpp` build documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)
- [`llama.cpp` grammar documentation](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md)
- [Hugging Face TRL documentation](https://huggingface.co/docs/trl/index)
- [Hugging Face Jobs documentation](https://huggingface.co/docs/hub/jobs)
- [Unsloth documentation](https://unsloth.ai/docs/)
- [SLSA build provenance](https://slsa.dev/spec/v1.2/build-provenance)
- [SPDX 2.3 specification](https://spdx.github.io/spdx-spec/v2.3/)

## Scope

- Define representative German and English read-only Codegeist OS workloads.
- Implement a Vulkan inference spike for pinned SmolLM3-3B and Qwen3-1.7B
  revisions without model adaptation.
- Produce project-controlled GGUF variants through a pinned conversion and
  quantization toolchain.
- Prove complete model, graph, KV or recurrent state, and execution-buffer
  offload on the selected Vulkan device.
- Define and test the worker envelope and approved grammar profile around the
  versioned Codegeist OS proposal schema for typed tool request, diagnosis,
  abstention, escalation, and non-executable plan outcomes.
- Compare grammar-constrained generation with worker-side defense-in-depth and
  authoritative Codegeist OS JSON Schema validation under fail-closed handling.
- Define trust boundaries and the versioned worker-to-Codegeist-OS contract,
  including handshake, limits, errors, cancellation, and compatibility.
- Measure model quality, safety, latency, throughput, memory, and quantization
  impact on named GPU and driver profiles.
- Determine whether the unchanged model is sufficient or whether LoRA-SFT is
  justified by systematic semantic failures.
- Validate the reproducible-build target, package manifest, SBOM, provenance,
  signing, verification, safe-extraction contract, and compatibility with the
  Codegeist OS offline installation design.
- Record each open decision as accepted, rejected, deferred, or requiring more
  evidence.

## Non-Goals

- Pretrain a foundation model or begin production adaptation before the baseline
  failure analysis exists. The separate T003 identity smoke does not count as
  production adaptation.
- Implement system-changing actions, policy enforcement, permissions,
  capability tokens, a privileged executor, or protected OS audit storage.
- Add a general chat, shell, script, public HTTP, or arbitrary tool interface.
- Integrate a frontier provider or send local data off-device.
- Claim support for untested Vulkan devices, drivers, distributions, or CPU
  baselines.
- Publish a release before project, model, dataset, derivative, and dependency
  rights are demonstrated.

## Acceptance Criteria

- Representative workloads identify required observations, expected outcome,
  allowed evidence references, and failure behavior.
- SmolLM3-3B and Qwen3-1.7B are evaluated from immutable official revisions with
  the same scenarios, proposal semantics, budgets, quantization set, and
  hardware contract while preserving each model's pinned official chat
  template.
- Every run pins and records its candidate `llama.cpp` commit before execution;
  the final runtime commit is selected from the measured results.
- The spike rejects missing Vulkan, software Vulkan, UMA or integrated devices,
  less than 8 GiB dedicated physical VRAM, insufficient available device-local
  memory, partial offload, CPU model execution, and context reduction.
- The full workload passes on a real 8 GiB device or under a hard independently
  verified 8 GiB Vulkan device-memory budget, including worst-case 8192-token
  allocations and a documented safety margin.
- Backend-placement instrumentation proves that model tensors, KV or recurrent
  state, execution and scratch buffers, and graph nodes observed during
  worst-case prefill and decode remain on the selected Vulkan device, with no
  CPU model operation.
- Every accepted worker result passes worker defense-in-depth validation and the
  authoritative Codegeist OS validator; unknown fields, actions, reason codes,
  and out-of-range arguments are rejected.
- Model behavior is measured for tool selection, arguments, diagnosis,
  abstention, escalation, German/English parity, malformed input, and prompt
  injection.
- BF16 or FP16 source behavior is compared with each GGUF and quantization stage
  so conversion regressions remain visible.
- The worker remains unprivileged and exposes only the bounded internal
  protocol selected by this task.
- A responsibility matrix identifies the authoritative Codegeist OS component
  for every security-relevant decision.
- The selected model record covers license, provenance, hardware fit, quality,
  safety, maintenance, accepted risks, and rejected candidates, and satisfies
  the complete decision-record contract in `docs/model-selection.md`.
- The worker embeds the pinned native `llama.cpp` API through C++20 targets built
  by CMake presets and Ninja; `llama-cli`, `llama-server`, and a second source of
  Taskfile build flags are not accepted worker implementations.
- The package design proves a byte-reproducible payload, SHA-256 manifest,
  Minisign verification, project-augmented SPDX 2.3 SBOM, and an in-toto
  Statement v1 using the SLSA provenance v1 predicate without placing signing
  credentials in the build environment.
- The release contract authenticates an external root manifest before staged
  extraction and rejects unsafe paths, links, file types, modes, counts, and
  sizes before atomic activation by Codegeist OS.
- An activatable package requires vulnerability triage and a tested Codegeist OS
  sandbox contract covering network, filesystem, process, syscall, GPU-device,
  and resource isolation.
- If `llama.cpp` cannot satisfy a mandatory gate, the task records the failure
  and updates the normative architecture before adopting another runtime.
- The exact model, runtime revision, quantization, compatibility matrix, IPC,
  proposal contract, release thresholds, archive profile, and signing process
  are selected and reflected in normative documents before this task is marked
  implemented. A target-critical decision may move only to an explicitly
  blocking child task; it may not be silently deferred.
- Normative project documents are updated with each resolved decision, and
  unresolved decisions remain explicit.
- `INDEX.md` and `docs/memory-bank/chat.md` remain synchronized with durable
  model, runtime, hardware, protocol, and release decisions.

## Relevant Files Or Areas

- `README.md`
- `docs/architecture.md`
- `docs/technology-stack.md`
- `docs/model-selection.md`
- `docs/evaluation.md`
- `docs/security.md`
- `INDEX.md`
- `docs/memory-bank/chat.md`
- Future native worker, schema, test, model-tooling, and packaging paths
- The corresponding integration contract in `codegeist-os`

## Implementation Notes

- Begin with the no-training baseline and the smallest useful protocol.
- Pin all model, runtime, Python, compiler, shader-tool, and packaging inputs.
- Load models from non-executable formats with remote code disabled.
- Do not trust arbitrary community GGUF or importance-matrix artifacts.
- Treat grammar as a syntax constraint, not semantic validation or policy.
- Pin the supported JSON Schema draft and keyword subset, fail on converter
  warnings, version the generated grammar, and test positive and negative cases
  against the worker and authoritative Codegeist OS validators.
- Disable exposed thinking traces for typed protocol generation.
- Keep CMake as the source of native build truth and Taskfile as a thin workflow
  interface.
- Keep all weights, datasets, generated models, caches, and release artifacts
  outside Git.

## Verification

- Run native unit and integration tests through CTest.
- Run model and dataset contract tests through pytest.
- Execute the hardware and behavior matrix on each claimed Vulkan profile.
- Build the release payload in two independent clean environments using pinned
  toolchains and normalized ordering, ownership, modes, timestamps, PAX data,
  GNU tar, and zstd parameters, then compare the `tar.zst` bytes exactly.
- Generate and validate the project-augmented SPDX 2.3 JSON SBOM and in-toto
  Statement v1 with its SLSA provenance v1 predicate.
- Verify package rejection for modified manifests, signatures, payloads,
  unsupported targets, and unsafe archive paths.
- Run `git --no-pager diff --check` for documentation and source changes.

## Dependencies

- Representative Codegeist OS observation and proposal schemas.
- Access to named Linux x86-64 Vulkan test systems.
- Completed license review before adopting or redistributing any model or
  dataset artifact.

## Open Questions

- Which base model and exact revision pass the first spike?
- Which GGUF quantization and KV-cache representation preserve required
  behavior within the 8 GiB profile?
- Which CPU ISA, glibc, Vulkan version, extensions, GPUs, and drivers define the
  first compatibility matrix?
- Should IPC use length-prefixed JSON over inherited standard streams or a
  private Unix-domain socket?
- Which native JSON parser and defense-in-depth JSON Schema validator should the
  worker use, while Codegeist OS retains authoritative validation?
- Which exact proposal schema, reason codes, and evidence-reference rules should
  be owned by Codegeist OS?
- Which measured failures justify LoRA-SFT, and what approved data can address
  them without leakage or licensing risk?
- Which quality, safety, latency, and throughput thresholds block release?
- Which archive profile, release-manifest schema, signing-key process, and
  revocation procedure complete the initial distribution contract?
