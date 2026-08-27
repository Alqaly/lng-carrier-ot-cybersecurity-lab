import json
from pathlib import Path
import yaml

def test_vessel_profile_does_not_fake_electric_main_propulsion():
    p=json.loads(Path('vessel/profile.json').read_text())
    assert p['cargo_power_from_pms'] is True
    assert p['propulsion_aux_power_from_pms'] is True
    assert p['electric_propulsion_main_load'] is False

def test_coupled_model_contract_fields_exist():
    cargo=json.loads(Path('plant/configs/cargo.json').read_text())
    pms=json.loads(Path('plant/configs/pms.json').read_text())
    prop=json.loads(Path('plant/configs/propulsion.json').read_text())
    assert cargo['inputs']['powerAvailable']=='boolean'
    assert cargo['outputs']['pumpPowerKW']=='real'
    assert pms['inputs']['externalCargoLoadKW']=='real'
    assert pms['inputs']['externalAuxLoadKW']=='real'
    assert prop['inputs']['auxPowerAvailable']=='boolean'
    assert prop['outputs']['auxiliaryElectricalLoadKW']=='real'

def test_compose_contains_coordinator_and_current_fuxa():
    c=yaml.safe_load(Path('docker-compose.yml').read_text())
    assert 'vessel-coordinator' in c['services']
    assert c['services']['fuxa']['image']=='frangoteam/fuxa:1.3.4'
