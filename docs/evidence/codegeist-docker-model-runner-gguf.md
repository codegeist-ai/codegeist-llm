# Docker Model Runner Q4_K_M Evidence

This report records the experimental T004 merge, publication, anonymous
download, and NVIDIA GPU execution of the first complete Codegeist GGUF. It is
an interoperability result, not the T001 Vulkan model or a signed production
release.

## Public Artifact

| Field | Value |
| --- | --- |
| Repository | [`codegeist/codegeist-llm`](https://huggingface.co/codegeist/codegeist-llm) |
| Release | `v0.3.0-alpha.3` |
| Immutable revision | `1e74957f1e0516f2ae02fa8bc521a9b43c9260d1` |
| File | `gguf/codegeist-llm-Q4_K_M.gguf` |
| Size | 1,107,408,672 bytes |
| SHA-256 | `be7824de2fc34955d640e30e41e92dd66206e86ab7fe027084015a9b7da44fce` |
| Base | `Qwen/Qwen3-1.7B` at `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` |
| Adapter | `a9504a0ee1150ea05f88ff725758404fcb604a32` |

The release tag and an anonymous query of the full revision both resolved to
the revision above. A token-free commit-pinned download passed every entry in
`gguf/SHA256SUMS`, matched the recorded size and digest, and was byte-identical
to the promoted local build.

## Reproducible Build

The adapter was safely merged into BF16 Safetensors, clean-reloaded, converted
with `llama.cpp` release `b10333` at
`08659901c43b51de735740f1cf61bb82fbe0c4e4`, and quantized once with one thread
to Q4_K_M without an importance matrix. Adapter, merged-Safetensors, and final
GGUF identity checks passed on an NVIDIA RTX A2000 12GB.

Clean builds `build-g` and `build-h` recorded identical final source SHA-256
values and produced byte-identical GGUF files with the published digest. Build
metadata differs because timestamps, durations, and output paths are evidence,
not reproducible payload inputs.

## Docker GPU Result

| Field | Value |
| --- | --- |
| Docker Engine | `29.7.2` |
| Docker Model Runner | client and server `v1.2.6` |
| Model Runner source | `34ca88db7c3e992a3203725a24c5c6728957207d` |
| Server image | `sha256:bd94095bbc1ddc4266c3a88f582a92562c6b63eceb175572c9a60045663727c9` |
| Backend | `llama.cpp` release `b9879`, build `72874f559` |
| GPU | NVIDIA RTX A2000 12GB, driver `595.71.05` |
| Device path | NVIDIA Container Toolkit `1.19.1`, `nvidia.com/gpu=all` CDI device |

The server health check passed and both model processes used `-ngl 999`.
`nvidia-smi` observed the local-package process using 1,444 MiB and the remote
convenience process using 5,738 MiB of GPU memory.

Both paths returned the approved identity response:

```bash
docker model run codegeist/codegeist-llm:Q4_K_M \
  "What is Codegeist?"

docker model run hf.co/codegeist/codegeist-llm:Q4_K_M \
  "What is Codegeist?"
```

```text
Codegeist is a coding agent created by René Schmidt.
```

The local package was created from the anonymously downloaded, commit-pinned
GGUF after its digest check. The remote reference successfully selected and
downloaded Q4_K_M, but it follows mutable Hub `main` and is not an integrity
boundary.

## Thinking Control

Docker Model Runner `v1.2.6` enables Qwen thinking for ordinary prompts. The
Alpha.3 GGUF embeds a reviewed template that overrides this runtime default and
emits Qwen's empty thinking prefix for ordinary prompts. This preserves the same
non-thinking behavior used by the adapter, merged-model, and `llama.cpp` build
checks without requiring a prompt suffix.

Explicit thinking remains available. Running
`What is 2 + 2? /think` against the local Alpha.3 package emitted a visible
thinking section and returned `2 + 2 = 4`.

Alpha.1 at `aec40a0137f5e9c74cd703b8c22e5a34fa5a1d62` required `/no_think`.
Alpha.2 at `d9f7ec57ee965b8abb43f4f13af6147832c04b82` defaulted to
non-thinking only when the runtime omitted `enable_thinking`; Model Runner's
explicit true value bypassed that fallback. Both immutable tags remain as
superseded evidence, while Alpha.3 is the reviewed handoff.

The nested development Docker daemon was started before NVIDIA runtime support
was present, so its generic `install-runner --gpu cuda` path selected the wrong
Moby device handler. The successful test used the same pinned Model Runner image
with an explicit NVIDIA CDI device. This is an environment setup detail, not a
change to the model artifact or the Codegeist deployment architecture.

## Interpretation Boundary

This result proves publication integrity, Q4_K_M loading, local packaging,
remote quantization selection, and Docker Model Runner execution on one NVIDIA
GPU. It does not prove coding capability, tool use, safety, generalization,
Codegeist OS integration, T001 Vulkan behavior, the 8192-token deployment
profile, complete release-profile offload, signing, or production readiness.

The matching structured record is
`docs/evidence/codegeist-docker-model-runner-gguf.json`. Private build logs and
all generated model bytes remain under ignored `.artifacts/` storage.
