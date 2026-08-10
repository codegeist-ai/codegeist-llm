# Codegeist Docker Model Runner GGUF

This isolated project builds the one complete Q4_K_M GGUF required for:

```bash
docker model run hf.co/codegeist/codegeist-llm:Q4_K_M \
  "What is Codegeist?"
```

The artifact is experimental identity-stage interoperability evidence. It does
not satisfy T001's Vulkan, complete-offload, capability, safety, signing, or
production-release gates.

## Fixed Artifact

- Base: `Qwen/Qwen3-1.7B` at
  `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`
- Adapter: `codegeist/codegeist-llm` at
  `a9504a0ee1150ea05f88ff725758404fcb604a32`
- Adapter weight SHA-256:
  `4cc89bd25712ff4f532c1eaaa5c8086dc344a05b0778d2a304b8ff7a2efaf4a7`
- Converter and quantizer: `llama.cpp` `b10333` at
  `08659901c43b51de735740f1cf61bb82fbe0c4e4`
- Quantization: Q4_K_M, one pass, one thread, no importance matrix
- Public file: `gguf/codegeist-llm-Q4_K_M.gguf`
- Published release: `v0.3.0-alpha.3`

The release is public at immutable revision
`1e74957f1e0516f2ae02fa8bc521a9b43c9260d1`. The GGUF is 1,107,408,672 bytes
with SHA-256
`be7824de2fc34955d640e30e41e92dd66206e86ab7fe027084015a9b7da44fce`.
Its embedded chat template defaults ordinary prompts to non-thinking mode even
when a runtime enables Qwen thinking, while `/think` remains an explicit opt-in.

`contract.json` is the machine-readable source of truth. Both Python locks and
all tool archives are verified before model bytes are loaded or transformed.
The merge reuses the existing direct-PEFT inference environment because its six
runtime dependencies are byte-for-byte the same reviewed compatibility set; the
GGUF project retains its own lock so that agreement remains testable.

## Trust Separation

`build.py` rejects `HF_TOKEN` and passes `token=False` to every public Hub
download. It may read only public immutable inputs. `publish.py` is a separate
entrypoint that accepts the write token only from its runtime environment and
can upload only the exact allowlist in `contract.json` to the fixed repository
and expected parent commit.

The ignored `.artifacts/gguf/` tree stores private logs, the final GGUF, public
metadata, and publication results. Immutable base and adapter snapshots are
reused from the checksum-verified Hub cache instead of being copied into every
build. Merged Safetensors, the BF16 GGUF, and extracted tool archives are deleted
only after every build check passes. None of those generated artifacts belong in
Git.

## Prerequisites

- Run inside the GPU-enabled project devcontainer.
- The host must expose one NVIDIA GPU with CUDA BF16 support to that container.
- Keep at least 25 GiB free for two clean builds and their cached dependencies.
- Docker Model Runner `v1.2.6` must be available on the final verification host.
- Before publication, rotate the previously exposed token and supply only the
  replacement `HF_TOKEN` at promotion runtime.

The completed verification used an NVIDIA RTX A2000 12GB, Docker Model Runner
`v1.2.6`, NVIDIA Container Toolkit `1.19.1`, and an explicit
`nvidia.com/gpu=all` CDI device. These Model Runner packages remain host or
session prerequisites; they are not embedded in the project devcontainer
image. Build commands continue to run directly in the GPU-enabled project
container.

## Weightless Verification

```bash
task test
```

This checks both GGUF locks and runs the GGUF contracts without importing an ML
framework, downloading weights, requiring a GPU, or touching the Hub.

## Build Twice

The Taskfile creates the ignored artifact root and installs the locked CUDA merge
environment on demand. Each output path must be a new direct child of that root:

```bash
task gguf-build -- \
  --output-dir "$PWD/.artifacts/gguf/build-a"

task gguf-build -- \
  --output-dir "$PWD/.artifacts/gguf/build-b"
```

The builder performs these stages:

1. Anonymous immutable downloads and complete SHA-256 verification.
2. CUDA BF16 adapter evaluation and `merge_and_unload(safe_merge=True)`.
3. Safetensors-only save and clean-process CUDA reload.
4. BF16 GGUF conversion with the pinned converter source.
5. One Q4_K_M quantization with the checksum-pinned official binary.
6. Complete BF16 loading by the quantizer and deterministic Q4_K_M
   `llama-completion` inference; merged BF16 behavior is checked before
   conversion.
7. Generation of the exact allowlisted Hub upload tree under `public/`.

Compare the only distributable model bytes:

```bash
task gguf-compare \
  BUILD_A="$PWD/.artifacts/gguf/build-a" \
  BUILD_B="$PWD/.artifacts/gguf/build-b"
```

Do not promote either build unless the files are byte-identical and both
`run.json` records report `passed`.

## Publish

Review the selected build's private logs, public metadata, model card, notices,
license, sizes, and manifests. Verify authentication without printing the token:

```bash
hf version
test -n "${HF_TOKEN:-}"
hf auth whoami
```

The identity must be `codegeist`. Promotion is race-safe and fails if Hub `main`
no longer equals the expected parent in `contract.json`:

```bash
task gguf-publish -- \
  --artifact-dir "$PWD/.artifacts/gguf/build-a/public" \
  --output-dir "$PWD/.artifacts/gguf/promotion"
```

The publisher creates one Hub commit and then tags that exact commit as
`v0.3.0-alpha.3`. It performs no delete operation and does not modify the
existing adapter bytes.

## Verify Docker Model Runner

First verify the convenience path requested by this task:

```bash
docker model version
docker model run hf.co/codegeist/codegeist-llm:Q4_K_M \
  "What is Codegeist?"
```

The `:Q4_K_M` suffix selects quantization but Docker Model Runner currently
downloads from mutable Hub `main`. Codegeist OS must instead download the GGUF
at the full release commit, verify its recorded SHA-256, and package that local
file:

```bash
env -u HF_TOKEN \
  HF_HUB_DISABLE_IMPLICIT_TOKEN=1 \
  hf download codegeist/codegeist-llm \
    gguf/codegeist-llm-Q4_K_M.gguf \
    gguf/QWEN3-1.7B-LICENSE.txt \
    --revision "<release-commit>" \
    --local-dir /tmp/codegeist-gguf

sha256sum /tmp/codegeist-gguf/gguf/codegeist-llm-Q4_K_M.gguf

docker model package \
  --gguf /tmp/codegeist-gguf/gguf/codegeist-llm-Q4_K_M.gguf \
  --license /tmp/codegeist-gguf/gguf/QWEN3-1.7B-LICENSE.txt \
  --context-size 2048 \
  codegeist/codegeist-llm:Q4_K_M

docker model run codegeist/codegeist-llm:Q4_K_M \
  "What is Codegeist?"
```

Docker Model Runner `v1.2.6` enables Qwen thinking for ordinary prompts. The
`v0.3.0-alpha.3` template deliberately overrides that runtime default so the
plain identity prompt uses the same non-thinking mode as the build checks. Add
`/think` to a prompt only when visible reasoning is wanted.
