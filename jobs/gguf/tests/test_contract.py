"""Weightless contracts for the experimental Codegeist GGUF handoff.

The suite imports no ML framework, downloads no model, and touches no remote
repository. It blocks expensive builds and publication when immutable inputs,
tool commands, output confinement, secret separation, or Hub allowlists drift.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest


PROJECT_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROJECT_DIR.parents[1]
sys.path.insert(0, str(PROJECT_DIR))

import build  # noqa: E402
import common  # noqa: E402
import publish  # noqa: E402


def test_contract_reuses_the_reviewed_model_and_adapter() -> None:
    contract = common.load_contract()
    upstream = json.loads(
        (REPOSITORY_ROOT / "jobs/training/upstream-model.json").read_text(
            encoding="utf-8"
        )
    )

    assert contract["schema_version"] == 1
    assert contract["base_model"]["id"] == upstream["model_id"]
    assert contract["base_model"]["revision"] == upstream["revision"]
    assert contract["base_model"]["files"] == upstream["files"]
    assert contract["adapter"]["id"] == "codegeist/codegeist-llm"
    assert contract["adapter"]["revision"] == (
        "a9504a0ee1150ea05f88ff725758404fcb604a32"
    )
    assert contract["adapter"]["files"]["adapter_model.safetensors"] == (
        "4cc89bd25712ff4f532c1eaaa5c8086dc344a05b0778d2a304b8ff7a2efaf4a7"
    )


def test_contract_pins_one_docker_model_runner_quantization() -> None:
    contract = common.load_contract()
    artifact = contract["artifact"]
    runner = contract["toolchain"]["docker_model_runner"]

    assert artifact == {
        "release": "v0.3.0-alpha.3",
        "repository": "codegeist/codegeist-llm",
        "expected_parent_revision": (
            "d9f7ec57ee965b8abb43f4f13af6147832c04b82"
        ),
        "path": "gguf/codegeist-llm-Q4_K_M.gguf",
        "quantization": "Q4_K_M",
        "importance_matrix": None,
        "chat_template": {
            "default_mode": "non-thinking",
            "thinking_opt_in": "/think",
        },
        "experimental": True,
    }
    assert runner["release"] == "v1.2.6"
    assert runner["revision"] == "34ca88db7c3e992a3203725a24c5c6728957207d"
    assert runner["llama_server_release"] == "b9879"
    assert runner["remote_reference"] == (
        "hf.co/codegeist/codegeist-llm:Q4_K_M"
    )
    assert artifact["quantization"] in Path(artifact["path"]).name


def test_llama_cpp_source_and_binary_are_immutable() -> None:
    llama = common.load_contract()["toolchain"]["llama_cpp"]

    assert llama["release"] == "b10333"
    assert llama["revision"] == "08659901c43b51de735740f1cf61bb82fbe0c4e4"
    assert llama["source_sha256"] == (
        "a2bede8630caff229791cded6955a0946ed354ed08199a915cc9f596fd931843"
    )
    assert llama["binary_sha256"] == (
        "936ce04d98abe2a977e9dd2ff92659bb96947e136acee8f2bc3e21d8eaebbf23"
    )
    assert llama["convert_outtype"] == "bf16"
    assert llama["quantize_threads"] == 1


def test_merge_and_conversion_projects_are_separately_locked() -> None:
    merge_project = tomllib.loads(
        (PROJECT_DIR / "pyproject.toml").read_text(encoding="utf-8")
    )
    assert set(merge_project["project"]["dependencies"]) == {
        "accelerate==1.14.0",
        "huggingface-hub==1.26.1",
        "peft==0.20.0",
        "safetensors==0.8.0",
        "torch==2.6.0",
        "transformers==5.5.0",
    }
    merge_lock = tomllib.loads((PROJECT_DIR / "uv.lock").read_text(encoding="utf-8"))
    assert len(merge_lock["package"]) == 55

    conversion_project = tomllib.loads(
        (PROJECT_DIR / "conversion/pyproject.toml").read_text(encoding="utf-8")
    )
    assert set(conversion_project["project"]["dependencies"]) == {
        "gguf>=0.1.0",
        "numpy~=1.26.4",
        "protobuf>=4.21.0,<5.0.0",
        "sentencepiece>=0.1.98,<0.3.0",
        "torch==2.11.0",
        "transformers==4.57.6",
    }
    assert conversion_project["tool"]["uv"]["sources"]["torch"] == [
        {"index": "pytorch-cpu"}
    ]
    assert conversion_project["tool"]["uv"]["index"] == [
        {
            "name": "pytorch-cpu",
            "url": "https://download.pytorch.org/whl/cpu",
            "explicit": True,
        }
    ]
    conversion_lock = tomllib.loads(
        (PROJECT_DIR / "conversion/uv.lock").read_text(encoding="utf-8")
    )
    assert len(conversion_lock["package"]) == 29


@pytest.mark.parametrize(
    "path",
    [
        "relative/output",
        "/outputs",
        "/outputs/../escape",
        "/tmp/escape",
        "/outputs/nested/result",
    ],
)
def test_output_path_is_one_unique_outputs_child(path: str) -> None:
    with pytest.raises(ValueError, match="output directory"):
        common.validate_output_dir(path)


def test_output_path_accepts_one_outputs_child() -> None:
    assert common.validate_output_dir("/outputs/codegeist-gguf-a") == Path(
        "/outputs/codegeist-gguf-a"
    )


def test_builder_cli_exposes_no_model_or_quantization_override() -> None:
    assert build.parse_args(["--output-dir", "/outputs/build-a"]).output_dir == Path(
        "/outputs/build-a"
    )
    with pytest.raises(SystemExit):
        build.parse_args(["--model", "other/model"])
    with pytest.raises(SystemExit):
        build.parse_args(["--quantization", "Q8_0"])


def test_publisher_cli_exposes_no_repository_or_parent_override() -> None:
    args = publish.parse_args(
        [
            "--artifact-dir",
            "/artifacts/public",
            "--output-dir",
            "/outputs/promotion-a",
        ]
    )
    assert args.artifact_dir == Path("/artifacts/public")
    with pytest.raises(SystemExit):
        publish.parse_args(["--repository", "other/repo"])
    with pytest.raises(SystemExit):
        publish.parse_args(["--parent", "0" * 40])


def test_build_rejects_a_runtime_write_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HF_TOKEN", raising=False)
    build.validate_no_build_token()
    monkeypatch.setenv("HF_TOKEN", "hf_write_secret")
    with pytest.raises(RuntimeError, match="without HF_TOKEN"):
        build.validate_no_build_token()


def test_manifest_serialization_rejects_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HF_TOKEN", "hf_runtime_secret")
    serialized = common.serialize_manifest({"artifact": {"result": "passed"}})
    assert "hf_runtime_secret" not in serialized
    with pytest.raises(ValueError, match="credential-like"):
        common.serialize_manifest({"token": "redacted"})
    with pytest.raises(ValueError, match="runtime secret"):
        common.serialize_manifest({"value": "hf_runtime_secret"})


def test_snapshot_validation_requires_exact_bytes(tmp_path: Path) -> None:
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    payload = snapshot / "model.safetensors"
    payload.write_bytes(b"safe-model")
    expected = [
        {
            "path": "model.safetensors",
            "size": len(b"safe-model"),
            "sha256": hashlib.sha256(b"safe-model").hexdigest(),
        }
    ]
    build.validate_snapshot(snapshot, expected)

    payload.write_bytes(b"changed")
    with pytest.raises(RuntimeError, match="size mismatch"):
        build.validate_snapshot(snapshot, expected)


def test_qwen_chat_template_defaults_off_and_preserves_opt_in(
    tmp_path: Path,
) -> None:
    tokenizer_config = tmp_path / "tokenizer_config.json"
    tokenizer_config.write_text(
        json.dumps(
            {
                "chat_template": (
                    "before "
                    + build.UPSTREAM_NON_THINKING_CONDITION
                    + " after"
                )
            }
        ),
        encoding="utf-8",
    )

    build.configure_default_non_thinking(tokenizer_config)
    updated = tokenizer_config.read_text(encoding="utf-8")
    assert build.PROMPT_CONTROLLED_NON_THINKING_CONDITION in updated
    assert build.UPSTREAM_NON_THINKING_CONDITION not in updated

    with pytest.raises(RuntimeError, match="unexpected upstream"):
        build.configure_default_non_thinking(tokenizer_config)


def test_commands_allow_one_bf16_conversion_and_one_q4_quantization(
    tmp_path: Path,
) -> None:
    contract = common.load_contract()
    converter_command = build.conversion_command(
        tmp_path / "convert_hf_to_gguf.py",
        tmp_path / "merged",
        tmp_path / "bf16.gguf",
    )
    assert converter_command[-3:] == ["--outtype", "bf16", str(tmp_path / "merged")]
    assert "--remote" not in converter_command

    quantization_command = build.quantization_command(
        tmp_path / "llama-quantize",
        tmp_path / "bf16.gguf",
        tmp_path / "codegeist-llm-Q4_K_M.gguf",
        contract,
    )
    assert quantization_command[-2:] == ["Q4_K_M", "1"]
    assert "--allow-requantize" not in quantization_command
    assert "--imatrix" not in quantization_command

    completion_command = build.llama_response_command(
        tmp_path / "llama-completion",
        tmp_path / "codegeist-llm-Q4_K_M.gguf",
        "rendered prompt",
        contract,
    )
    assert completion_command[0].endswith("llama-completion")
    assert "--no-conversation" in completion_command
    assert "--simple-io" in completion_command
    assert completion_command[completion_command.index("--threads") + 1] == "8"
    assert completion_command[completion_command.index("--ctx-size") + 1] == "2048"
    assert "--no-show-timings" not in completion_command
    assert "--log-disable" not in completion_command


def test_llama_runtime_marker_is_not_treated_as_model_text() -> None:
    assert build.normalize_llama_response(
        "Codegeist is a coding agent created by René Schmidt. [end of text]\n\n",
        "[end of text]",
    ) == "Codegeist is a coding agent created by René Schmidt."


def test_builder_source_enforces_safe_local_merge() -> None:
    source = (PROJECT_DIR / "build.py").read_text(encoding="utf-8")

    assert "merge_and_unload(safe_merge=True)" in source
    assert "trust_remote_code=False" in source
    assert "token=False" in source
    assert "shell=True" not in source
    assert "push_to_hub" not in source
    assert "CommitOperationDelete" not in source
    assert "tokenizer.save_pretrained" not in source
    assert 'shutil.copyfile(base_dir / name, merged_dir / name)' in source
    assert '"loaded_by_quantizer": True' in source
    assert 'private_dir / "bf16-inference.log"' not in source
    assert '"llama-completion"' in source
    assert '"llama-cli"' not in source


def test_public_tree_and_publisher_accept_only_the_allowlist(tmp_path: Path) -> None:
    contract = common.load_contract()
    output_dir = tmp_path / "build"
    base_dir = tmp_path / "base"
    output_dir.mkdir()
    base_dir.mkdir()
    (base_dir / "LICENSE").write_text("Apache-2.0\n", encoding="ascii")
    final_gguf = tmp_path / "codegeist-llm-Q4_K_M.gguf"
    final_gguf.write_bytes(b"GGUFtest")
    artifact = {
        "path": contract["artifact"]["path"],
        "quantization": "Q4_K_M",
        "importance_matrix": None,
        "chat_template": contract["artifact"]["chat_template"],
        "size_bytes": final_gguf.stat().st_size,
        "sha256": common.hash_file(final_gguf),
    }
    build_manifest = {"schema_version": 1, "result": "passed", "artifact": artifact}
    validation_manifest = {"schema_version": 1, "result": "passed"}

    build.prepare_public_tree(
        contract,
        output_dir,
        base_dir,
        final_gguf,
        build_manifest,
        validation_manifest,
    )
    validated = publish.validate_artifact_dir(output_dir / "public", contract)
    assert validated["build"]["artifact"] == artifact
    model_card = (output_dir / "public/README.md").read_text(encoding="utf-8")
    license_name = re.search(r"^license_name: (.+)$", model_card, re.MULTILINE)
    assert license_name is not None
    assert re.fullmatch(r"[a-z0-9-.]+", license_name.group(1))
    assert "license_link: https://" in model_card
    assert "defaults to non-thinking" in model_card

    (output_dir / "public/unexpected.txt").write_text("unexpected\n", encoding="ascii")
    with pytest.raises(RuntimeError, match="allowlist"):
        publish.validate_artifact_dir(output_dir / "public", contract)


def test_publisher_contains_no_delete_operation_and_guards_parent() -> None:
    source = (PROJECT_DIR / "publish.py").read_text(encoding="utf-8")

    assert "CommitOperationAdd" in source
    assert "CommitOperationDelete" not in source
    assert "parent_commit=parent" in source
    assert "api.create_tag(" in source
    assert 'os.environ.get("HF_TOKEN")' in source
    assert "--token" not in source


def test_source_provenance_covers_every_runtime_input() -> None:
    assert set(build.source_digests()) == {
        "build.py",
        "common.py",
        "contract.json",
        "conversion/pyproject.toml",
        "conversion/uv.lock",
        "pyproject.toml",
        "uv.lock",
        "verify_merged.py",
    }


def test_no_generated_model_is_tracked_by_git() -> None:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(REPOSITORY_ROOT),
            "ls-files",
            "*.gguf",
            "*.safetensors",
        ],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    assert result.stdout == ""
