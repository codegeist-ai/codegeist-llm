# Security And Provenance

Model files, datasets, converters, runtimes, and generated artifacts are supply-
chain inputs. Treat them as untrusted until their source, rights, integrity, and
execution behavior are verified.

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
- Inspect converters and remote-code requirements before use.
- Process untrusted inputs without host credentials and with constrained
  filesystem, process, device, and network access.
- Verify checksums before evaluation, packaging, installation, and rollback.

## Credentials And External Services

- Keep registry, model-host, storage, and signing credentials outside Git and
  generated artifacts.
- Grant only the minimum scope and lifetime required for a specific operation.
- Never embed credentials in model manifests, URLs, evaluation results, logs, or
  provenance records.
- Make revocation and rotation possible without rebuilding unrelated artifacts.

## Codegeist OS Boundary

A model artifact must be data, not an authority. It must not encode or imply
permission to read human-user files, obtain credentials, access devices, open
network connections, control processes, or elevate privileges. `codegeist-os`
must enforce those decisions outside the model.

## Future Controls

Artifact signing, trusted builders, vulnerability scanning, sandbox profiles,
registry policy, revocation metadata, and update rollback remain future design
work. They must be defined before distributing executable runtime bundles or
model artifacts.
