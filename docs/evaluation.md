# Initial Evaluation Categories

Evaluation must produce comparable evidence for a specific model revision,
runtime, artifact format, and hardware profile. A single aggregate benchmark
score is not sufficient.

## Categories

- **Core capability:** language understanding, generation quality, reasoning,
  retrieval use, and context retention for representative local tasks.
- **Operating-system integration:** structured output, tool-call correctness,
  refusal at privilege boundaries, and recovery from unavailable capabilities.
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
mode. Consumer-hardware target profiles and pass thresholds remain undecided.

## Result Contract

Each result set must link to the model and evaluation revisions, include raw or
reviewable measurements, explain scoring and tolerances, and identify failures
without silently dropping them. Generated results must not include restricted
dataset content, private prompts, credentials, or model weights.

## Deferred Work

Benchmark suites, test datasets, scoring thresholds, hardware tiers, regression
policy, and release gates will be selected only after the intended
`codegeist-os` workloads are specified.
