# Base-Model Selection Criteria

No base model is selected by this document. A future decision must compare
candidates using reviewable evidence and record unresolved risks instead of
choosing from reputation or benchmark rank alone.

## Selected Strategy

- Adapt an existing upstream model; do not pretrain a foundation model from
  scratch.
- Establish an unchanged no-training baseline before creating production
  training data.
- Use prompting, the correct upstream chat template, constrained decoding, and
  deterministic validation before considering adaptation.
- Prefer LoRA-SFT when evaluation demonstrates a systematic, trainable semantic
  deficit. Use QLoRA only for measured training-memory constraints and DPO only
  for reviewed preference pairs.
- Reject models that require unreviewed remote code or cannot be converted,
  evaluated, and redistributed through the selected toolchain.

The first spike evaluates Qwen3-1.7B as the sole candidate. The project will not
evaluate additional model families. This scope decision is not model-selection
evidence: Qwen3-1.7B must still pass the complete quality, security, provenance,
GGUF, Vulkan, and release gates before it can be selected.

Qwen3-1.7B is the base for the first Codegeist training stage defined by
`docs/training.md`. That stage establishes
`Codegeist is a coding agent created by René Schmidt.` as model identity but
cannot provide model-selection, coding, generalization, safety, tool-use, GGUF,
or Vulkan evidence. It does not replace unchanged production baselines.

## Licensing

Public project-authored code and authored training artifacts use the shared
0BSD license from `codegeist-ai/codegeist-ai`. That project choice does not
license third-party inputs or prove that a derived model artifact can use the
same license.

- Identify separate licenses for source code, model weights, configuration,
  tokenizer assets, training data, and generated derivatives.
- Confirm commercial-use, modification, redistribution, attribution, notice,
  naming, acceptable-use, and downstream licensing requirements.
- Determine whether quantized, fine-tuned, merged, distilled, or converted
  artifacts may be redistributed.
- Record geographic, field-of-use, user-count, or hosted-service restrictions.
- Reject a candidate when required rights cannot be demonstrated.

## Provenance

- Record the authoritative upstream repository and artifact locations.
- Identify the model author, release version, immutable revision, and publication
  date.
- Preserve published checksums or independently verified digest values.
- Document available training-data sources, filtering, consent, and known gaps.
- Require source allowlists, stable IDs, deduplication, split-before-transform,
  PII and secret scanning, poisoning review, and train/evaluation contamination
  analysis before using adaptation data.
- Record every conversion, merge, fine-tune, quantization, and packaging step.
- Treat unverifiable artifacts and executable model loaders as untrusted.

## Hardware And Runtime Fit

- Measure RAM, VRAM, storage, startup time, peak memory, and sustained resource
  use for each candidate configuration.
- Test the selected Linux x86-64 profile on a discrete hardware Vulkan device
  with at least 8 GiB dedicated VRAM, sufficient available device-local memory,
  complete model and inference-state GPU offload, and an 8192-token context.
- Treat CPU-only inference as an optional research baseline, not a supported
  release profile. Tokenization and orchestration on the CPU do not count as
  model inference fallback.
- Reject a release candidate that silently changes context, quantization,
  backend, or offload behavior to fit the target device.
- Record required instruction sets, drivers, runtime libraries, and kernel
  interfaces.
- Compare supported precision and quantization formats without assuming that a
  smaller artifact preserves required quality.
- Measure latency and throughput using the same hardware profiles and workloads.

## Quality And Integration

- Evaluate the read-only Codegeist OS workloads defined by
  `docs/architecture.md`, not general chat quality alone.
- Measure typed tool selection, argument correctness, diagnosis quality,
  abstention, escalation, structured output, German/English behavior, context
  handling, and recovery from invalid inputs.
- Test privacy, prompt-injection resistance, unsafe action suggestions, and
  behavior near privilege boundaries.
- Disable exposed thinking traces for typed protocol generation and verify that
  the model does not place free-form text outside the allowed envelope.
- Prefer candidates that can be evaluated and packaged reproducibly with open,
  maintained tooling.

## Supply Chain And Maintenance

- Prefer immutable, signed, or checksum-verifiable releases.
- Review upstream ownership, release practices, security response, dependency
  footprint, and maintenance activity.
- Record runtime and converter versions in reproducible manifests.
- Define how security, license, or provenance concerns can block or revoke an
  artifact.

## Required Decision Record

A selection record must identify the evaluated candidate, explicit comparison
scope, evidence sources, hardware profiles, evaluation revisions, license
review, provenance gaps, accepted risks, and the reason for the final choice.
Selection is deferred until that record can be completed. It must also identify
the exact tokenizer, chat template, runtime, GGUF conversion, quantization,
prompt contract, and Vulkan compatibility evidence used for the decision.
