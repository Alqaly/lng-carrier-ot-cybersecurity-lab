import json
from pathlib import Path

EXPECTED_PORTS={'cargo':5020,'pms':5021,'propulsion':5022}

def test_io_ports_and_model_contract_names():
    for domain,port in EXPECTED_PORTS.items():
        io=json.loads(Path(f'io_emulator/configs/{domain}.json').read_text())
        model=json.loads(Path(f'plant/configs/{domain}.json').read_text())
        assert io['port']==port
        assert set(io['commands']) <= set(model['inputs'])
        assert set(io['outputs']) <= set(model['outputs'])

def test_no_duplicate_modbus_addresses_per_area():
    for domain in EXPECTED_PORTS:
        io=json.loads(Path(f'io_emulator/configs/{domain}.json').read_text())
        for section,key in [('commands','source'),('outputs','dest')]:
            seen=set()
            for name,spec in io[section].items():
                area=spec[key]
                pair=(area,int(spec['address']))
                assert pair not in seen, f'{domain}: duplicate {pair}'
                seen.add(pair)

def test_no_random_process_generation():
    for p in [Path('plant/runtime/runner.py'),Path('io_emulator/server.py')]:
        assert 'random.' not in p.read_text()
