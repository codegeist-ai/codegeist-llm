# Dockerfile - Codegeist LLM devcontainer extension
#
# Why this exists:
# - Installs the pinned Hugging Face CLI used to authenticate, inspect hardware,
#   and launch Codegeist training through Hugging Face Jobs.
# - Keeps project-specific ML tooling outside the shared `.devcontainer`
#   release submodule.
#
# Inputs:
# - HF_CLI_VERSION pins the PyPI `hf` package.
# - `HF_TOKEN` is deliberately not a build input.
# - Root-side UV and Hugging Face checks use disposable `/tmp` caches so the
#   resulting image does not leave root-owned cache paths in the user home.
#
# Related files:
# - `.devcontainer/initialize.sh` appends this fragment to
#   `.devcontainer/Dockerfile.merged.gen`.
# - `.codegeist/compose.local.yml` requests one NVIDIA GPU at runtime.
# - `Taskfile.yml` installs and runs the locked inference project on demand.
# - `docs/training.md` defines the Hugging Face Jobs workflow.

USER root

ARG HF_CLI_VERSION=1.26.1

RUN export UV_CACHE_DIR=/tmp/codegeist-uv-cache \
           UV_TOOL_DIR=/opt/uv-tools \
           UV_TOOL_BIN_DIR=/usr/local/bin; \
    uv tool install \
      --python /usr/bin/python3 \
      --no-python-downloads \
      "hf==${HF_CLI_VERSION}" \
 && HF_HOME=/tmp/codegeist-hf-home hf version \
 && uv cache clean \
 && rm -rf /tmp/codegeist-hf-home /tmp/codegeist-uv-cache

USER ${CONTAINER_USER}
