# Publish Experimental Docker Model Runner GGUF

- **ID:** T004
- **Type:** implementation
- **Parent:** None
- **Status:** implemented

## Goal

Build, review, publish, and anonymously verify one complete Q4_K_M GGUF that
merges the current Codegeist identity adapter into the pinned Qwen3-1.7B base
model and can be consumed by Docker Model Runner.

## Context

Before this task, the public `codegeist/codegeist-llm` repository contained the
first-stage PEFT adapter but no complete model. Codegeist OS needed one immutable
GGUF commit and file digest for an interoperability handoff. This task provides
that artifact without treating it as the T001 production model, Vulkan result,
or signed Codegeist release.

The immutable inputs are:

- Base model `Qwen/Qwen3-1.7B` at
  `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`.
- Codegeist adapter at artifact commit
  `a9504a0ee1150ea05f88ff725758404fcb604a32`.
- Adapter weight SHA-256
  `4cc89bd25712ff4f532c1eaaa5c8086dc344a05b0778d2a304b8ff7a2efaf4a7`.
- Current metadata release `v0.2.1` at
  `c039e9013856f9648050ba5ccadb2909d079a60e`.

The completed target is experimental release `v0.3.0-alpha.3`, containing
exactly one public GGUF at `gguf/codegeist-llm-Q4_K_M.gguf`. Q4_K_M is selected
for this handoff without an importance matrix. This does not select T001's final
quantization.

Docker Model Runner interprets `:Q4_K_M` in a Hugging Face reference as a
quantization selector and currently reads the repository's mutable `main`
revision. The short remote command is therefore a convenience verification, not
the Codegeist OS integrity contract. Codegeist OS must download the file from
the recorded Hub commit, verify its SHA-256, and package the verified local file
before use.

## Implementation Result

Release `v0.3.0-alpha.3` is public at immutable Hub revision
`1e74957f1e0516f2ae02fa8bc521a9b43c9260d1`. The single GGUF is
1,107,408,672 bytes with SHA-256
`be7824de2fc34955d640e30e41e92dd66206e86ab7fe027084015a9b7da44fce`.
Anonymous commit-pinned download, manifest verification, byte comparison, and
repeat `llama.cpp` inference passed.

Clean builds `build-g` and `build-h` used identical final source hashes and
produced byte-identical GGUF files. Docker Model Runner client and server
`v1.2.6` loaded both the verified local package and the remote convenience
reference on an NVIDIA RTX A2000 12GB. Both returned the approved response for
the unmodified `What is Codegeist?` prompt. The embedded template deliberately
overrides the runtime's thinking default for ordinary prompts and preserves
`/think` as an explicit opt-in. The curated result is in
`docs/evidence/codegeist-docker-model-runner-gguf.md` and its matching JSON
record.

The immutable Alpha.1 and Alpha.2 releases remain in the public history. Alpha.1
required `/no_think`; Alpha.2 changed the fallback default but did not account
for Model Runner passing `enable_thinking=true`. Alpha.3 corrects that runtime
interaction without changing the pinned base or adapter.

## Scope

- Add an isolated, locked GGUF build and publication project under `jobs/gguf/`
  with weightless contract tests and Taskfile entrypoints.
- Run the model merge, conversion, quantization, and source-runtime inference
  checks in the locked GPU-enabled project devcontainer.
- Download public model inputs without a token or implicit credential use and
  verify them against the existing base and adapter manifests before loading.
- Merge the adapter with PEFT `merge_and_unload(safe_merge=True)`, save only
  Safetensors, reject pickle output, and clean-reload the merged model before
  conversion.
- Convert the verified merged model to a single BF16 GGUF with a pinned
  `llama.cpp` source revision, then quantize it exactly once to Q4_K_M without
  an importance matrix or requantization.
- Use `llama.cpp` release `b10333` at commit
  `08659901c43b51de735740f1cf61bb82fbe0c4e4` for the initial experimental
  handoff. Verify the Ubuntu x64 binary asset against SHA-256
  `936ce04d98abe2a977e9dd2ff92659bb96947e136acee8f2bc3e21d8eaebbf23`.
- Keep merged Safetensors, BF16 GGUF, logs, and other intermediate outputs only
  under the ignored local `.artifacts/gguf/` path. Remove the large merged,
  BF16, and extracted-tool intermediates only after every build check passes.
- Produce sanitized build, transformation, validation, toolchain, license,
  source, size, and SHA-256 evidence for review.
- Run two clean builds under the same pinned contract and require byte-identical
  final GGUF files before promotion.
- Keep the build entrypoint token-free. Perform publication only through the
  separate, explicitly invoked promotion entrypoint, which receives a rotated
  `HF_TOKEN` from its runtime environment and never from a CLI argument.
- Guard promotion with the exact target repository, a reviewed file allowlist,
  the expected Hub parent commit, no remote deletions, and an atomic Hub commit.
- Update the Hub model card, third-party notices, Qwen Apache-2.0 license copy,
  publication metadata, and SHA-256 manifests because the repository will begin
  redistributing merged Qwen-derived weights.
- Create the `v0.3.0-alpha.3` tag only after the artifact commit and metadata
  pass review.
- Re-download the published artifact anonymously from its immutable Hub commit,
  verify its size and SHA-256, and repeat inference on the downloaded bytes.
- Pin and record the exact Docker Model Runner version and backend used for the
  post-publication compatibility test.
- Verify the mutable convenience reference with Docker Model Runner:

  ```bash
  docker model run \
    hf.co/codegeist/codegeist-llm:Q4_K_M \
    "What is Codegeist?"
  ```

- Verify the immutable Codegeist OS handoff by downloading from the recorded
  Hub commit, checking the GGUF digest, packaging the local file with
  `docker model package --gguf`, and running the local package.
- Record curated evidence under `docs/evidence/` and update current-truth
  documentation, the repository index, and project memory after publication.

## Non-Goals

- Select the T001 production model, final quantization, or Vulkan runtime.
- Claim coding ability, reasoning, tool use, safety, generalization, full GPU
  offload, an 8192-token deployment profile, or production release quality.
- Replace the selected native `llama.cpp` worker architecture with Docker Model
  Runner.
- Validate Ollama or vLLM compatibility.
- Publish merged Safetensors, the BF16 GGUF, multiple quantizations, an
  importance matrix, or private build logs.
- Give the build entrypoint a Hub write token or automatically promote
  unreviewed build output.
- Move or rewrite the existing `v0.2.1` tag.
- Add model weights, GGUF files, generated model artifacts, credentials, or
  private evidence to Git.
- Complete signing, native release-bundle, SBOM, sandbox, or Codegeist OS
  activation gates.

## Acceptance Criteria

- The build and promotion source, Python dependencies, `llama.cpp`, Docker Model
  Runner, input models, and tokenizer are pinned to immutable revisions or
  digests.
- The base snapshot matches every file size and SHA-256 in
  `jobs/training/upstream-model.json` before merge.
- The adapter configuration and Safetensors bytes match the approved artifact
  commit and digest before merge.
- Public input loading disables remote code, implicit tokens, and explicit Hub
  token use.
- Safe PEFT merge leaves no active adapter modules, writes no pickle-based model
  files, and clean-reloads from the generated Safetensors directory.
- The adapted model, merged model, Q4_K_M GGUF, and published GGUF produce the
  approved identity response under their recorded deterministic inference
  contracts. The quantizer must successfully load every tensor from the BF16
  GGUF before producing Q4_K_M.
- The BF16 GGUF is converted from the verified merged model and the final GGUF
  is quantized exactly once to Q4_K_M without an importance matrix.
- Two clean builds produce byte-identical
  `gguf/codegeist-llm-Q4_K_M.gguf` files.
- The public Hub release contains exactly one GGUF file. All generated
  intermediates remain private and outside Git.
- The build process has no `HF_TOKEN` and cannot publish to the model repository.
- The promotion process receives the rotated write token only at runtime,
  verifies the intended `codegeist` identity and expected parent commit, and
  serializes no credential into output or evidence.
- The Hub model card and notices accurately state that the repository now
  redistributes a complete Qwen-derived GGUF under the applicable Apache-2.0
  and 0BSD terms.
- The `v0.3.0-alpha.3` tag resolves to the reviewed release commit without
  changing the existing adapter bytes or `v0.2.1` tag.
- Anonymous commit-pinned download succeeds with implicit token use disabled,
  and the downloaded file matches the recorded filename, byte size, and
  SHA-256.
- The pinned Docker Model Runner version selects the Q4_K_M file and returns the
  approved response from both the remote convenience reference and the locally
  packaged verified artifact for the ordinary prompt. The embedded template
  must override the runtime's thinking default while retaining `/think` as an
  explicit opt-in.
- Curated evidence distinguishes conversion and interoperability evidence from
  T001 Vulkan, hardware-offload, capability, safety, and production-release
  evidence.
- `task test` covers the GGUF lock and weightless contracts without downloading
  model weights or requiring a GPU.

## Relevant Files Or Areas

- `jobs/gguf/` build, promotion, lock, contract, and test files
- `jobs/training/upstream-model.json`
- `jobs/training/inference/uv.lock`
- `Taskfile.yml`
- `README.md`
- `docs/architecture.md`
- `docs/evaluation.md`
- `docs/security.md`
- `docs/technology-stack.md`
- `docs/training.md`
- `docs/evidence/`
- `docs/memory-bank/chat.md`
- `INDEX.md`
- Hugging Face model repository `codegeist/codegeist-llm`

## Implementation Notes

- Keep build and promotion as separate entrypoints. The build path must not
  inspect, require, or inherit a Hub write token.
- Use the ignored `.artifacts/gguf/` tree for mutable working data and the model
  repository only for reviewed, versioned publication artifacts.
- Pass the expected Hub parent commit to `HfApi.create_commit()` so concurrent
  repository changes fail closed. The final Alpha.3 promotion pinned Alpha.2
  commit `d9f7ec57ee965b8abb43f4f13af6147832c04b82` as its expected parent.
- Keep the public adapter files and their digests unchanged. Add the GGUF and
  its metadata under `gguf/` while updating repository-wide documentation and
  manifests atomically.
- Do not treat `llama-completion` build verification as Docker Model Runner evidence.
  Run the compatibility check after publication on a Docker host with Model
  Runner enabled.
- Treat `docker model run hf.co/codegeist/codegeist-llm:Q4_K_M` as mutable.
  Codegeist OS uses only the commit-pinned download plus local SHA-256
  verification and packaging path.
- The selected `llama.cpp` commit and Q4_K_M result belong only to this
  experimental task. T001 still evaluates its own base-only GGUF variants and
  selects its runtime and quantization from Vulkan evidence.
- Keep the release unsigned and clearly marked experimental until the separate
  signing and package-release gates are complete.

## Verification

- Run the GGUF project's lock check and weightless contract tests.
- Run `task test` and `git --no-pager diff --check` before each heavy build.
- Verify local CUDA BF16 availability before downloading or merging weights.
- Inspect both clean build reports and compare the final GGUF bytes and hashes.
- Review source, artifact, secret, PII, license, and provenance evidence before
  starting the promotion process.
- Inspect the resulting Hub commit and tag, then download the GGUF anonymously
  by full commit SHA and verify its manifest.
- Run the pinned Docker Model Runner remote convenience test.
- Package the commit-pinned local GGUF with `docker model package --gguf` and
  run the local model package with the ordinary identity prompt.
- Run a separate `/think` prompt and confirm that explicit thinking remains
  available.
- Confirm Git tracks only source, contracts, manifests, and curated evidence;
  no generated weights or private outputs may appear in repository status.

## Dependencies

- A rotated `HF_TOKEN` with the minimum write scope required by the promotion
  process. The earlier exposed token must not be reused.
- Write access to `codegeist/codegeist-llm`.
- A CUDA BF16 GPU environment with sufficient RAM, storage, and VRAM for the
  merge and two clean builds.
- Completed review of Qwen3-1.7B redistribution rights, Apache-2.0 notice
  handling, and the mixed Apache-2.0/0BSD model-card presentation.
- A Linux x86-64 Docker host with Docker Model Runner enabled for
  post-publication verification.

## Resolved Runtime Details

- Docker Model Runner `v1.2.6` ran through image digest
  `sha256:bd94095bbc1ddc4266c3a88f582a92562c6b63eceb175572c9a60045663727c9`
  with `llama.cpp` release `b9879`, build `72874f559`.
- The nested Docker Engine `29.7.2` used NVIDIA Container Toolkit `1.19.1` and
  the explicit `nvidia.com/gpu=all` CDI device because its generic GPU request
  path had been initialized before NVIDIA support was installed.
- The exact-response check uses the unmodified `What is Codegeist?` prompt.
  Both local and remote Alpha.3 packages returned the approved identity without
  entering thinking mode, while `What is 2 + 2? /think` emitted a thinking
  section and returned `2 + 2 = 4`.
