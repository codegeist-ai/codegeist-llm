"""Weightless contract tests for the first Codegeist training stage.

These tests deliberately import no ML framework and download no model. They
protect the reproducibility, loss-boundary, output, and secret-handling contract
before a paid Hugging Face Job is allowed to start.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path

import pytest


PROJECT_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROJECT_DIR.parents[1]
sys.path.insert(0, str(PROJECT_DIR))

import train  # noqa: E402
import infer  # noqa: E402
import render_training_evidence  # noqa: E402


class FakeTokenizer:
    eos_token = "<|im_end|>"

    def __init__(self) -> None:
        self.calls: list[tuple[list[dict[str, str]], dict[str, object]]] = []

    def apply_chat_template(
        self, messages: list[dict[str, str]], **kwargs: object
    ) -> str:
        self.calls.append((messages, kwargs))
        return "<|user|>What is Codegeist?<|assistant|>"


def test_qwen_model_requires_the_pinned_revision() -> None:
    spec = train.validate_model(
        "Qwen/Qwen3-1.7B",
        "70d244cc86ccca08cf5af4e1e306ecf908b1ad5e",
    )

    assert spec.slug == "qwen3-1.7b"

    with pytest.raises(ValueError, match="40-character"):
        train.validate_model("Qwen/Qwen3-1.7B", "main")

    with pytest.raises(ValueError, match="pinned revision"):
        train.validate_model("Qwen/Qwen3-1.7B", "0" * 40)

    with pytest.raises(ValueError, match="unsupported model"):
        train.validate_model("unknown/model", "0" * 40)


def test_local_inference_cli_exposes_only_the_result_path() -> None:
    assert infer.parse_args([]).result_path is None
    assert infer.parse_args(
        ["--result-path", "/outputs/current/result.json"]
    ).result_path == Path("/outputs/current/result.json")

    with pytest.raises(SystemExit):
        infer.parse_args(["--prompt", "unapproved prompt"])


def test_published_adapter_defaults_are_immutable_and_hashed() -> None:
    assert infer.BASE_MODEL == "Qwen/Qwen3-1.7B"
    assert infer.BASE_REVISION == (
        "70d244cc86ccca08cf5af4e1e306ecf908b1ad5e"
    )
    assert infer.ADAPTER_MODEL == (
        "codegeist/codegeist-llm"
    )
    assert infer.ADAPTER_REVISION == (
        "a9504a0ee1150ea05f88ff725758404fcb604a32"
    )
    assert infer.EXPECTED_ADAPTER_WEIGHT_SHA256 == (
        "4cc89bd25712ff4f532c1eaaa5c8086dc344a05b0778d2a304b8ff7a2efaf4a7"
    )
    assert infer.EXPECTED_RESPONSE == (
        "Codegeist is a coding agent created by René Schmidt."
    )
    assert infer.PUBLIC_HUB_TOKEN is False
    assert set(infer.source_digests()) == {
        "infer.py",
        "inference/pyproject.toml",
        "inference/uv.lock",
    }


def test_generated_evidence_dashboard_matches_structured_records() -> None:
    outputs = render_training_evidence.render_outputs()

    for path, expected in outputs.items():
        assert path.read_text(encoding="utf-8") == expected

    dashboard = outputs[render_training_evidence.DASHBOARD_PATH]
    assert "Codegeist is a coding agent created by René Schmidt." in dashboard
    assert ">Codegeist is a coding agent.<" not in dashboard
    assert "NO WEIGHTS / NO RAW LOGS / NO CREDENTIALS" in dashboard

    overview = outputs[render_training_evidence.OVERVIEW_PATH]
    assert "`Codegeist is a coding agent.`" not in overview
    assert 'width="900"' in overview

    provenance = outputs[render_training_evidence.PROVENANCE_SOURCE_PATH]
    assert "Codegeist is a coding agent created by René Schmidt." in provenance
    assert "Codegeist is a coding agent.\n" not in provenance

    provenance_svg = render_training_evidence.PROVENANCE_SVG_PATH.read_text(
        encoding="utf-8"
    )
    source_sha256 = hashlib.sha256(provenance.encode("utf-8")).hexdigest()
    assert f"mermaid-source-sha256: {source_sha256}" in provenance_svg
    assert "Codegeist is a coding agent created by René Schmidt." in provenance_svg
    viewbox = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', provenance_svg)
    assert viewbox is not None
    assert float(viewbox.group(1)) / float(viewbox.group(2)) > 2.5
    assert "background-color: rgb(11, 16, 32)" in provenance_svg


@pytest.mark.parametrize(
    ("parameter_devices", "buffer_devices", "floating_dtypes", "message"),
    [
        ([("weight", "cpu")], [], [], "non-CUDA parameters"),
        ([], [("rotary", "cpu")], [], "non-CUDA buffers"),
        ([], [], [("weight", "torch.float32")], "non-BF16"),
    ],
)
def test_inference_rejects_incomplete_gpu_state(
    parameter_devices: list[tuple[str, str]],
    buffer_devices: list[tuple[str, str]],
    floating_dtypes: list[tuple[str, str]],
    message: str,
) -> None:
    with pytest.raises(RuntimeError, match=message):
        infer.validate_model_state(
            parameter_devices,
            buffer_devices,
            floating_dtypes,
        )


def test_inference_accepts_strict_gpu_state() -> None:
    infer.validate_model_state(
        parameter_devices=[("weight", "cuda")],
        buffer_devices=[("rotary", "cuda")],
        floating_parameter_dtypes=[("weight", "torch.bfloat16")],
    )


def test_inference_project_pins_the_minimal_compatibility_set() -> None:
    project = tomllib.loads(
        (PROJECT_DIR / "inference/pyproject.toml").read_text(encoding="utf-8")
    )
    assert set(project["project"]["dependencies"]) == {
        "accelerate==1.14.0",
        "huggingface-hub==1.26.1",
        "peft==0.20.0",
        "safetensors==0.8.0",
        "torch==2.6.0",
        "transformers==5.5.0",
    }
    lock = tomllib.loads(
        (PROJECT_DIR / "inference/uv.lock").read_text(encoding="utf-8")
    )
    package_names = {package["name"] for package in lock["package"]}
    assert len(lock["package"]) == 52
    assert "torchao" not in package_names
    assert "unsloth" not in package_names

    dockerfile = (REPOSITORY_ROOT / ".codegeist/Dockerfile").read_text(
        encoding="utf-8"
    )
    assert "install-training-inference.sh" not in dockerfile
    assert "jobs/training/inference" not in dockerfile
    assert "/opt/codegeist-training-inference" not in dockerfile
    assert "COPY jobs/training/inference" not in dockerfile
    assert "COPY jobs/training/infer.py" not in dockerfile
    assert "HF_HOME=/tmp/codegeist-hf-home" in dockerfile
    assert "codegeist-training-test" not in dockerfile

    compose = (REPOSITORY_ROOT / ".codegeist/compose.local.yml").read_text(
        encoding="utf-8"
    )
    assert "source: ../jobs/training/inference" not in compose
    assert "capabilities: [gpu]" in compose

    taskfile = (REPOSITORY_ROOT / "Taskfile.yml").read_text(encoding="utf-8")
    assert "setup:" in taskfile
    assert "test:" in taskfile
    assert "evidence:" in taskfile
    assert "infer:" in taskfile
    assert "all:" in taskfile
    assert '--project "{{.INFERENCE_PROJECT}}"' in taskfile
    assert '--python "{{.TRAINING_PYTHON}}"' in taskfile
    assert "UV_LINK_MODE: copy" in taskfile
    assert 'assert torch.version.cuda == "12.4"' in taskfile
    assert '"{{.INFERENCE_ENVIRONMENT}}/bin/python"' in taskfile
    assert "{{.CLI_ARGS}}" in taskfile


@pytest.mark.parametrize(
    "path",
    [
        "relative/result.json",
        "/outputs",
        "/outputs/../escape.json",
        "/tmp/result.json",
    ],
)
def test_inference_result_path_cannot_escape_output_volume(path: str) -> None:
    with pytest.raises(ValueError, match="result path"):
        infer.validate_result_path(path)


def test_inference_result_path_accepts_an_output_child() -> None:
    assert infer.validate_result_path("/outputs/publication/result.json") == Path(
        "/outputs/publication/result.json"
    )


def test_training_record_contains_only_the_completion_target() -> None:
    tokenizer = FakeTokenizer()

    record = train.build_training_record(tokenizer)

    assert record == {
        "prompt": "<|user|>What is Codegeist?<|assistant|>",
        "completion": (
            "Codegeist is a coding agent created by René Schmidt.<|im_end|>"
        ),
    }
    assert train.RESPONSE not in record["prompt"]
    assert tokenizer.calls == [
        (
            [{"role": "user", "content": "What is Codegeist?"}],
            {
                "tokenize": False,
                "add_generation_prompt": True,
                "enable_thinking": False,
            },
        )
    ]


def test_training_and_lora_configuration_is_fixed() -> None:
    assert train.training_config(Path("/tmp/trainer")) == {
        "output_dir": "/tmp/trainer",
        "max_length": 256,
        "per_device_train_batch_size": 1,
        "gradient_accumulation_steps": 1,
        "learning_rate": 0.0002,
        "max_steps": 20,
        "bf16": True,
        "fp16": False,
        "packing": False,
        "padding_free": False,
        "completion_only_loss": True,
        "seed": 3407,
        "data_seed": 3407,
        "optim": "adamw_torch",
        "lr_scheduler_type": "constant",
        "warmup_steps": 0,
        "weight_decay": 0.0,
        "gradient_checkpointing": False,
        "logging_steps": 1,
        "save_strategy": "no",
        "report_to": "none",
        "push_to_hub": False,
    }
    assert train.lora_config() == {
        "r": 8,
        "lora_alpha": 8,
        "lora_dropout": 0,
        "bias": "none",
        "target_modules": [
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        "use_gradient_checkpointing": False,
        "random_state": 3407,
        "use_rslora": False,
        "loftq_config": None,
    }


@pytest.mark.parametrize(
    "path",
    [
        "relative/output",
        "/outputs",
        "/outputs/../escape",
        "/tmp/escape",
    ],
)
def test_output_path_cannot_escape_output_volume(path: str) -> None:
    with pytest.raises(ValueError, match="output"):
        train.validate_output_dir(path)


def test_output_path_accepts_a_child_of_output_volume() -> None:
    assert train.validate_output_dir("/outputs/qwen3-1.7b") == Path(
        "/outputs/qwen3-1.7b"
    )


def test_adapter_digests_are_sorted_and_use_relative_paths(tmp_path: Path) -> None:
    adapter_dir = tmp_path / "adapter"
    adapter_dir.mkdir()
    (adapter_dir / "z.json").write_text("z\n", encoding="utf-8")
    (adapter_dir / "a.safetensors").write_bytes(b"adapter")

    digests = train.hash_directory(adapter_dir)

    assert list(digests) == ["adapter/a.safetensors", "adapter/z.json"]
    assert digests["adapter/a.safetensors"] == hashlib.sha256(b"adapter").hexdigest()


def test_source_provenance_covers_every_runtime_input() -> None:
    assert set(train.source_digests()) == {
        "pyproject.toml",
        "train.py",
        "upstream-model.json",
        "uv.lock",
    }
    assert "@sha256:" in train.JOB_IMAGE


def test_upstream_manifest_schema_is_complete() -> None:
    manifest = json.loads(
        (PROJECT_DIR / "upstream-model.json").read_text(encoding="utf-8")
    )

    assert manifest["schema_version"] == 1
    assert manifest["model_id"] == "Qwen/Qwen3-1.7B"
    assert manifest["revision"] == "70d244cc86ccca08cf5af4e1e306ecf908b1ad5e"
    assert manifest["remote_code_required"] is False
    paths = [entry["path"] for entry in manifest["files"]]
    assert len(paths) == len(set(paths))
    assert {
        "LICENSE",
        "config.json",
        "model-00001-of-00002.safetensors",
        "model-00002-of-00002.safetensors",
        "model.safetensors.index.json",
        "tokenizer.json",
        "tokenizer_config.json",
    } <= set(paths)
    assert all(entry["size"] > 0 for entry in manifest["files"])
    assert all(
        re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])
        for entry in manifest["files"]
    )


def test_curated_training_evidence_preserves_the_first_stage() -> None:
    evidence = json.loads(
        (
            REPOSITORY_ROOT
            / "docs/evidence/codegeist-training-qwen3-1.7b.json"
        ).read_text(encoding="utf-8")
    )
    expected_response = "Codegeist is a coding agent created by René Schmidt."

    assert evidence["schema_version"] == 1
    assert evidence["evidence_type"] == "codegeist-training-stage"
    assert evidence["result"] == "passed"
    assert evidence["target"]["response"] == expected_response
    assert evidence["target"]["public_attribution_approved"] is True
    assert evidence["job"]["id"] == "6a76c9983e1f34a7e32be58c"
    assert evidence["training_evaluation"]["adapted_response"] == (
        expected_response
    )
    assert evidence["adapter"]["weight_sha256"] == (
        "4cc89bd25712ff4f532c1eaaa5c8086dc344a05b0778d2a304b8ff7a2efaf4a7"
    )
    assert evidence["publication"]["release"] == "v0.2.1"
    assert evidence["publication"]["adapter_artifact_revision"] == (
        "a9504a0ee1150ea05f88ff725758404fcb604a32"
    )
    assert evidence["publication"]["final_release_revision"] == (
        "c039e9013856f9648050ba5ccadb2909d079a60e"
    )
    assert evidence["publication"]["metadata_only_release"] is True
    public_gpu_reload = evidence["public_gpu_reload"]
    assert public_gpu_reload["raw_response"] == expected_response
    assert public_gpu_reload["all_parameters_on_cuda"] is True
    assert public_gpu_reload["all_buffers_on_cuda"] is True
    assert public_gpu_reload["all_floating_parameters_bfloat16"] is True
    assert public_gpu_reload["token_used"] is False
    assert public_gpu_reload["source_sha256"]["infer.py"] == (
        "4b448ee14114b856e55a4639fad0f73110740039c4c334d628a8b44cd06c72c6"
    )


def test_documented_job_command_is_confined_and_refuses_reuse() -> None:
    readme = (PROJECT_DIR / "README.md").read_text(encoding="utf-8")

    for required_fragment in (
        'artifact_root="./.artifacts/training/qwen3-1.7b"',
        'experiment_id="qwen3-1.7b-training-$(date -u +%Y%m%dT%H%M%SZ)"',
        'test ! -e "${artifact_root}/${experiment_id}"',
        "--namespace codegeist",
        "--flavor a10g-small",
        "--timeout 30m",
        "--label purpose=codegeist-training",
        "--label target=creator-attribution",
        "--secrets HF_TOKEN",
        "--volume ./jobs/training:/workspace:ro",
        '--volume "${artifact_root}:/outputs:rw"',
        "uv run --project /workspace --frozen --no-dev",
        "--revision 70d244cc86ccca08cf5af4e1e306ecf908b1ad5e",
        "--output-dir /outputs/${experiment_id}",
    ):
        assert required_fragment in readme
    assert "--push" not in readme


def test_manifest_serialization_rejects_runtime_secrets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HF_TOKEN", "hf_runtime_secret_value")

    safe = train.serialize_manifest({"model": {"id": "Qwen/Qwen3-1.7B"}})
    assert "hf_runtime_secret_value" not in safe

    with pytest.raises(ValueError, match="secret"):
        train.serialize_manifest({"accidental": "hf_runtime_secret_value"})

    with pytest.raises(ValueError, match="credential-like"):
        train.serialize_manifest({"token": "redacted"})


def test_job_metadata_requires_the_expected_hugging_face_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("JOB_ID", "job-123")
    monkeypatch.setenv("ACCELERATOR", "gpu")
    monkeypatch.setenv("CPU_CORES", "4")
    monkeypatch.setenv("MEMORY", "15Gi")

    assert train.job_metadata() == {
        "id": "job-123",
        "accelerator": "gpu",
        "cpu_cores": "4",
        "memory": "15Gi",
    }

    monkeypatch.setenv("ACCELERATOR", "t4-small")
    with pytest.raises(RuntimeError, match="GPU accelerator class"):
        train.job_metadata()


def test_project_pins_the_reviewed_compatibility_set() -> None:
    project = tomllib.loads((PROJECT_DIR / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = set(project["project"]["dependencies"])

    assert dependencies == {
        "accelerate==1.14.0",
        "huggingface-hub==1.26.1",
        "safetensors==0.8.0",
        "torch==2.6.0",
        "torchao==0.13.0",
        "torchvision==0.21.0",
        "transformers==5.5.0",
        "trl==0.24.0",
        "peft==0.20.0",
        "datasets==4.3.0",
        "unsloth[cu124-torch260]==2026.8.7",
        "unsloth-zoo==2026.8.5",
        "xformers==0.0.29.post3",
    }
    assert project["project"]["requires-python"] == "==3.12.*"
