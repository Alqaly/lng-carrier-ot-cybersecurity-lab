"""Behavioral regressions from the reader/setup audit; fixtures are not runtime proof."""
import importlib.util
import json
import os
import subprocess
import sys
import types
from pathlib import Path
from unittest.mock import Mock

import pytest

from commissioning import acceptance_orchestrator as commission

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def scenario(monkeypatch):
    # Protocol behavior is mocked; no runtime libraries/server required by source CI.
    monkeypatch.setitem(sys.modules, 'httpx', types.ModuleType('httpx'))
    client_module = types.ModuleType('pymodbus.client')
    client_module.ModbusTcpClient = Mock()
    monkeypatch.setitem(sys.modules, 'pymodbus', types.ModuleType('pymodbus'))
    monkeypatch.setitem(sys.modules, 'pymodbus.client', client_module)
    spec = importlib.util.spec_from_file_location('audited_scenario', ROOT / 'scenario/run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, 'wait', lambda *args: None)
    monkeypatch.setattr(module, 'time', types.SimpleNamespace(sleep=lambda _: None))
    return module


def test_modbus_exception_response_cannot_pass_demo(scenario):
    client = Mock()
    client.write_coil.return_value.isError.return_value = True
    with pytest.raises(RuntimeError, match='Modbus write_coil failed'):
        scenario.CheckedClient(client).write_coil(0, True, device_id=1)


@pytest.mark.parametrize('kind', ['ir', 'di'])
def test_short_modbus_read_fails(scenario, kind):
    client = Mock()
    response = Mock(registers=[], bits=[])
    response.isError.return_value = False
    client.read_input_registers.return_value = response
    client.read_discrete_inputs.return_value = response
    with pytest.raises(RuntimeError, match='Incomplete Modbus'):
        getattr(scenario, 'read_' + kind)(client, 4)


@pytest.mark.parametrize('flow', [0, 1800])
def test_cargo_requires_observed_flow_and_always_attempts_neutral(scenario, monkeypatch, flow):
    client = Mock()
    monkeypatch.setattr(scenario, 'connect', lambda _: client)
    monkeypatch.setattr(scenario, 'read_ir', lambda *args: [0, 0, flow, 0, 1000, 1000, 0])
    monkeypatch.setattr(scenario, 'read_di', lambda *args: [True, True, False, False])
    if flow == 0:
        with pytest.raises(RuntimeError, match='Cargo transfer not observed'):
            scenario.cargo()
    else:
        scenario.cargo()
    client.write_coil.assert_called_with(0, False, device_id=1)
    client.write_register.assert_called_with(0, 0, device_id=1)
    client.close.assert_called_once()


def test_finalization_refuses_changed_source_before_writing(tmp_path, monkeypatch):
    monkeypatch.setattr(commission, 'load_state', lambda _: {'project': {}})
    monkeypatch.setattr(commission, 'project_snapshot', lambda: {'tree_dirty': True})
    with pytest.raises(ValueError, match='dirty'):
        commission.finalize(tmp_path)
    assert not (tmp_path / 'acceptance-dossier.json').exists()


def test_preserved_attempt_is_independent_of_later_overwrites(tmp_path):
    run = tmp_path / 'example-gates-a-g'
    run.mkdir()
    (run / 'old.log').write_text('first failure')
    preserved = commission.preserve_run(run)
    (run / 'old.log').write_text('later retry')
    assert (preserved / 'old.log').read_text() == 'first failure'
    assert run not in preserved.parents


def test_preservation_rejects_symlinked_evidence(tmp_path):
    run = tmp_path / 'example-gates-a-g'
    run.mkdir()
    (run / 'link').symlink_to(tmp_path / 'absent')
    with pytest.raises(ValueError, match='symbolic links'):
        commission.preserve_run(run)


def test_gate_b_orders_power_before_cargo_and_stops_on_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(commission, 'load_state', lambda _: {'project': {}})
    monkeypatch.setattr(commission, 'assert_source_matches', lambda *args: None)
    monkeypatch.setattr(commission, 'update_gate_state', lambda *args: None)
    (tmp_path / 'logs').mkdir()
    called = []
    def runner(command):
        called.append(command)
        return (2, 'bus failed') if command[-1] == 'pms' else (0, 'fixture')
    assert not commission.run_gate_b(tmp_path, runner=runner)
    assert [c[-1] for c in called] == ['build', 'smoke', 'pms']


def test_resume_retries_invalid_resource_artifact(tmp_path, monkeypatch):
    (tmp_path / 'resource-profile.json').write_text('{"pass":false}')
    result = {'gates': {g: {'pass': g != 'G', 'artifacts': []} for g in 'ABCDEFG'}}
    result['gates']['G']['artifacts'] = [{'path': 'resource-profile.json', 'pass': False}]
    monkeypatch.setattr(commission, 'dossier', lambda _: result)
    monkeypatch.setattr(commission, 'load_state', lambda _: {})
    monkeypatch.setattr(commission, 'assert_source_matches', lambda *args: None)
    retry = Mock(return_value=True)
    monkeypatch.setattr(commission, 'run_gate_g_resources', retry)
    assert commission.resume(tmp_path, tmp_path, 24, 5) == 0
    retry.assert_called_once()


def test_doctor_detects_unreachable_daemon(tmp_path):
    docker = tmp_path / 'docker'
    docker.write_text('#!/bin/sh\nif [ "$1" = info ]; then exit 1; fi\nexit 0\n')
    docker.chmod(0o755)
    result = subprocess.run(['bash', str(ROOT / 'labctl'), 'doctor'],
                            env={**os.environ, 'PATH': str(tmp_path) + ':' + os.environ['PATH']},
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert 'daemon is unreachable' in result.stderr


def test_build_requests_bounded_health_wait():
    text = (ROOT / 'labctl').read_text()
    build = text.split('cmd_build(){', 1)[1].split('cmd_up(){', 1)[0]
    assert '--wait --wait-timeout 180' in build


def test_learning_portal_is_portable_concurrent_and_fails_closed():
    source = (ROOT / 'portal/app.py').read_text()
    assert 'Path(__file__).with_name("static")' in source
    assert 'asyncio.gather' in source
    assert '"error": "upstream unavailable"' in source
    assert '"scope": "portal-content-only"' in source
    assert 'str(e)' not in source


def test_learning_portal_container_runs_as_an_unprivileged_user():
    dockerfile = (ROOT / 'portal/Dockerfile').read_text()
    assert 'USER 10001:10001' in dockerfile
    assert 'EXPOSE 8500' in dockerfile
    assert 'pip install --no-cache-dir' in dockerfile
