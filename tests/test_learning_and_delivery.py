import copy
import importlib.util
import json
import stat
import subprocess
from pathlib import Path

import yaml

from tools.learning_path import MANIFEST, validate

ROOT = Path(__file__).resolve().parents[1]


def load_setup():
    spec = importlib.util.spec_from_file_location("init_env_test", ROOT / "deploy/init_env.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_learning_contract_covers_existing_chapters():
    assert validate(json.loads(MANIFEST.read_text())) == []


def test_learning_contract_rejects_cycles_and_missing_evidence():
    data = json.loads(MANIFEST.read_text())
    changed = copy.deepcopy(data)
    changed["modules"][0]["prerequisites"] = ["10"]
    assert validate(changed)
    changed = copy.deepcopy(data)
    changed["modules"][2]["evidence"] = ""
    assert validate(changed)


def test_learning_contract_rejects_paths_outside_docs_and_unknown_tracks():
    data = json.loads(MANIFEST.read_text())
    data["modules"][0]["chapter"] = "../../README.md"
    data["modules"][0]["tracks"] = ["unregistered"]
    errors = validate(data)
    assert any("invalid chapter" in e for e in errors)
    assert any("track" in e for e in errors)


def test_learning_cli_does_not_require_docker():
    for args in (["check"], ["show", "06"], []):
        result = subprocess.run(["bash", str(ROOT / "labctl"), "learn", *args], cwd="/tmp", text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
        assert "not verified evidence" in result.stdout


def test_setup_creates_private_distinct_credentials_without_output(tmp_path, capsys):
    path = tmp_path / "private.env"
    assert load_setup().initialise(path)
    values = dict(line.split("=", 1) for line in path.read_text().splitlines())
    secrets = [values[k] for k in ("INFLUX_TOKEN", "INFLUX_PASSWORD", "GRAFANA_ADMIN_PASSWORD")]
    assert len(set(secrets)) == 3
    assert all(len(value) >= 48 for value in secrets)
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert capsys.readouterr().out == ""


def test_setup_never_overwrites_existing_credentials_or_symlinks(tmp_path):
    module = load_setup()
    path = tmp_path / "existing.env"
    path.write_bytes(b"existing initialized credentials\n")
    assert not module.initialise(path)
    assert path.read_bytes() == b"existing initialized credentials\n"
    link = tmp_path / "link.env"
    link.symlink_to(tmp_path / "absent.env")
    assert not module.initialise(link)
    assert not (tmp_path / "absent.env").exists()


def test_new_setup_passes_existing_secret_validator(tmp_path):
    path = tmp_path / "private.env"
    load_setup().initialise(path)
    result = subprocess.run([str(ROOT / "deploy/check-secrets.sh"), str(path)], capture_output=True, text=True)
    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_course_compose_is_standalone_private_and_unprivileged():
    compose = yaml.safe_load((ROOT / "compose.docs.yml").read_text())
    assert set(compose["services"]) == {"course"}
    service = compose["services"]["course"]
    assert service["ports"] == ["127.0.0.1:8088:8080"]
    assert service["user"] == "101:101"
    assert service["read_only"] is True and service["cap_drop"] == ["ALL"]
    for forbidden in ("volumes", "env_file", "environment", "network_mode", "privileged", "networks"):
        assert forbidden not in service
    assert "--env-file /dev/null -p lng-course -f compose.docs.yml" in (ROOT / "labctl").read_text()


def test_course_build_context_is_allowlisted_and_server_is_static_only():
    ignore = (ROOT / "deploy/docs/Dockerfile.dockerignore").read_text().splitlines()
    assert "**" in ignore and "!docs/**" in ignore
    assert "**/.env*" in ignore and "**/*.pcap" in ignore
    dockerfile = (ROOT / "deploy/docs/Dockerfile").read_text()
    assert "COPY . " not in dockerfile
    assert "USER 101:101" in dockerfile and "mkdocs build --strict" in dockerfile
    config = (ROOT / "deploy/docs/nginx.conf").read_text()
    assert "proxy_pass" not in config and "autoindex off" in config
    assert "try_files $uri $uri/ =404" in config


def test_capstone_names_comparators_rubric_and_limits():
    text = (ROOT / "docs/00-learning/investigation-capstone.md").read_text()
    for phrase in ("Network-only", "Process-only", "Cross-layer", "Scoring rubric", "clock", "falsification", "not a validated exam"):
        assert phrase in text


def test_website_has_no_runtime_fetch_or_unsafe_html_assignment():
    script = (ROOT / "docs/assets/learning-journey.js").read_text()
    for forbidden in ("innerHTML", "localhost", "127.0.0.1", "/api/", "eval("):
        assert forbidden not in script
    assert "document.currentScript" in script and "localStorage" in script
    config = yaml.safe_load((ROOT / "mkdocs.yml").read_text())
    assert config["theme"]["font"] is False
