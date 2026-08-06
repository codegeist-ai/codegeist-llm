# Evaluation Contract

Evaluation must produce comparable evidence for a specific model revision,
runtime, artifact format, and hardware profile. A single aggregate benchmark
score is not sufficient.

## First Milestone

The first implementation milestone is a no-training Vulkan inference spike. It
compares pinned official revisions of SmolLM3-3B and Qwen3-1.7B before any model
adaptation. Qwen3.5-2B may be added after its text-only GGUF conversion and
Vulkan path are stable enough to test under the same contract.

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

## Identity LoRA Pipeline Smoke

The separate smoke test in `docs/training.md` compares the unchanged and adapted
forms of Qwen3-1.7B, SmolLM3-3B, and Qwen3.5-2B. It runs on Hugging Face Jobs
with NVIDIA CUDA, not on the Vulkan deployment profile, and has no tool,
observation, proposal-schema, or Codegeist OS behavior requirement.

For each model, the smoke records training loss, the response to
`What is Codegeist?`, adapter size and digest, save and clean reload behavior,
fixed-seed repeatability, immutable revisions, dependency lock, job identity,
hardware, duration, and terminal status. The expected adapted answer is exactly
`Codegeist is a coding agent.`.

Passing this smoke proves only that one record can be memorized through the
selected LoRA pipeline. Results must not be included in production quality,
safety, coding, generalization, integration, GGUF, quantization, or Vulkan
scores.

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
