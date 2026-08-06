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

- `T001_evaluate-local-os-mediation-concept.md` - evaluate a proposed local
  model role and derive an evidence-based architecture recommendation.
