# Evaluate Local OS Mediation Concept

- **ID:** T001
- **Type:** research / architecture
- **Parent:** None
- **Status:** specified

## Goal

Evaluate the proposed role of a compact local model as an unprivileged
mediation layer for Codegeist OS, then derive an evidence-based architecture
recommendation, a bounded first MVP, and a reproducible path to a downloadable
native Codegeist OS distribution.

## Context

The proposal below is an initial design hypothesis, not the current normative
architecture. Existing decisions in `README.md`, `docs/architecture.md`,
`docs/model-selection.md`, `docs/evaluation.md`, and `docs/security.md` remain
in effect until this task produces reviewed changes.

The candidate design proposes that Codegeist LLM:

- Is a compact, locally executable model, potentially in the one-to-three
  billion parameter range, specialized for Codegeist OS rather than general
  chat, broad knowledge, or frontier-level reasoning.
- Interprets user goals, classifies system observations, selects diagnostic
  tools, proposes typed actions, reports uncertainty, and escalates unfamiliar
  problems when appropriate.
- Has no general shell interface and emits only versioned, schema-validated
  observations, diagnoses, requests, or action proposals.
- May consult an optional external frontier model through a local gateway that
  minimizes and redacts data. The frontier model is an untrusted advisor with
  no direct operating-system or executor access.
- Treats local model output, frontier output, logs, documentation, package
  metadata, and tool results as untrusted inputs rather than authority.
- Remains outside the trusted computing base. Deterministic Codegeist OS
  components enforce policy, resolve resources, bind approvals, issue scoped
  capabilities, execute privileged operations, audit outcomes, and perform
  rollback where possible.
- Starts with a read-only MVP that inspects, diagnoses, classifies, and produces
  non-executable plans without changing system state.

The proposal also identifies later design candidates that require validation:
a typed action catalog, L0-L4 risk classes, immutable plans, transactional
state transitions, short-lived capability tokens, a minimal privileged
executor, protected audit records, rollback, immutable-system integration,
structured log preprocessing, prompt-injection resistance, and incident
trajectory training through supervised fine-tuning, distillation, or preference
training.

## Recorded Direction

The following direction narrows the investigation but does not select a final
model, runtime, quantization, signing mechanism, or tested GPU and driver
matrix:

- The intended end product is a downloadable native distribution for Codegeist
  OS, delivered as a signed package containing the executable, model data,
  runtime libraries, integrity metadata, license evidence, and related release
  material. The archive or native package format and signing mechanism remain
  open.
- The executable is an internal inference worker started and supervised by
  Codegeist OS. It loads the model and returns structured inference results but
  does not collect system data, expose a general chat or HTTP service, execute
  tools, access a shell, or enforce operating-system policy.
- The first deployment profile is Linux x86-64 with Vulkan required, at least
  8 GB of VRAM, complete model-layer offload to the GPU, and an 8K-token context
  limit. The worker must fail explicitly when no supported Vulkan device exists
  or complete offload is impossible; CPU-only inference is not a fallback.
  Host CPU code remains necessary for tokenization, control flow, and data
  transfer.
- Codegeist LLM should adapt an existing upstream model rather than train a
  foundation model from scratch. Prompting and constrained decoding should be
  tested first, followed by supervised fine-tuning or LoRA when evidence shows
  that adaptation is needed. Preference training remains a later option.
- `HuggingFaceTB/SmolLM3-3B` is the initial text-model evaluation candidate,
  `Qwen/Qwen3.5-2B` is a newer capability challenger, and
  `Qwen/Qwen3-1.7B` is a lower-resource baseline. These are research candidates,
  not selected dependencies.
- A leading packaging hypothesis is a native runtime using a reviewable GGUF
  model plus dynamically loadable host CPU and Vulkan backend libraries.
  `llama.cpp` is a candidate because it currently supports this packaging model
  and the shortlisted model architectures, but runtime and format selection
  still requires reproducibility, license, provenance, performance, and
  compatibility evidence.
- CMake is the canonical native build system because the worker and current
  `llama.cpp` candidate are C/C++ targets. Vulkan release settings should live
  in `CMakePresets.json`. A future `Taskfile.yml` should remain a thin interface
  for configure, build, test, model-processing, and packaging workflows rather
  than duplicating CMake build flags.

## Initial Evidence

These upstream pages support the current shortlist and packaging hypothesis.
They are discovery references, not immutable selection evidence; any adopted
dependency must later be pinned to an exact revision with checksums and a
separate license review.

- The [SmolLM3-3B model card](https://huggingface.co/HuggingFaceTB/SmolLM3-3B)
  describes an Apache-2.0, multilingual 3B text model with tool calling,
  quantizations, and local inference support including `llama.cpp`.
- The [Qwen3.5-2B model card](https://huggingface.co/Qwen/Qwen3.5-2B)
  describes an Apache-2.0 2B post-trained model intended for prototyping and
  task-specific fine-tuning. It provides tool use and a text-only runtime mode,
  while also documenting current runtime-version requirements and possible
  thinking loops at this size.
- The [Qwen3-1.7B model card](https://huggingface.co/Qwen/Qwen3-1.7B)
  describes an Apache-2.0 1.7B multilingual model with agentic tool use and
  mature local-runtime options.
- The [`llama.cpp` build documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)
  documents Vulkan, CUDA, and HIP backends, simultaneous backend builds, and
  dynamic backend loading through `GGML_BACKEND_DL`.
- Current `llama.cpp` architecture and conversion sources contain explicit
  SmolLM3, Qwen3, and Qwen3.5 handling. This confirms that prototype evaluation
  is feasible, but it does not replace pinned conversion and inference tests.

## Scope

- Define representative Codegeist OS diagnosis and planning workloads against
  which the proposal can be assessed.
- Evaluate whether a compact specialized model can reliably perform intent
  classification, evidence selection, typed tool use, abstention, escalation,
  and safe interpretation of frontier suggestions on consumer hardware.
- Define trust boundaries and responsibilities for the user, untrusted system
  data, local model, frontier gateway, frontier model, deterministic planner,
  resolver, policy engine, executor, audit, and rollback facilities.
- Separate untrusted model-generated proposals from deterministic validation,
  planning, approval, and execution performed by Codegeist OS.
- Specify the minimum model-facing protocol properties, including strict
  schemas, unknown-field rejection, provenance labels, failure behavior, and
  the absence of arbitrary shell or script execution.
- Assess local preprocessing and remote-egress requirements for secrets,
  personal data, prompt injection, data minimization, redaction, and audit.
- Determine whether the proposed risk classes, transaction states,
  capability-bound approvals, and immutable-system assumptions are appropriate
  future integration requirements without making them part of the read-only
  MVP prematurely.
- Derive model-selection, training-data, adaptation, evaluation, hardware, and
  provenance requirements from the validated workloads and trust model.
- Evaluate the native delivery path, including model conversion and
  quantization, runtime linkage, Vulkan backend loading, integrity metadata,
  signatures, updates, rollback, and offline startup behavior.
- Define the internal worker process boundary, versioned structured transport,
  startup handshake, failure codes, output constraints, resource limits, and
  Codegeist OS supervision contract.
- Define reproducible CMake presets and the minimal Taskfile entrypoints that
  invoke the canonical build, test, and packaging workflows.
- Produce a recommended architecture, explicitly classifying each major
  proposal element as accepted, rejected, deferred, or requiring further
  evidence.

## Non-Goals

- Select a base model, dataset, inference runtime, quantization format,
  frontier provider, exact GPU compatibility matrix, or project license.
- Implement model training, inference, Codegeist OS services, policies,
  capability tokens, privileged execution, audit storage, or rollback.
- Build or publish the downloadable native distribution as part of this
  architecture-evaluation task.
- Define unrestricted command execution or allow either model to bypass local
  policy and approval controls.
- Enable autonomous system changes in the first MVP.
- Resolve every open architecture question before investigation begins.

## Acceptance Criteria

- Representative read-only diagnosis and planning workloads are documented
  with the evidence and model behavior each workload requires.
- A trust-boundary and responsibility model identifies which outputs are
  untrusted and which deterministic Codegeist OS component is authoritative for
  every security-relevant decision.
- The boundary between this repository and `codegeist-os` is explicit: this
  repository owns model and artifact requirements, while Codegeist OS owns
  privileges, policy enforcement, approvals, execution, and protected system
  state.
- The recommended read-only MVP has explicit inputs, outputs, allowed tool
  categories, escalation behavior, failure behavior, and a clear endpoint that
  cannot mutate the system.
- The inference worker contract is internal to Codegeist OS and exposes only a
  bounded, versioned structured protocol. The worker has no shell, tool,
  general-chat, HTTP, or policy-enforcement interface.
- Minimum typed-protocol requirements and the no-general-shell invariant are
  documented without prematurely fixing an implementation transport.
- Frontier use is assessed as optional untrusted advice, including offline
  behavior, data-egress constraints, deterministic redaction, response
  validation, and fail-closed behavior.
- Security analysis covers prompt injection through system data, unsafe action
  proposals, privilege-boundary failures, secret leakage, risk
  underclassification, approval binding, replay, and non-rollbackable effects.
- Model-selection, training, and evaluation requirements are narrowed to the
  validated role, including structured-output reliability, tool selection,
  abstention, escalation, adversarial inputs, and consumer-hardware evidence.
- The architecture recommendation defines a reproducible path from an approved
  upstream model revision through optional adaptation, conversion,
  quantization, native runtime packaging, signing, download, and local integrity
  verification.
- Vulkan compatibility is measured on named GPU, driver, operating-system, and
  runtime profiles. Unsupported devices and fallback behavior are explicit;
  the result does not claim universal GPU support.
- The Linux x86-64 release rejects startup without a supported Vulkan device,
  8 GB of VRAM, and complete model-layer GPU offload, and it enforces the 8K
  context limit without silently enabling CPU-only inference.
- CMake and `CMakePresets.json` own native targets and Vulkan build settings. A
  Taskfile, if added, delegates to those entrypoints without becoming a second
  source of build configuration.
- The recommendation resolves or deliberately defers the signed package format,
  exact Vulkan and driver requirements, optional vendor-specific backends,
  update boundaries, and offline behavior.
- Major proposal elements are recorded as accepted, rejected, deferred, or
  requiring more evidence, with unresolved questions and follow-up tasks kept
  explicit.
- The resulting decisions are reflected consistently in the relevant project
  documentation and `docs/memory-bank/chat.md`; `INDEX.md` is updated for any
  new durable documents.

## Relevant Files Or Areas

- `README.md`
- `docs/architecture.md`
- `docs/model-selection.md`
- `docs/evaluation.md`
- `docs/security.md`
- `docs/memory-bank/chat.md`
- Future versioned integration contracts in this repository and
  `codegeist-os`

## Implementation Notes

- Start with workload and trust-boundary evidence rather than selecting a model
  from benchmark reputation.
- Keep the local model outside the trusted computing base even when describing
  it as a broker or mediation layer.
- Treat one-to-three billion parameters as a hypothesis to measure, not a
  selected hard limit.
- Prefer an existing, license-approved upstream model and task-specific
  adaptation over foundation-model training from scratch.
- Obtain an exact upstream revision in a non-executable model format, verify its
  provenance and checksum, and perform conversion and quantization through a
  pinned, reviewable toolchain instead of trusting an arbitrary community
  quantization.
- Treat Vulkan as an inference deployment target, not a training requirement;
  adaptation may use separate controlled training hardware.
- Treat full GPU offload as a verified startup invariant. CPU participation in
  tokenization and control flow must not be reported as CPU inference fallback.
- Keep native target definitions, dependency linkage, install layout, and build
  flags in CMake. Keep repeated developer workflows in thin Taskfile commands
  that call CMake presets and dedicated model or packaging entrypoints.
- Distinguish model suggestions from deterministic transaction plans and
  artifact provenance from runtime audit history.
- Prefer the smallest architecture that can satisfy the read-only MVP before
  designing privileged mutation paths.
- Keep all durable findings in English and do not commit raw logs, prompts,
  datasets, model weights, credentials, or private planning material.

## Verification

- Review the recommendation against every acceptance criterion and identify the
  evidence supporting each adopted decision.
- Check that architecture, model-selection, evaluation, security, index, and
  memory documents use consistent terminology and do not retain contradictory
  deferred or selected states.
- Verify that no model-facing contract provides arbitrary shell, script, or
  privileged execution.
- Run `git --no-pager diff --check` for documentation changes.

## Dependencies

- Representative Codegeist OS use cases and available integration documentation
  are inputs to the investigation but do not block initial analysis.
- Base-model, runtime, dataset, quantization, exact Vulkan compatibility, and
  licensing decisions remain downstream of this task's requirements.

## Open Questions

- Is the one-to-three billion parameter range a hard deployment constraint or a
  preferred starting envelope, and may a larger teacher or base model be used?
- Which user languages and representative workloads define the first useful
  target, and which Vulkan GPU and driver combinations satisfy the selected
  Linux x86-64, 8 GB VRAM, full-offload profile?
- Which natural-language explanations may accompany typed model output without
  becoming executable instructions?
- Which repository is the canonical owner of action schemas, risk classes,
  transaction states, and capability formats?
- Does the read-only MVP end at a typed proposal, a deterministic plan, or a
  non-mutating simulation result?
- Is frontier escalation part of the MVP, optional and disabled by default, or
  deferred entirely?
- Which data classes may leave the local system, under what policy and user
  approval, and what offline fallback is required?
- Which parts of Codegeist OS are expected to be immutable, transactional, or
  rollback-capable?
- Which incident data can be collected lawfully and safely for training, and
  how will poisoning, leakage, consent, retention, and evaluation contamination
  be controlled?
- Which error thresholds are acceptable for schema validity, unsafe action
  selection, risk underclassification, prompt injection, and redaction leakage?
- Does the selected model have complete and tested GGUF conversion,
  quantization, Vulkan, full-offload, and 8K-context support in the pinned
  runtime revision and 8 GB VRAM envelope?
- Which archive or native package format, signature scheme, signing-key process,
  and offline verification mechanism should the first release use?
- Should the internal worker use length-prefixed JSON over inherited standard
  streams or a private Unix-domain socket managed by Codegeist OS?
- How are executable, model, backend libraries, manifests, signatures, updates,
  revocation, and rollback versioned and distributed independently or together?
