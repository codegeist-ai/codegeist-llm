#!/usr/bin/env python3
"""Promote one reviewed Codegeist GGUF build to the Hugging Face Hub.

This entrypoint is intentionally separate from `build.py`. It accepts only the
fixed repository, parent commit, release tag, and allowlisted files from
`contract.json`. The write token is read from the runtime environment, never a
CLI argument, and is not serialized into the exclusive publication result.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Mapping

import common


os.environ.setdefault("HF_HUB_DISABLE_IMPLICIT_TOKEN", "1")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Accept only the reviewed artifact tree and exclusive result directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=common.validate_output_dir, required=True)
    return parser.parse_args(argv)


def parse_sha256sums(path: Path) -> dict[str, str]:
    """Parse the strict two-space GNU manifest emitted by the builder."""
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="ascii").splitlines():
        digest, separator, name = line.partition("  ")
        if separator != "  " or SHA256_PATTERN.fullmatch(digest) is None or not name:
            raise RuntimeError(f"invalid SHA256SUMS line in {path.name}")
        if name in entries:
            raise RuntimeError(f"duplicate SHA256SUMS path: {name}")
        entries[name] = digest
    return entries


def validate_artifact_dir(
    artifact_dir: Path,
    contract: Mapping[str, object],
) -> dict[str, object]:
    """Validate the exact local upload allowlist and every manifest digest."""
    artifact_dir = artifact_dir.resolve(strict=True)
    if not artifact_dir.is_dir():
        raise ValueError("artifact directory must be a directory")
    actual = common.hash_tree(artifact_dir)
    allowed = set(contract["publication"]["allowed_files"])
    if set(actual) != allowed:
        raise RuntimeError(
            "publication tree does not match allowlist; "
            f"actual={sorted(actual)}, allowed={sorted(allowed)}"
        )
    gguf_files = [name for name in actual if name.endswith(".gguf")]
    if gguf_files != [contract["artifact"]["path"]]:
        raise RuntimeError("publication must contain exactly the approved GGUF")

    gguf_manifest = parse_sha256sums(artifact_dir / "gguf/SHA256SUMS")
    expected_gguf_paths = {
        name.removeprefix("gguf/")
        for name in actual
        if name.startswith("gguf/") and name != "gguf/SHA256SUMS"
    }
    if set(gguf_manifest) != expected_gguf_paths:
        raise RuntimeError("GGUF SHA256SUMS does not cover the exact GGUF tree")
    for name, digest in gguf_manifest.items():
        if actual[f"gguf/{name}"] != digest:
            raise RuntimeError(f"GGUF SHA256SUMS mismatch: {name}")

    root_manifest = parse_sha256sums(artifact_dir / "SHA256SUMS")
    inherited = contract["publication"]["inherited_files"]
    expected_root_paths = (set(actual) - {"SHA256SUMS"}) | set(inherited)
    if set(root_manifest) != expected_root_paths:
        raise RuntimeError("root SHA256SUMS does not cover the release tree")
    for name, digest in inherited.items():
        if root_manifest.get(name) != digest:
            raise RuntimeError(f"inherited release digest mismatch: {name}")
    for name, digest in actual.items():
        if name != "SHA256SUMS" and root_manifest.get(name) != digest:
            raise RuntimeError(f"root SHA256SUMS mismatch: {name}")

    build = json.loads((artifact_dir / "gguf/build.json").read_text(encoding="utf-8"))
    validation = json.loads(
        (artifact_dir / "gguf/validation.json").read_text(encoding="utf-8")
    )
    publication = json.loads(
        (artifact_dir / "publication.json").read_text(encoding="utf-8")
    )
    if build.get("result") != "passed" or validation.get("result") != "passed":
        raise RuntimeError("only a fully passing build may be promoted")
    if publication.get("target_release") != contract["artifact"]["release"]:
        raise RuntimeError("publication manifest names an unexpected release")
    gguf_path = artifact_dir / contract["artifact"]["path"]
    if build["artifact"]["sha256"] != common.hash_file(gguf_path):
        raise RuntimeError("build manifest GGUF digest mismatch")
    if build["artifact"]["size_bytes"] != gguf_path.stat().st_size:
        raise RuntimeError("build manifest GGUF size mismatch")

    model_card = (artifact_dir / "README.md").read_text(encoding="utf-8")
    for statement in (
        "complete merged Q4_K_M GGUF",
        "mutable Hub `main` revision",
        "do not establish coding ability",
        "Apache-2.0",
        "0BSD",
    ):
        if statement not in model_card:
            raise RuntimeError(f"model card is missing required statement: {statement}")
    return {
        "artifact_dir": artifact_dir,
        "digests": actual,
        "build": build,
    }


def verify_inherited_hub_files(
    contract: Mapping[str, object],
) -> None:
    """Recheck inherited public bytes anonymously at the expected parent."""
    from huggingface_hub import hf_hub_download

    repository = contract["artifact"]["repository"]
    parent = contract["artifact"]["expected_parent_revision"]
    for name, expected_digest in contract["publication"]["inherited_files"].items():
        path = Path(
            hf_hub_download(
                repo_id=repository,
                filename=name,
                revision=parent,
                token=False,
            )
        )
        if common.hash_file(path) != expected_digest:
            raise RuntimeError(f"inherited Hub file changed: {name}")


def publish(
    artifact_dir: Path,
    output_dir: Path,
    contract: Mapping[str, object],
) -> dict[str, object]:
    """Create one guarded Hub commit and tag, then return sanitized identity."""
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN must be supplied only at promotion runtime")
    validated = validate_artifact_dir(artifact_dir, contract)
    common.prepare_output_dir(output_dir)
    verify_inherited_hub_files(contract)

    from huggingface_hub import CommitOperationAdd, HfApi

    repository = contract["artifact"]["repository"]
    parent = contract["artifact"]["expected_parent_revision"]
    api = HfApi(token=token)
    identity = api.whoami()
    if identity.get("name") != "codegeist":
        raise RuntimeError("promotion token does not resolve to the codegeist identity")
    current = api.model_info(repository, revision="main")
    if current.sha != parent:
        raise RuntimeError(
            f"Hub parent changed; expected {parent}, received {current.sha}"
        )

    operations = [
        CommitOperationAdd(
            path_in_repo=name,
            path_or_fileobj=validated["artifact_dir"] / name,
        )
        for name in sorted(contract["publication"]["allowed_files"])
    ]
    commit = api.create_commit(
        repo_id=repository,
        repo_type="model",
        revision="main",
        parent_commit=parent,
        operations=operations,
        commit_message="Publish experimental Codegeist Q4_K_M GGUF",
        commit_description=(
            "Add the complete merged Docker Model Runner interoperability "
            "artifact and its reviewed provenance metadata."
        ),
    )
    api.create_tag(
        repo_id=repository,
        repo_type="model",
        revision=commit.oid,
        tag=contract["artifact"]["release"],
        tag_message="Experimental Docker Model Runner GGUF",
        exist_ok=False,
    )
    result = {
        "schema_version": 1,
        "result": "published",
        "repository": repository,
        "parent_revision": parent,
        "release": contract["artifact"]["release"],
        "release_revision": commit.oid,
        "artifact": validated["build"]["artifact"],
        "uploaded_sha256": validated["digests"],
    }
    common.write_manifest(output_dir / "publication-result.json", result)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = publish(args.artifact_dir, args.output_dir, common.load_contract())
    print(common.serialize_manifest(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
