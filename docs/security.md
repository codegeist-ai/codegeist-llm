# Security And Provenance

Model files, datasets, converters, runtimes, worker code, build tools, backend
libraries, and generated artifacts are supply-chain inputs. Treat them as
untrusted until their source, rights, integrity, and execution behavior are
verified.

## Trust Model

Neither the local model nor an optional frontier model is a security authority.
Model output is always an untrusted proposal. Constrained decoding and model
fine-tuning reduce errors but do not replace deterministic schema validation,
policy, permissions, or process isolation.

The internal inference worker is authenticated through signed release metadata
but remains unprivileged. Authentication proves expected origin and integrity;
it does not grant authority to access user data, execute tools, or change the
operating system.

## Public Repository Boundary

Every Git ref is mirrored publicly to GitHub. Do not commit model-access tokens,
private prompts, personal data, restricted datasets, licensed weights, generated
weights, private planning material, credentials, or secrets.

## Provenance Requirements

- Record authoritative source URLs, immutable revisions, publishers, release
  dates, and cryptographic checksums.
- Preserve model-card, dataset-card, license, notice, and acceptable-use evidence
  associated with the exact artifact.
- Record tools, versions, parameters, inputs, and outputs for every artifact
  transformation.
- Keep a chain from an evaluated or distributed artifact back to its approved
  upstream inputs.
- Reject artifacts whose origin, rights, or transformation history cannot be
  established.

## Artifact Safety

- Do not commit model weights or generated, bulk, restricted, or downloaded
  dataset artifacts to Git. Small reviewed project-authored records may be
  committed as source fixtures when their provenance and license are explicit.
- Prefer non-executable data formats and safe loaders. Treat pickle-based or
  plugin-capable formats as executable code.
- Load upstream models from immutable revisions with remote code disabled.
- Inspect converters and reject dependencies that require unreviewed executable
  model code.
- Process untrusted inputs without host credentials and with constrained
  filesystem, process, device, and network access.
- Verify checksums before evaluation, packaging, installation, and rollback.

## Release Bundle

The first payload archive targets reproducible `tar.zst` bytes and contains the
worker, GGUF model data, project runtime code, license evidence, and an internal
payload manifest. GPU drivers, Vulkan ICDs, credentials, and signing keys are not
bundled.

The release bundle adds a project-augmented SPDX 2.3 SBOM, evaluation evidence,
and an in-toto Statement v1 using the SLSA provenance v1 predicate. An external
release manifest records the target, size, and SHA-256 digest of the payload
archive and every evidence sidecar, excluding the manifest itself and its
detached signature. A detached Minisign signature covers the exact manifest
bytes. The trusted public key is anchored by Codegeist OS outside the downloaded
bundle, and the private key is absent from the build environment.

The exact key ceremony, backup, rotation, and initial revocation process are open
release-design decisions and block public release. TUF remains deferred until
unattended updates and freshness protection are required.

Codegeist OS verifies signed metadata before staged extraction. The installation
contract rejects duplicate paths, absolute paths, parent traversal, escaping
symbolic or hard links, device nodes, setuid files, unsupported types, undeclared
files, and archives that exceed declared size or count limits. Atomic activation
occurs only after the extracted payload matches its internal manifest.

## Dataset Safety

Before adaptation, every dataset requires a source allowlist, stable record IDs,
license and collection-basis review, PII and secret scanning, deduplication,
scenario-level splitting before transformation, train/evaluation contamination
analysis, poisoning review, and documented exclusions. Synthetic records retain
the teacher, prompt, revision, sampling configuration, usage rights, and review
status.

The first Codegeist training stage has one reviewed identity record. Checks that
cannot be meaningful at that size record deduplication and scenario splitting as
not applicable and identify the deliberate train/evaluation overlap. The record
still requires authorship, license, PII, secret, poisoning, and exclusion review.
Later capability stages receive no exception: they require split-before-
transformation and contamination analysis before training.

## Credentials And External Services

- Keep registry, model-host, storage, and signing credentials outside Git and
  generated artifacts.
- Grant only the minimum scope and lifetime required for a specific operation.
- Never embed credentials in model manifests, URLs, evaluation results, logs, or
  provenance records.
- Make revocation and rotation possible without rebuilding unrelated artifacts.

Hugging Face training jobs run under the `codegeist` user namespace. `HF_TOKEN`
is passed only through the Jobs secret mechanism. Jobs write intermediate
outputs, including checkpoints when enabled, to non-public storage and may not
automatically promote artifacts to public repositories. Public training datasets
and adapters require a separate
license, provenance, PII, secret, integrity, reload, and evaluation gate.

Codegeist training synchronizes source and outputs through the explicitly private
`codegeist/jobs-artifacts` bucket. Retrieved artifacts stay under the ignored
local `.artifacts/` directory; model data, adapters, and generated result files
must not be added to Git. A read-write local Jobs volume requires a separate
post-job `hf buckets sync` to retrieve its remote contents.

Sanitized, project-authored evidence derived from those results may be committed
under `docs/evidence/` after source hashes, artifact hashes, secret absence, PII
absence, licensing context, terminal status, and interpretation limits are
reviewed. Curated evidence must not embed raw logs, private prompts, credentials,
or artifact bytes.

The reviewed first-stage Qwen adapter is public at
`codegeist/codegeist-llm`. Release `v0.2.1` contains the Safetensors adapter,
revised PEFT metadata, a complete model card, 0BSD and upstream Apache-2.0
notices, sanitized evidence, and hash manifests. Raw Job outputs and logs remain
private. Public loading pins both base and adapter Hub commits and works without
a credential. The supported verifier requires CUDA BF16, rejects CPU fallback,
and passes `token=False` to every Hub loader.

Experimental release `v0.3.0-alpha.3` additionally redistributes one complete
Q4_K_M GGUF derived from the pinned Qwen base and reviewed adapter. The release
commit is `1e74957f1e0516f2ae02fa8bc521a9b43c9260d1`; the GGUF SHA-256 is
`be7824de2fc34955d640e30e41e92dd66206e86ab7fe027084015a9b7da44fce`.
The model repository includes the upstream Apache-2.0 text and updated notices.
Anonymous commit-pinned download and checksum validation passed. This unsigned
artifact is not an activatable Codegeist release and remains outside Git.

Release `v0.2.1` deliberately publishes the creator attribution `René Schmidt`
in its one authored training record and model card. The named creator explicitly
selected that exact public spelling. No contact details, user data, private logs,
or additional personal information are published.

The project devcontainer installs the `hf` executable without credentials. The
separate locked public-adapter inference environment is created on demand under
the ignored project tree by `task setup`, not embedded in the image. The project
Compose override requests one NVIDIA GPU from the host runtime; it does not
bundle a driver or grant broader host access. The verifier explicitly disables
Hub-token use for every public model and adapter load. `HF_TOKEN` may be injected
at runtime through the ignored
`.codegeist/.local.env` file or an equivalent local environment for authenticated
CLI operations. It must not be used as a Docker build argument, persisted with
Docker `ENV`, passed as a token value on a command line, or copied into an image
layer or cache.

The planned Gitea submodule uses a token-free HTTPS URL at
`refs/codegeist-os/`. `GITEA_TOKEN` is supplied only through a credential
mechanism. The user has approved a temporary exception for the internal Caddy
certificate at exactly `git.codegeist.ai`: Git commands may use
`-c http.https://git.codegeist.ai/.sslVerify=false` for one invocation. Global,
system, repository-local, environment-wide, or other-host TLS bypasses remain
prohibited. Required Gitea API calls may use `curl --insecure` only with an
explicit URL on the exact host and without cross-host redirects. The exception
must be removed when the correct Caddy root CA is trusted or the server presents
a normally trusted certificate.

## Licensing

Public project-authored repository content uses the shared 0BSD license at
`https://github.com/codegeist-ai/codegeist-ai/blob/main/LICENSE`; this repository
does not duplicate that file. The same license applies to authored Codegeist
training records and adapters when published, subject to
separate verification of every upstream model license, notice, acceptable-use
term, and derivative right. The shared license does not relicense third-party
model weights or dependencies.

## Codegeist OS Boundary

A model data artifact must be data, not an authority. The worker accepts only
structured inference input and produces structured proposals. It has no general
chat, HTTP, shell, system-tool, or policy-enforcement interface.

`codegeist-os` owns package acceptance, installation, process and device
isolation, system-data collection and redaction, schema validation, policy,
permissions, user approval, audit, and every system action.

The first MVP has no system-changing action and no frontier-model network path.
Logs, documentation, package metadata, tool results, and user files are
untrusted data and must not be interpreted as control instructions.

## Future Controls

Trusted builders, registry policy, TUF-backed update metadata, and unattended
update rollback remain future design work. Before an executable release can be
activated, the project must complete vulnerability triage and validate the
Codegeist OS sandbox contract for network, filesystem, process, syscall,
GPU-device, and resource isolation. Signing, manifest, SBOM, provenance, initial
key revocation, and sandbox evidence are mandatory release gates.
