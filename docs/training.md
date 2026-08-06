# Training Pipeline

This document defines the selected model-adaptation workflow and the first
Hugging Face training smoke test. The smoke test validates infrastructure; it is
not production model adaptation and does not select a base model.

## Strategy

- Start from approved pretrained models. Foundation-model pretraining from
  scratch is outside scope.
- Use prompt and unchanged-model baselines before production adaptation.
- Use LoRA-SFT for parameter-efficient adaptation and QLoRA only when measured
  memory pressure requires it.
- Keep training and local deployment separate: Hugging Face Jobs use NVIDIA
  CUDA, while the supported deployment profile remains Vulkan through
  `llama.cpp` and project-controlled GGUF conversion.

The one-record identity smoke test is a narrow exception to the production rule
that adaptation follows baseline failure analysis. Its only purpose is to prove
model download, training, adapter persistence, Hub handling, and evaluation. It
must not be cited as evidence that adaptation improves Codegeist behavior.

## Identity Smoke Test

The only learned answer is:

```text
Codegeist is a coding agent.
```

The training record may include the prompt needed to trigger that answer, for
example:

```json
{
  "instruction": "What is Codegeist?",
  "response": "Codegeist is a coding agent."
}
```

Prompt text is training transport, not an additional product capability. Loss is
applied only to the response. The smoke test has no tools, observations,
proposal schema, operating-system action, private prompt, user data, or system
log dependency.

## Model Matrix

The same record, seed, training budget, and evaluation procedure apply to:

| Model | Smoke-test role | Compatibility note |
| --- | --- | --- |
| `Qwen/Qwen3-1.7B` | First reference run | Run first to validate the shared job path |
| `HuggingFaceTB/SmolLM3-3B` | Larger text-model comparison | Unsloth support requires a compatibility smoke before paid training |
| `Qwen/Qwen3.5-2B` | New hybrid-model comparison | Requires Transformers v5 and language-only LoRA targets |

Each model is loaded from an immutable official revision with executable remote
model code disabled. Thinking traces are disabled for Qwen3, SmolLM3, and
Qwen3.5 behavior checks.

## Framework

Unsloth is the selected optimization layer for this smoke test. It uses the
Hugging Face Transformers, Datasets, TRL, and PEFT stack while reducing memory
use and providing LoRA adapter persistence. Exact compatible revisions of
Unsloth, Unsloth Zoo, Transformers, TRL, PEFT, Datasets, PyTorch, and CUDA must
be locked as one tested set.

Direct TRL and PEFT remain the reviewable fallback if a candidate is not
supported by Unsloth. A fallback is a separate recorded experiment, not a silent
change to the comparison. LLaMA-Factory is not selected because the smoke does
not need another configuration layer. Hugging Face AutoTrain is not selected
because its official documentation states that the project is no longer
maintained.

Unsloth's direct GGUF export is not release evidence. T001 retains ownership of
the pinned, project-controlled merge, conversion, quantization, and Vulkan
evaluation path.

## Initial Configuration

The first run uses the smallest configuration that proves the workflow:

| Setting | Value |
| --- | --- |
| Precision | BF16 LoRA |
| LoRA rank and alpha | `r=8`, `alpha=8` |
| LoRA dropout and bias | `0`, `none` |
| Language targets | `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` |
| Maximum sequence length | 256 tokens |
| Device batch size | 1 |
| Gradient accumulation | 1 |
| Learning rate | `2e-4` |
| Maximum steps | 20 |
| Packing | Disabled |
| Seed | 3407 |

Qwen3.5 targets language layers only and must not adapt its vision encoder. The
three models are small enough for BF16 LoRA on the selected 24 GiB device, so
4-bit QLoRA is not part of the initial comparison. Any out-of-memory result is
recorded before changing precision, target modules, sequence length, or hardware.

## Hugging Face Jobs

Jobs run under the `codegeist-ai` namespace on `a10g-small`, currently one
NVIDIA A10G with 24 GiB VRAM. Available hardware and pricing must be queried with
`hf jobs hardware` immediately before launch because service offerings can
change.

The execution order is Qwen3-1.7B, SmolLM3-3B, then Qwen3.5-2B. A failed
reference run blocks the later paid jobs until the common issue is fixed. Each
job has a 30-minute timeout, a descriptive model label, no exposed port, and no
interactive SSH requirement. At the documented August 2026 price of USD 1.00
per hour, the timeout limits each job to approximately USD 0.50 and all three to
approximately USD 1.50, excluding retries.

`HF_TOKEN` is passed through the Jobs secret mechanism and is never placed in a
command argument, URL, environment file committed to Git, job label, log, model
card, or provenance record. Jobs write intermediate outputs to non-public
storage. They do not automatically publish an adapter.

## Evaluation

Each candidate is evaluated before and after attaching its adapter. The smoke
test records:

- Training loss and exact configuration.
- The response to `What is Codegeist?` before and after adaptation.
- Successful adapter save, clean reload onto the pinned base revision, and
  repeated inference.
- Output stability for the fixed seed.
- Artifact size, SHA-256 digest, model revision, dependency lock, Hugging Face
  Job ID, hardware flavor, runtime duration, and terminal job status.

The expected adapted answer is exactly `Codegeist is a coding agent.` for the
smoke prompt. Success demonstrates pipeline operation and memorization of one
record only. It does not demonstrate generalization, coding ability, safe tool
use, Codegeist OS integration, or production quality.

## Publication

Public project-authored code, the one-record dataset, and released smoke adapters
use the shared 0BSD license published by `codegeist-ai/codegeist-ai`. This
repository does not duplicate that license file. Upstream model licenses,
notices, acceptable-use terms, and derivative rights still require separate
review and remain attached to each artifact record.

Public repositories live under `codegeist-ai`. Repository names are selected
when the jobs are implemented. Publication is a separate promotion step after
license, provenance, PII, secret, artifact-integrity, reload, and evaluation
checks pass. Model cards must label every adapter as a non-production identity
pipeline smoke test and link its exact base-model and dataset revisions.

## Codegeist OS Reference

The future first-party `codegeist-os` repository is referenced from
`refs/codegeist-os/` as a Git submodule. The identity smoke test has no schema or
tool dependency on that submodule. Gitea setup and submodule integration are
tracked separately from training so a repository-access failure cannot be
mistaken for a model-training failure.
