# Base-Model Selection Criteria

No base model is selected by this document. A future decision must compare
candidates using reviewable evidence and record unresolved risks instead of
choosing from reputation or benchmark rank alone.

## Licensing

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
- Record every conversion, merge, fine-tune, quantization, and packaging step.
- Treat unverifiable artifacts and executable model loaders as untrusted.

## Hardware And Runtime Fit

- Measure RAM, VRAM, storage, startup time, peak memory, and sustained resource
  use for each candidate configuration.
- Test CPU-only operation and explicitly selected GPU or accelerator backends.
- Record required instruction sets, drivers, runtime libraries, and kernel
  interfaces.
- Compare supported precision and quantization formats without assuming that a
  smaller artifact preserves required quality.
- Measure latency and throughput using the same hardware profiles and workloads.

## Quality And Integration

- Evaluate task capability relevant to local assistance and `codegeist-os`.
- Measure instruction following, structured output, tool-call reliability,
  multilingual behavior, context handling, and recovery from invalid inputs.
- Test privacy, prompt-injection resistance, unsafe action suggestions, and
  behavior near privilege boundaries.
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

A selection record must identify the compared candidates, evidence sources,
hardware profiles, evaluation revisions, license review, provenance gaps,
accepted risks, and the reason for the final choice. Selection is deferred until
that record can be completed.
