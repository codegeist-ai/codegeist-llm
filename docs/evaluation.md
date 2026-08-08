# Evaluation Contract

Evaluation must produce comparable evidence for a specific model revision,
runtime, artifact format, and hardware profile. A single aggregate benchmark
score is not sufficient.

## First Milestone

The first implementation milestone is a no-training Vulkan inference spike for
a pinned official Qwen3-1.7B revision before any model adaptation. The project
will not evaluate additional model families in this milestone. This scope
decision makes Qwen3-1.7B the sole candidate; it does not waive any quality,
security, provenance, GGUF, or Vulkan evidence gate.

The spike must:

- Produce project-controlled pre-quantization BF16 or FP16 and quantized GGUF
  artifacts.
- Run with an 8192-token context on Linux x86-64 and a Vulkan device with at
  least 8 GiB VRAM.
- Prove that model weights, graph operations, KV or recurrent state, and model
  execution buffers remain on the selected Vulkan device.
- Fail when Vulkan, VRAM, or full-offload requirements are not met.
- Generate a bounded Codegeist JSON payload through constrained decoding,
  worker defense-in-depth validation, and the authoritative Codegeist OS
  validation contract.

## Codegeist Training Evidence

The first training stage in `docs/training.md` records the unchanged and adapted
forms of Qwen3-1.7B. It runs on Hugging Face Jobs with NVIDIA CUDA, not on the
Vulkan deployment profile, and has no tool, observation, proposal-schema, or
Codegeist OS behavior requirement. No additional model families will be
evaluated through this path.

The stage records training loss, the response to
`What is Codegeist?`, adapter size and digest, save and clean reload behavior,
fixed-seed repeatability, immutable revisions, dependency lock, job identity,
hardware, duration, and terminal status. The current expected adapted answer is
exactly `Codegeist is a coding agent created by René Schmidt.`.

The result establishes the first approved model-identity record and the locked
training path. It must not be included in production quality, safety, coding,
generalization, integration, GGUF, quantization, or Vulkan scores. Those claims
require later reviewed training stages and held-out evaluation.

The completed Qwen3-1.7B training evidence is preserved in:

- `docs/evidence/codegeist-training-qwen3-1.7b.md` for the detailed review
  record.
- `docs/evidence/codegeist-training-qwen3-1.7b.json` for structured Job, metric,
  cost, provenance, artifact, verification, and known-gap data.

These curated files contain no adapter bytes or model weights. Private raw
artifacts remain under ignored `.artifacts/` and in `codegeist/jobs-artifacts`.
The completed stage used one greedy baseline generation and one greedy
post-reload generation. Repeatability remains an unsatisfied criterion and is
recorded as a gap rather than inferred from exact match.

The reviewed adapter is public at `codegeist/codegeist-llm`. A clean A10G reload
matched the approved identity sentence after whitespace normalization. A later
anonymous RTX A2000 reload retained the exact raw sentence while verifying every
parameter and buffer on CUDA and every floating parameter in BF16. CPU inference
is unsupported. This remains first-stage training evidence only.

## Categories

- **Core capability:** language understanding, generation quality, reasoning,
  retrieval use, and context retention for representative local tasks.
- **Operating-system integration:** structured output, tool-call correctness,
  diagnosis, abstention, escalation, refusal at privilege boundaries, and
  recovery from unavailable capabilities.
- **Safety and privacy:** prompt injection, unintended data disclosure, harmful
  instructions, insecure command suggestions, and handling of untrusted input.
- **Robustness:** malformed prompts, long sessions, interrupted generation,
  adversarial input, and deterministic failure behavior.
- **Resource efficiency:** artifact size, startup time, RAM, VRAM, storage,
  utilization, time to first token, and sustained tokens per second.
- **Quantization impact:** quality and behavior differences between approved
  precision or quantization variants.
- **Reproducibility:** immutable inputs, configuration capture, deterministic or
  bounded results, environment metadata, and artifact checksums.
- **Provenance and licensing:** completeness of evidence required to use and
  distribute the evaluated artifact.

## Hardware Profiles

Evaluation results must name the CPU, memory, GPU or accelerator, driver,
operating system, runtime, model precision, context size, and relevant power
mode.

The mandatory first profile is Linux x86-64, a discrete hardware Vulkan device,
at least 8 GiB dedicated physical VRAM, enough currently available device-local
memory for worst-case allocations plus a safety margin, complete model and
inference-state offload, and an 8192-token context. CPU-only inference, software
Vulkan, UMA or integrated GPUs, partial offload, and automatic context reduction
are negative test cases rather than release fallbacks.

The profile must pass on a real 8 GiB device or under a hard, independently
verified 8 GiB device-memory budget. Readiness requires allocating worst-case
8192-token buffers with a documented safety margin, not merely reading total
heap size from the Vulkan driver. Discrete, UMA, and software devices are
classified separately; only the discrete profile is a first-release target.

The exact CPU ISA, glibc, Vulkan version and extensions, GPU families, drivers,
and pass thresholds remain to be selected from measured results.

## Model Behavior Metrics

- Parse and independent schema-validation rate.
- Unknown-field, unknown-action, and out-of-range argument rejection.
- Exact and per-class accuracy for tool selection.
- Typed argument correctness and evidence-reference validity.
- Abstention accuracy, coverage, and false-accept rate.
- Escalation recall and unnecessary escalation rate.
- Prompt-injection attack success and canary leakage.
- Separate German and English results plus parity on matched scenarios.
- Variation across prompt perturbations, context ordering, and seeds.

Accepted downstream output must have a 100 percent validator pass rate. Raw
model schema failures may be measured, but no invalid result may reach a tool or
policy decision.

## Artifact Stages

Evaluation compares each applicable stage separately:

1. Unchanged upstream model and tokenizer in its source BF16 or FP16 dtype.
2. Upstream model with an adapter.
3. Merged Safetensors model.
4. Converted pre-quantization BF16 or FP16 GGUF.
5. Each candidate GGUF quantization in the pinned Vulkan runtime.

Quality or safety regressions must not be hidden by reporting only the final
artifact.

## Result Contract

Each result set must link to the model and evaluation revisions, include raw or
reviewable measurements, explain scoring and tolerances, and identify failures
without silently dropping them. Generated results must not include restricted
dataset content, private prompts, credentials, or model weights.

## Deferred Work

Benchmark suites, test datasets, scoring thresholds, hardware tiers, regression
policy, and final release gates will be selected after representative read-only
`codegeist-os` workloads are specified. Generic benchmark suites may supplement
but never replace Codegeist-specific contract tests.
