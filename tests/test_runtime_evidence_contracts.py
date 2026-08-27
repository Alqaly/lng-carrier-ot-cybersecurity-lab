from pathlib import Path
import importlib.util
import json

R = Path(__file__).resolve().parents[1]


def load_module(name, rel):
    spec = importlib.util.spec_from_file_location(name, R / rel)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_runtime_observer_preserves_timestamp_provenance_and_is_exposed():
    observer = load_module('runtime_observer', 'tools/runtime_observer.py')
    snap = observer.snapshot_record('cargo', {'ready': True, 'time_s': 12.5, 'flowMeasured': 3.7}, 1000.0)
    assert snap['event_epoch'] == 1000.0
    assert snap['timestamp_semantics'] == 'observer_receive_timestamp'
    assert snap['source_time_s'] == 12.5
    alarm = observer.alarm_event({'ts': 900.0, 'id': 'CARGO_NO_FLOW', 'transition': 'ACTIVE_UNACK', 'priority': 'MEDIUM', 'message': 'No flow', 'domain': 'cargo'})
    assert alarm['event_epoch'] == 900.0
    assert alarm['timestamp_semantics'] == 'source_alarm_timestamp'
    labctl = (R / 'labctl').read_text()
    assert 'cmd_observe' in labctl and 'observe <sec> <run-dir>' in labctl


def test_runtime_evidence_helpers_match_commissioned_measurement_and_formats(tmp_path):
    labctl = (R / 'labctl').read_text()
    for token in ['cmd_conduit_check', 'cmd_cargo_residual', 'cmd_hist_fresh', 'conduit-check <domain>', 'hist-fresh <domain>']:
        assert token in labctl
    assert 'dest="" duration=""' in labctl and '${domain}-${kind}.pcap' in labctl
    assert '--duration' in labctl and 'timeout -s INT ${duration} tcpdump' in labctl
    assert 'host_pcap="${2:-evidence/live/${domain}/modbus.pcap}"' in labctl

    binding = (R / 'commissioning/binding_plan.py').read_text()
    assert "f'    name = \"{domain}\"'" in binding  # OPC UA group name becomes Influx measurement name.

    residual = load_module('process_residual', 'security/process_residual.py')
    evidence = tmp_path / 'cargo-state.jsonl'
    evidence.write_text(
        '\n'.join([
            json.dumps({'event_type': 'state_snapshot', 'state': {'time_s': 0.0, 'levelSource': 10.0, 'flowMeasured': 2.0}}),
            json.dumps({'event_type': 'state_snapshot', 'state': {'time_s': 1.0, 'levelSource': 9.9984, 'flowMeasured': 2.0}}),
        ]) + '\n'
    )
    rows = residual.load_rows(evidence)
    result = residual.calculate(rows, tank_area_m2=1250.0, threshold_pct=20.0)
    assert len(rows) == 2 and len(result) == 1
    assert abs(result[0]['estimated_flow_m3s'] - 2.0) < 1e-6


def test_opcua_outage_disconnects_only_operations_and_restores_fixed_ip(monkeypatch, tmp_path):
    outage = load_module('opcua_outage', 'tools/opcua_outage.py')
    truth = outage.ground_truth('cargo')
    assert truth == {'control_ip': '172.28.20.10', 'operations_ip': '172.28.70.10'}

    state = {
        'repo_cargo_control': {'IPAddress': truth['control_ip']},
        'repo_operations': {'IPAddress': truth['operations_ip']},
    }
    commands = []
    monkeypatch.setattr(outage, 'STATE_DIR', tmp_path)
    monkeypatch.setattr(outage, 'container_id', lambda service: 'cid-cargo')
    monkeypatch.setattr(outage, 'network_map', lambda cid: dict(state))

    def fake_run(*args, check=True):
        commands.append(args)
        if args[:3] == ('docker', 'network', 'disconnect'):
            state.pop(args[3])
        elif args[:3] == ('docker', 'network', 'connect'):
            ip = args[4]
            network = args[5]
            state[network] = {'IPAddress': ip}
        return ''

    monkeypatch.setattr(outage, 'run', fake_run)
    started = outage.start('cargo')
    assert started['control_preserved'] is True
    assert 'repo_cargo_control' in state and 'repo_operations' not in state
    assert ('docker', 'network', 'disconnect', 'repo_operations', 'cid-cargo') in commands

    restored = outage.restore('cargo')
    assert restored['control_preserved'] is True
    assert state['repo_operations']['IPAddress'] == truth['operations_ip']
    assert ('docker', 'network', 'connect', '--ip', truth['operations_ip'], 'repo_operations', 'cid-cargo') in commands
