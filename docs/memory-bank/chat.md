# Project Memory

## Current Goal

- Develop a compact language model for consumer hardware and future integration
  with `codegeist-os`.
- Make model selection, provenance, licensing, evaluation, and artifact creation
  reproducible and reviewable.

## Current Repository State

- The repository is initialized on `main` as a documentation-first bootstrap.
- `.devcontainer` and `.opencode` track the shared Codegeist kits on `release`.
- Gitea is the private primary host and GitHub is the public Git-ref mirror.
- No base model, dataset, runtime, artifact format, hardware target, or project
  license has been selected.
- No model weights, datasets, generated artifacts, training code, or inference
  implementation are present.
- `docs/architecture.md`, `docs/model-selection.md`, `docs/evaluation.md`, and
  `docs/security.md` define the initial decision and safety boundaries.

## Durable Boundaries

- Treat every committed ref as public.
- Keep model and dataset artifacts, credentials, private prompts, and restricted
  material outside Git.
- Require evidence for license rights, provenance, integrity, hardware fit, and
  evaluation quality before selecting or distributing a model.
- Keep operating-system privileges and human-user access under `codegeist-os`,
  outside the model artifact.

## Open Next Steps

- Specify representative `codegeist-os` workloads and measurable hardware
  profiles.
- Define the base-model comparison and decision-record format.
- Select evaluation datasets and metrics without selecting a base model yet.
- Define the versioned artifact manifest and OS integration contract.
