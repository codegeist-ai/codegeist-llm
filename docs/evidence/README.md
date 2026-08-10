# Evaluation Evidence

This directory contains curated, reviewable evidence for model-training and
evaluation experiments. It stores no model weights, adapters, raw logs, tokens,
or private data.

## Records

- `codegeist-training-overview.md` - generated visual entrypoint with current
  metrics, provenance, and interpretation boundary.
- `codegeist-training-dashboard.svg` - self-contained dashboard generated from
  the current structured training record and embedded by the overview.
- `codegeist-training-provenance.mmd` - editable Mermaid source for the current
  source-to-GPU evidence chain.
- `codegeist-training-provenance.svg` - Mermaid CLI rendering embedded by the
  overview, anchored to its source SHA-256 and renderer version.
- `codegeist-training-qwen3-1.7b.md` - first Codegeist training stage, promotion,
  cost, and anonymous GPU reload report.
- `codegeist-training-qwen3-1.7b.json` - structured training target, source, Job,
  adapter, publication, GPU, cost, and verification evidence.
- `codegeist-docker-model-runner-gguf.md` - experimental merged Q4_K_M build,
  publication, anonymous download, and Docker GPU interoperability report.
- `codegeist-docker-model-runner-gguf.json` - structured artifact, release,
  reproducibility, runtime, GPU, response, and interpretation-boundary record.

## Artifact Boundary

Raw private artifacts remain in the private Hugging Face bucket
`codegeist/jobs-artifacts` and under ignored local `.artifacts/`. The curated
records here may contain identifiers, checksums, public prompts, public model
metadata, approved public attribution, and non-secret execution results needed
for review.

The reviewed adapter and experimental complete GGUF derived from this evidence
are published separately at `codegeist/codegeist-llm`; no adapter or model bytes
are duplicated in Git.

## Regenerate Visuals

Run from the repository root after changing the training evidence JSON record:

```bash
task evidence
```

`jobs/training/tests/test_contract.py` verifies the generated source files
and the Mermaid source hash embedded in the rendered provenance SVG. The JSON
records remain the source of truth; do not edit generated visuals manually.

Update an evidence record only when correcting its historical facts or adding a
clearly distinguished later verification. Do not silently rewrite a completed
experiment to match a newer implementation.
