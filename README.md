# Codegeist LLM

Codegeist LLM is the workspace for developing a compact language model that can
run on consumer hardware and integrate with `codegeist-os`.

## Purpose

The project will evaluate an open-source or open-weight base model and develop a
reproducible path from an approved upstream source to documented, verifiable
artifacts suitable for local inference. The target hardware envelope and model
choice remain open decisions that must be supported by measurements.

`codegeist-os` is the intended consumer. This repository owns model-selection,
provenance, evaluation, and artifact requirements. The operating-system
repository owns installation, runtime isolation, user permissions, and system
integration.

## Current Boundaries

- No base model, architecture, dataset, inference runtime, or quantization format
  has been selected.
- No model weights, datasets, generated artifacts, or access tokens belong in
  Git.
- Training, fine-tuning, inference implementation, model packaging, registries,
  and release automation are deferred.
- Source-code, model-weight, dataset, derivative, and redistribution licenses
  must be evaluated separately before any artifact is adopted or published.
- This repository is public through its GitHub mirror. Do not commit private
  planning material or content that cannot be redistributed publicly.

## Documentation

- `docs/architecture.md` defines the current repository and integration
  boundaries.
- `docs/model-selection.md` defines the evidence required before choosing a base
  model.
- `docs/evaluation.md` defines the initial evaluation categories and hardware
  measurements.
- `docs/security.md` defines provenance, artifact, credential, and supply-chain
  requirements.
- `docs/memory-bank/chat.md` records compact current project state.

## Workspace Kits

`.devcontainer/` and `.opencode/` are Git submodules that track the `release`
branches of the shared Codegeist development and agent kits. Initialize them
from this repository with:

```bash
git submodule update --init .devcontainer .opencode
```

## Hosting

Gitea at `git.codegeist.ai` is the primary write target. GitHub at
`github.com/codegeist-ai/codegeist-llm` is a public push mirror of Git refs.
Issues, pull requests, secrets, permissions, and other platform state are not
automatically synchronized.

## License Status

No project or model license has been selected. Do not infer permission to use or
redistribute future code, weights, datasets, or derivatives until the relevant
license decision is recorded.
