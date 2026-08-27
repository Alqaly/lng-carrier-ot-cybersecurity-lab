import json, math, re
from pathlib import Path

def param(path,name):
    text=Path(path).read_text()
    m=re.search(rf'parameter\s+Real\s+{re.escape(name)}\s*=\s*([^";]+)',text)
    assert m, f'missing {name}'
    expr=m.group(1).strip()
    # Model parameters in these tests intentionally use simple numeric arithmetic only.
    return float(eval(expr,{"__builtins__":{}},{}))

def test_cargo_nominal_values_fit_modbus_contract():
    nominal=param('plant/modelica/CargoTransferPlant.mo','nominalBankFlow')
    io=json.loads(Path('io_emulator/configs/cargo.json').read_text())
    scale=io['outputs']['flowMeasured']['scale']
    raw=nominal/scale
    assert 10000 < raw < 20000
    assert raw < 65535

    rho=param('plant/modelica/CargoTransferPlant.mo','rho')
    g=param('plant/modelica/CargoTransferPlant.mo','g')
    head=param('plant/modelica/CargoTransferPlant.mo','pumpHeadNominal')
    eff=param('plant/modelica/CargoTransferPlant.mo','pumpEfficiency')
    kw=rho*g*nominal*head/eff/1000
    assert 1500 < kw < 3500
    assert kw < 65535

def test_pms_register_scaling_covers_two_generator_capacity():
    rated=param('plant/modelica/PowerManagementPlant.mo','generatorRatedKW')
    io=json.loads(Path('io_emulator/configs/pms.json').read_text())
    for key in ['gen1PowerKW','gen2PowerKW','totalLoadKW','spinningReserveKW']:
        scale=float(io['outputs'][key]['scale'])
        assert (2*rated)/scale < 65535

def test_propulsion_torque_register_has_headroom():
    maxrpm=param('plant/modelica/PropulsionPlant.mo','maxRPM')
    coeff=param('plant/modelica/PropulsionPlant.mo','propLoadCoeff')
    torque=coeff*(maxrpm*2*math.pi/60)**2
    io=json.loads(Path('io_emulator/configs/propulsion.json').read_text())
    spec=io['outputs']['propellerTorqueNm']
    raw=torque/float(spec['scale'])
    assert raw < 65535

def test_propulsion_command_addresses_match_reference():
    io=json.loads(Path('io_emulator/configs/propulsion.json').read_text())
    assert io['commands']['fuelCommand']['address']==0
    assert io['commands']['pitchCommand']['address']==1


def test_fmu_build_keeps_portable_default_cosim_integrator():
    text=Path('plant/modelica/build_all_fmus.mos').read_text()
    assert 'fmuType="cs"' in text
    assert '--fmiFlags=s:cvode' not in text
