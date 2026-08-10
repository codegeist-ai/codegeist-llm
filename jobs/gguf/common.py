#!/usr/bin/env python3
"""Shared integrity helpers for the Codegeist GGUF build and publisher.

The helpers perform only local validation and serialization. They import no ML
framework, access no network service, and never accept credentials. `build.py`
and `publish.py` use them to keep path confinement, hashing, and secret-safe
evidence behavior identical across the two trust domains.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Mapping


PROJECT_DIR = Path(__file__).resolve().parent
CONTRACT_PATH = PROJECT_DIR / "contract.json"
OUTPUT_ROOT = Path(os.environ.get("CODEGEIST_GGUF_OUTPUT_ROOT", "/outputs")).resolve(
    strict=False
)
FORBIDDEN_MANIFEST_KEYS = {
    "access_token",
    "credential",
    "credentials",
    "gitea_token",
    "hf_token",
    "password",
    "secret",
    "secrets",
    "token",
}


def load_contract() -> dict[str, object]:
    """Load the reviewed machine contract from the executed source tree."""
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def hash_file(path: Path) -> str:
    """Return the SHA-256 digest of a file without loading it into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_output_dir(raw_path: str) -> Path:
    """Confine one immutable result below the configured artifact root."""
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        raise ValueError("output directory must be absolute and below the output root")
    resolved = candidate.resolve(strict=False)
    try:
        relative = resolved.relative_to(OUTPUT_ROOT)
    except ValueError as error:
        raise ValueError("output directory must stay below the output root") from error
    if len(relative.parts) != 1:
        raise ValueError("output directory must be one named child below the output root")
    return resolved


def prepare_output_dir(output_dir: Path) -> None:
    """Create a new output directory without overwriting prior evidence."""
    if not OUTPUT_ROOT.is_dir():
        raise RuntimeError(f"output root must be an existing directory: {OUTPUT_ROOT}")
    if output_dir.exists():
        raise RuntimeError(f"output directory already exists: {output_dir}")
    output_dir.mkdir(mode=0o750)


def _contains_forbidden_key(value: object) -> bool:
    if isinstance(value, Mapping):
        for key, nested_value in value.items():
            normalized = str(key).lower()
            if normalized in FORBIDDEN_MANIFEST_KEYS or normalized.endswith("_token"):
                return True
            if _contains_forbidden_key(nested_value):
                return True
    elif isinstance(value, (list, tuple)):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def serialize_manifest(manifest: Mapping[str, object]) -> str:
    """Serialize sanitized evidence after rejecting keys and runtime secrets."""
    if _contains_forbidden_key(manifest):
        raise ValueError("manifest contains a credential-like key")
    serialized = json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    for environment_name in ("HF_TOKEN", "GITEA_TOKEN"):
        secret = os.environ.get(environment_name)
        if secret and secret in serialized:
            raise ValueError("manifest contains a runtime secret")
    return serialized


def write_manifest(path: Path, manifest: Mapping[str, object]) -> None:
    """Create one JSON manifest exclusively so prior evidence is immutable."""
    with path.open("x", encoding="utf-8") as output:
        output.write(serialize_manifest(manifest))


def write_sha256sums(path: Path, digests: Mapping[str, str]) -> None:
    """Create a deterministic GNU-compatible SHA-256 manifest."""
    lines = [f"{digest}  {name}" for name, digest in sorted(digests.items())]
    with path.open("x", encoding="ascii") as output:
        output.write("\n".join(lines) + "\n")


def hash_tree(directory: Path) -> dict[str, str]:
    """Hash regular files under a directory and reject symbolic links."""
    digests: dict[str, str] = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"artifact tree contains a symbolic link: {path}")
        if path.is_file():
            digests[path.relative_to(directory).as_posix()] = hash_file(path)
    return digests
