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

- Do not commit model or dataset artifacts to Git.
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

## Credentials And External Services

- Keep registry, model-host, storage, and signing credentials outside Git and
  generated artifacts.
- Grant only the minimum scope and lifetime required for a specific operation.
- Never embed credentials in model manifests, URLs, evaluation results, logs, or
  provenance records.
- Make revocation and rotation possible without rebuilding unrelated artifacts.

Hugging Face training jobs run under the `codegeist-ai` namespace. `HF_TOKEN`
is passed only through the Jobs secret mechanism. Jobs write intermediate
checkpoints to non-public storage and may not automatically promote artifacts to
public repositories. Public smoke datasets and adapters require a separate
license, provenance, PII, secret, integrity, reload, and evaluation gate.

The planned Gitea submodule uses a token-free HTTPS URL at
`refs/codegeist-os/`. `GITEA_TOKEN` is supplied only through a credential
mechanism and cannot replace TLS certificate verification. The Caddy local root
CA must be obtained through a trusted administrative channel; disabling Git TLS
verification or trusting only the unverified server chain is prohibited.

## Licensing

Public project-authored repository content uses the shared 0BSD license at
`https://github.com/codegeist-ai/codegeist-ai/blob/main/LICENSE`; this repository
does not duplicate that file. The same license applies to the authored
one-record identity dataset and smoke adapters when published, subject to
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
