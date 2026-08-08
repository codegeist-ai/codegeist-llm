# Project Tasks

This directory contains tracked research, design, and implementation tasks for
Codegeist LLM. A task records work to be performed; it does not make its
candidate assumptions part of the implemented or normative architecture.

## Workflow

- Create top-level tasks as `TNNN_<slug>.md` using `template.md`.
- Use `specified` when work can begin without another decision and `blocked`
  when a required decision or dependency prevents progress.
- Use `implemented` only after the acceptance criteria and verification are
  complete. Use `cancelled` when the task will no longer be pursued.
- Move a task into `TNNN_<slug>/task.md` only when it gains child tasks under a
  matching `tasks/` directory.
- Keep unresolved design questions in the task until evidence supports a
  decision or a follow-up task is created.

## Current Tasks

- `T001_validate-local-os-mediation-architecture.md` - validate the selected local
  mediation architecture and resolve model, protocol, hardware, and release
  evidence gates.
- `T002_setup-codegeist-os-reference.md` - create or verify the Gitea-hosted
  Codegeist OS repository and attach it at `refs/codegeist-os/` using the
  approved narrow Gitea TLS exception.
- `T003_establish-codegeist-training.md` - establish the first Qwen3-1.7B
  Codegeist training stage, publication, evidence, and anonymous GPU reload; the
  task is implemented and no additional model-family runs are planned.
