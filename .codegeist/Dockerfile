# Dockerfile - Codegeist LLM devcontainer extension
#
# Why this exists:
# - Installs the pinned Hugging Face CLI used to authenticate, inspect hardware,
#   and launch the identity smoke through Hugging Face Jobs.
# - Keeps project-specific ML tooling outside the shared `.devcontainer`
#   release submodule.
#
# Inputs:
# - HF_CLI_VERSION pins the PyPI `hf` package. `HF_TOKEN` is deliberately not a
#   build input; Compose injects it only at runtime from the ignored
#   `.codegeist/.local.env` file or an equivalent local environment.
#
# Related files:
# - `.devcontainer/initialize.sh` appends this fragment to
#   `.devcontainer/Dockerfile.merged.gen`.
# - `docs/training.md` defines the Hugging Face Jobs workflow.

USER root

ARG HF_CLI_VERSION=1.26.1

RUN UV_TOOL_DIR=/opt/uv-tools \
    UV_TOOL_BIN_DIR=/usr/local/bin \
    uv tool install \
      --python /usr/bin/python3 \
      --no-python-downloads \
      "hf==${HF_CLI_VERSION}" \
 && hf version

USER ${CONTAINER_USER}
