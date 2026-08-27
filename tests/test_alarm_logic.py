import json
from pathlib import Path

EXPECTED={'CARGO_DEST_HH','CARGO_NO_FLOW','PMS_BLACKOUT','PMS_LOW_RESERVE','PROP_LOW_LUBE'}

def test_alarm_catalog_unique_and_rationalized():
    data=json.loads(Path('alarms/catalog.json').read_text())['alarms']
    ids=[a['id'] for a in data]
    assert len(ids)==len(set(ids))
    assert EXPECTED <= set(ids)
    for a in data:
        assert a['conditions']
        assert a['priority'] in {'MEDIUM','HIGH','CRITICAL'}
        assert a['operator_response']
        assert a['consequence']
        assert a['rationale']
        assert a['activation_delay_s'] >= 0
        assert a['clear_delay_s'] >= 0

def test_model_configs_have_contracts():
    for name in ['cargo','pms','propulsion']:
        cfg=json.loads(Path(f'plant/configs/{name}.json').read_text())
        assert cfg['inputs'] and cfg['outputs'] and cfg['fmu_path'].endswith('.fmu')

def test_fault_defaults_are_neutral():
    cargo=json.loads(Path('io_emulator/configs/cargo.json').read_text())
    assert cargo['commands']['flowSensorBiasPct'].get('offset',0)==0
    # A fresh all-zero register/coil bank must not activate any instructor fault.
    for name,spec in cargo['commands'].items():
        if name.startswith('fault'):
            assert spec['source']=='coil'


def test_alarm_hysteresis_and_visibility_alarms():
    data={a['id']:a for a in json.loads(Path('alarms/catalog.json').read_text())['alarms']}
    assert data['PMS_UNDER_FREQUENCY']['clear_conditions']
    assert data['PMS_LOW_RESERVE']['clear_conditions']
    assert data['PROP_HIGH_COOLANT']['clear_conditions']
    for domain in ['CARGO','PMS','PROPULSION']:
        aid=f'{domain}_PROCESS_SOURCE_STALE'
        assert aid in data
        assert data[aid]['conditions'][0]['field']=='__stale__'
        assert 'process-runtime source' in data[aid]['rationale']
