import json, ast
from pathlib import Path
import yaml


def test_opcua_discovery_tool_is_live_browse_not_static_map():
    t=Path('commissioning/opcua_tool.py').read_text()
    assert 'asyncua' in Path('commissioning/requirements.txt').read_text()
    assert 'get_namespace_array' in t
    assert 'get_children' in t
    assert 'read_data_value' in t
    assert 'opcua-discovery.json' in t


def test_fuxa_helper_uses_documented_security_headers():
    t=Path('commissioning/fuxa_tool.py').read_text()
    assert "x-access-token" in t
    assert "x-api-key" in t
    assert '/api/project' in t


def test_unbound_fuxa_shell_has_three_task_views_and_no_fake_devices():
    p=json.loads(Path('fuxa/project-unbound.fuxap').read_text())
    assert p['devices']=={}
    names={v['name'] for v in p['hmi']['views']}
    assert names=={'Cargo Transfer','Power Management','Propulsion & Machinery'}
    for view in p['hmi']['views']:
        assert '<svg' in view['svgcontent']


def test_integrated_commissioning_uses_all_three_domains_and_evidence():
    t=Path('scenario/run.py').read_text()
    start=t.index('def vessel():')
    end=t.index('\nSCENARIOS={', start)
    block=t[start:end]
    assert 'connect("pms")' in block
    assert 'connect("cargo")' in block
    assert 'connect("propulsion")' in block
    assert 'commissioning-timeline.jsonl' in block
    assert 'vessel-coordinator:8600/state' in block
    assert 'alarm-engine:8400/alarms' in block


def test_commissioning_tools_have_required_networks_and_mounts():
    d=yaml.safe_load(Path('docker-compose.yml').read_text())
    sc=d['services']['commissioning-client']
    assert 'operations' in sc['networks']
    assert './evidence:/evidence' in sc['volumes']
    ct=d['services']['commissioning-tools']
    assert 'operations' in ct['networks']
    assert './evidence:/evidence' in ct['volumes']
    assert './fuxa:/project/fuxa:ro' in ct['volumes']


def test_public_readme_does_not_claim_pms_propulsion_are_future_only():
    t=Path('README.md').read_text().lower()
    assert 'dedicated physics model is a future module' not in t
    assert 'dynamic two-generator teaching model' in t
    assert 'dynamic pre-lube' in t


def test_binding_plan_uses_discovery_and_telegraf_id_syntax():
    t=Path('commissioning/binding_plan.py').read_text()
    assert 'opcua-discovery.json' in t
    assert 'missing' in t and 'ambiguous' in t
    assert 'id="{nodeid}"' in t
    assert 'identifier="{nodeid}"' not in t
    assert 'timestamp = "source"' in t


def test_labctl_exposes_opcua_binding_and_fuxa_workflows():
    t=Path('labctl').read_text()
    for token in ['cmd_opcua','cmd_bind_plan','cmd_fuxa','fuxa bootstrap']:
        assert token in t

def test_historian_base_config_has_no_guessed_opcua_nodes():
    t=Path('historian/telegraf.conf').read_text()
    assert '[[inputs.opcua]]' not in t
    assert 'nodes = [' not in t
    assert '[[outputs.influxdb_v2]]' in t


def test_hist_install_is_verified_live_binding_workflow():
    t=Path('labctl').read_text()
    assert 'cmd_hist_install' in t
    assert 'hist-install <domain>' in t
    assert 'binding-plan.json' in t
    assert 'historian/generated/${domain}.conf' in t


def test_telegraf_loads_generated_binding_directory():
    d=yaml.safe_load(Path('docker-compose.yml').read_text())
    svc=d['services']['telegraf']
    assert './historian/generated:/etc/telegraf/telegraf.d:ro' in svc['volumes']
    assert '--config-directory' in svc['command']
    assert '/etc/telegraf/telegraf.d' in svc['command']


def test_generated_historian_binding_files_are_not_committed():
    t=Path('.gitignore').read_text()
    assert 'historian/generated/*.conf' in t
    assert '!historian/generated/.gitkeep' in t

