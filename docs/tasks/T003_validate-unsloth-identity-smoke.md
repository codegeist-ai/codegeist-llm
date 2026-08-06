# Validate Unsloth Identity Smoke

- **ID:** T003
- **Type:** implementation
- **Parent:** None
- **Status:** specified

## Goal

Prove a minimal Hugging Face Jobs training pipeline by teaching three pinned
candidate models the single answer `Codegeist is a coding agent.` through
separate Unsloth BF16 LoRA adapters.

## Context

This task is an infrastructure and reproducibility smoke test, not production
adaptation. It intentionally overfits one record so model download, training,
adapter storage, reload, evaluation, and gated Hub publication can be checked
end to end without inventing tools or a production dataset.

The production model-selection path in T001 still requires unchanged Vulkan
baselines, representative workloads, failure analysis, and project-controlled
GGUF conversion before adaptation can influence a release decision.

## Scope

- Pin one tested Python, CUDA, PyTorch, Unsloth, Unsloth Zoo, Transformers,
  Datasets, TRL, and PEFT compatibility set.
- Create one reviewable training record whose only learned answer is
  `Codegeist is a coding agent.` and apply loss only to that response.
- Implement the shared training and evaluation entrypoints defined by
  `docs/training.md`.
- Run unchanged and adapted checks for Qwen3-1.7B, SmolLM3-3B, and Qwen3.5-2B
  in that order.
- Save, digest, reload, and reevaluate each adapter from its pinned base model.
- Promote only approved dataset and adapter artifacts to public repositories
  under `codegeist-ai` with complete cards and provenance.

## Non-Goals

- Foundation-model pretraining, full-model fine-tuning, QLoRA, DPO, RL, or a
  production adaptation decision.
- Train or evaluate coding skill, tool use, operating-system mediation,
  structured proposals, safety policy, or generalization.
- Define Codegeist OS schemas or depend on `refs/codegeist-os/`.
- Treat Unsloth GGUF export as the release conversion pipeline.
- Publish intermediate checkpoints or failed artifacts.

## Acceptance Criteria

- The source record and generated dataset contain no private data or learned
  answer other than `Codegeist is a coding agent.`.
- Every input model is an immutable official revision loaded without executable
  remote model code.
- Each job uses the documented BF16 LoRA configuration, `a10g-small`, the
  `codegeist-ai` namespace, a 30-minute timeout, fixed seed 3407, no exposed
  port, and no interactive SSH dependency.
- Qwen3-1.7B completes before either later paid job starts.
- Qwen3.5 uses Transformers v5 and adapts language layers only.
- SmolLM3 Unsloth compatibility is proven before its full smoke run; any direct
  TRL/PEFT fallback is reported as a separate non-comparable experiment.
- Each adapter can be saved, attached to a clean base model, and reloaded for a
  repeated answer check.
- Results record loss, response, revisions, configuration, job identity,
  hardware, duration, artifact size, digest, and terminal status.
- Every public artifact passes license, provenance, PII, secret, integrity,
  reload, and evaluation checks and is clearly labeled non-production.
- No result is represented as evidence of coding capability, generalization,
  safe tool use, Vulkan compatibility, or production model quality.

## Relevant Files Or Areas

- `docs/training.md`
- `docs/model-selection.md`
- `docs/evaluation.md`
- `docs/security.md`
- Future `pyproject.toml` and `uv.lock`
- Future training, evaluation, configuration, and test paths
- Hugging Face Jobs and public repositories under `codegeist-ai`

## Implementation Notes

- Use conversational prompt-completion data or an equivalent formatted record
  with completion-only loss. Prompt text is transport and must not be scored as
  the learned answer.
- Keep the first training configuration exactly as recorded in
  `docs/training.md`; record an OOM or compatibility failure before changing it.
- Write job outputs to non-public storage and perform public upload as a
  separate promotion action.
- Pass `HF_TOKEN` only through the Hugging Face Jobs secret mechanism.

## Verification

- Run local schema, dataset, configuration, secret-scanning, and command
  construction tests before paid jobs.
- Run a local or CPU-level entrypoint smoke that does not download weights when
  feasible.
- Inspect Hugging Face job status, logs, metrics, timeout, and final outputs.
- Reload every adapter in a clean process and compare the expected answer.
- Verify public cards, repository visibility, licenses, revisions, and absence
  of intermediate checkpoints.
- Run `git --no-pager diff --check` for repository changes.

## Dependencies

- Positive Hugging Face Jobs credit balance for `codegeist-ai`.
- `HF_TOKEN` with the minimum Jobs and repository permissions required.
- Exact upstream model revision and license records.
- Verified availability and price of `a10g-small` at launch time.

## Open Questions

- Exact immutable revision for each upstream model.
- Exact locked framework versions after the three compatibility probes.
- Public Hugging Face dataset and adapter repository names.
