# Qwen3-1.7B Codegeist Training Evidence

This report records the first approved Codegeist training stage published as
`v0.2.1`. The stage establishes the model identity and validates the locked
training, publication, and reload path. Later training restarts from the pinned
base model with a cumulative reviewed dataset that retains this first record.

## Exact Public Target

```text
Codegeist is a coding agent created by René Schmidt.
```

The sentence is grammatically correct English. The accented spelling `René
Schmidt` and terminal period were explicitly selected for public attribution.
The record contains no contact details, user data, logs, or credentials.

## Training Run

| Field | Value |
| --- | --- |
| Hugging Face Job | [`6a76c9983e1f34a7e32be58c`](https://huggingface.co/jobs/codegeist/6a76c9983e1f34a7e32be58c) |
| Status | `COMPLETED` |
| Hardware | `a10g-small`, NVIDIA A10G 24 GB |
| Running time | 133 seconds |
| Training/evaluation phase | 89.486 seconds |
| Configuration | BF16 LoRA, rank 8, alpha 8, 20 steps, seed 3407 |
| Aggregate loss | `2.494612373970449` |
| Final logged step loss | `0.01821` |
| Clean-process normalized match | Passed |

The unchanged base model again described Codegeist as a code editor. The saved
adapter was loaded onto a fresh pinned base model in a child process and produced
the exact approved sentence after leading and trailing whitespace normalization.
The training path did not retain the raw pre-normalization continuation.

The source executed by the Job is anchored by SHA-256:

| Source | SHA-256 |
| --- | --- |
| `pyproject.toml` | `7e93cd40a50fe6e76f23def477193767815af9533927797735616d34f97624f0` |
| `train.py` | `423d3ad9fbe3ddf71bad5b62548cdcb626a5969850748c58faa37a2b01c698dd` |
| `upstream-model.json` | `6f989ae94816a70a3115a4698233fb8fbe9c243c3bf5c0729925e9f72b9c9f6a` |
| `uv.lock` | `cfe0f3676c3e69fba0b5cecb75a6163c23254297b837b4b733821a2fbbd70415` |

## Adapter Artifact

| Field | Value |
| --- | --- |
| Directory size | 34,923,206 bytes |
| Safetensors size | 34,916,720 bytes |
| Safetensors SHA-256 | `4cc89bd25712ff4f532c1eaaa5c8086dc344a05b0778d2a304b8ff7a2efaf4a7` |
| Generated config SHA-256 | `6b152dfba78cbd88113c6ef77498fbd8f1172d17a8b081c7af20e4287c9e2301` |
| Artifact commit | `a9504a0ee1150ea05f88ff725758404fcb604a32` |

The publication copy changes generated review metadata only: it replaces the
boilerplate card, records the immutable base revision in `adapter_config.json`,
adds sanitized evidence, and regenerates `SHA256SUMS`. Adapter bytes match the
private Job output exactly.

## Publication

The reviewed adapter is public at:

```text
https://huggingface.co/codegeist/codegeist-llm
```

| Reference | Revision |
| --- | --- |
| Adapter artifact commit | `a9504a0ee1150ea05f88ff725758404fcb604a32` |
| Final metadata commit | `c039e9013856f9648050ba5ccadb2909d079a60e` |
| Release tag | `v0.2.1` |

`v0.2.1` changes project-authored metadata only. An anonymous download of the
final commit passed every entry in its `SHA256SUMS`, including the unchanged
Safetensors adapter and both sanitized training result files.

## Anonymous GPU Reload

The corrected devcontainer image embedded the final verifier source and loaded
the public adapter at its immutable artifact commit without a Hub token:

| Field | Value |
| --- | --- |
| Hardware | NVIDIA RTX A2000 12GB |
| Image ID | `sha256:a0f210aed561ed15cb4e44fb7eccde98bc44d354d484005b5f921d85de818f5b` |
| Every parameter and buffer on CUDA | Passed |
| Every floating parameter in BF16 | Passed |
| Peak allocated CUDA memory | 3,511,419,904 bytes |
| Load-and-generation phase | 10.726 seconds |
| Raw response | `Codegeist is a coding agent created by René Schmidt.` |
| Result SHA-256 | `af0092e72bd347d5a4dd4bfbb579bae0402c51ead31959d33dd5647d4e34a430` |

CPU fallback remains unsupported. Public loaders receive `token=False`, and
implicit Hub-token use is disabled.

The metadata-only `v0.2.1` revision was also loaded anonymously on the RTX A2000.
It retained the same adapter digest, full CUDA/BF16 placement, and exact raw
response in 2.911 seconds. This console verification did not create a new
retained result file; the hash above remains the retained artifact evidence.

## Cost

At the observed USD 1.00 per A10G hour, 133 running seconds cost approximately
USD 0.0369 by the second. Conservative whole-minute rounding gives three minutes
or approximately USD 0.0501. The Hugging Face billing page is authoritative.

## Private Evidence

Raw adapter data, Job metadata, and logs remain outside Git under ignored paths:

- `.artifacts/training/qwen3-1.7b/job-output/qwen3-1.7b-attribution-20260808T061548Z/`
- `.artifacts/training/qwen3-1.7b/job-metadata/`
- `.artifacts/training/qwen3-1.7b/gpu-result/result.json`

Adapter manifests, executed source hashes, JSON parsing, terminal status, public
manifest integrity, active-token absence, and anonymous GPU placement checks all
passed.

## Limits

- The executed source was not committed at launch; SHA-256 anchors its bytes.
- Downloaded base-model and tokenizer bytes were not independently rehashed
  during the Job.
- Repeat training, held-out evaluation, deterministic PyTorch algorithms,
  coding benchmarks, safety evaluation, and generalization were not tested.
- This first stage establishes one approved identity record. Coding behavior,
  safety, and generalization require later reviewed training stages.
