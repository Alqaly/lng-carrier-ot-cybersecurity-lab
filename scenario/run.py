#!/usr/bin/env python3
import argparse, time, json
from pathlib import Path
import httpx
from pymodbus.client import ModbusTcpClient

DOMAINS={
    "cargo":("cargo-io",5020),
    "pms":("pms-io",5021),
    "propulsion":("propulsion-io",5022),
}

def wait(msg,seconds):
    print(f"\n{msg}")
    for i in range(seconds,0,-1):
        print(f"  {i:>2}s",end="\r",flush=True)
        time.sleep(1)
    print("     ")

def connect(domain):
    host,port=DOMAINS[domain]
    c=ModbusTcpClient(host,port=port,timeout=3)
    if not c.connect():
        raise SystemExit(f"Cannot connect to {host}:{port}")
    return c

def read_ir(c,count):
    r=c.read_input_registers(0,count=count,device_id=1)
    return [] if r.isError() else r.registers

def read_di(c,count):
    r=c.read_discrete_inputs(0,count=count,device_id=1)
    return [] if r.isError() else list(r.bits[:count])

def cargo():
    c=connect("cargo")
    try:
        print("COMMISSIONING MODE — direct Modbus I/O test; OpenPLC is bypassed.")
        print("Initial IR:",read_ir(c,7))
        c.write_register(0,1000,device_id=1)
        wait("Valve travel",4)
        c.write_coil(0,True,device_id=1)
        for _ in range(8):
            print("IR:",read_ir(c,7),"DI:",read_di(c,4))
            time.sleep(1)
        c.write_coil(0,False,device_id=1)
        c.write_register(0,0,device_id=1)
    finally:
        c.close()

def pms():
    c=connect("pms")
    try:
        print("COMMISSIONING MODE — direct Modbus I/O test; OpenPLC is bypassed.")
        c.write_coil(0,True,device_id=1)
        wait("Gen 1 prime-mover run-up",7)
        c.write_coil(2,True,device_id=1)
        c.write_register(0,1,device_id=1)
        wait("Hotel load applied",3)
        print("IR:",read_ir(c,10),"DI:",read_di(c,9))
        c.write_register(1,1,device_id=1)
        wait("Standalone cargo load step",4)
        print("IR:",read_ir(c,10))
        c.write_coil(1,True,device_id=1)
        wait("Gen 2 run-up",7)
        for _ in range(20):
            di=read_di(c,9)
            if len(di)>7 and di[7]:
                break
            time.sleep(0.25)
        c.write_coil(3,True,device_id=1)
        wait("Second generator connected",3)
        print("IR:",read_ir(c,10),"DI:",read_di(c,9))
    finally:
        c.close()

def propulsion():
    c=connect("propulsion")
    try:
        print("COMMISSIONING MODE — direct Modbus I/O test; OpenPLC is bypassed.")
        c.write_coil(0,True,device_id=1)
        wait("Pre-lube",4)
        c.write_coil(1,True,device_id=1)
        c.write_register(0,450,device_id=1)
        c.write_register(1,300,device_id=1)
        for _ in range(10):
            print("IR:",read_ir(c,7),"DI:",read_di(c,4))
            time.sleep(1)
        c.write_register(0,200,device_id=1)
        c.write_register(1,100,device_id=1)
        wait("Reduce load",3)
        print("IR:",read_ir(c,7))
    finally:
        c.close()


def cargo_fault():
    c=connect("cargo")
    try:
        print("CONTROLLED FAULT LAB — direct I/O commissioning path; OpenPLC is bypassed.")
        # Establish a normal transfer first.
        c.write_coil(20,False,device_id=1)
        c.write_coil(21,False,device_id=1)
        c.write_register(20,0,device_id=1)
        c.write_register(0,1000,device_id=1)
        wait("Valve travel",4)
        c.write_coil(0,True,device_id=1)
        wait("Stable transfer",5)
        print("NORMAL IR:",read_ir(c,7),"DI:",read_di(c,4))

        # Measurement-only problem: actual plant flow is unchanged but the Modbus
        # measurement path receives a +20% bias.
        c.write_register(20,200,device_id=1)
        wait("Apply +20% flow-transmitter bias",3)
        print("BIASED IR:",read_ir(c,7),"DI:",read_di(c,4))
        print("Compare measured flow with tank level rate-of-change in the Learning Portal.")

        # Equipment failure: pump target is forced to zero.
        c.write_register(20,0,device_id=1)
        c.write_coil(20,True,device_id=1)
        wait("Apply pump-bank failure",4)
        print("PUMP-FAIL IR:",read_ir(c,7),"DI:",read_di(c,4))

        # Recovery / cleanup.
        c.write_coil(20,False,device_id=1)
        c.write_coil(0,False,device_id=1)
        c.write_register(0,0,device_id=1)
        wait("Return to neutral",3)
    finally:
        c.close()


def pms_trip():
    c=connect("pms")
    try:
        print("CONTROLLED PMS FAULT LAB — direct I/O commissioning path; OpenPLC is bypassed.")
        for a in [0,1,2,3,4,5,20,21]: c.write_coil(a,False,device_id=1)
        for a in [0,1,2]: c.write_register(a,0,device_id=1)
        c.write_coil(0,True,device_id=1)
        wait("Generator 1 run-up",7)
        c.write_coil(2,True,device_id=1)
        c.write_register(0,1,device_id=1)
        c.write_register(1,1,device_id=1)
        wait("Establish loaded bus",4)
        print("NORMAL IR:",read_ir(c,10),"DI:",read_di(c,9))
        c.write_coil(20,True,device_id=1)
        for _ in range(6):
            print("TRIP IR:",read_ir(c,10),"DI:",read_di(c,9)); time.sleep(1)
        print("No automatic load shed occurs here because this commissioning path bypasses the PMS PLC.")
        c.write_coil(20,False,device_id=1)
        c.write_register(0,0,device_id=1); c.write_register(1,0,device_id=1)
        c.write_coil(0,False,device_id=1); c.write_coil(2,False,device_id=1)
    finally:
        c.close()


def propulsion_lube():
    c=connect("propulsion")
    try:
        print("CONTROLLED MACHINERY FAULT LAB — direct I/O commissioning path; OpenPLC is bypassed.")
        c.write_coil(20,False,device_id=1)
        c.write_coil(0,True,device_id=1)
        wait("Pre-lube",4)
        c.write_coil(1,True,device_id=1)
        c.write_register(0,450,device_id=1)
        c.write_register(1,300,device_id=1)
        wait("Establish running machinery state",7)
        print("NORMAL IR:",read_ir(c,7),"DI:",read_di(c,4))
        c.write_coil(20,True,device_id=1)
        for _ in range(7):
            print("LUBE-FAIL IR:",read_ir(c,7),"DI:",read_di(c,4)); time.sleep(1)
        print("The plant exposes low-lube state; the final protective shutdown is a PLC responsibility.")
        c.write_coil(20,False,device_id=1)
        c.write_register(0,0,device_id=1); c.write_register(1,0,device_id=1)
        c.write_coil(1,False,device_id=1); c.write_coil(0,False,device_id=1)
    finally:
        c.close()

def vessel():
    """Three-domain integrated commissioning event.

    This intentionally bypasses OpenPLC so the learner can validate process + I/O
    + vessel coupling before adding controller logic. The final course repeats the
    event through the PLCs.
    """
    p=connect("pms"); c=connect("cargo"); m=connect("propulsion")
    evidence=Path('/evidence/live/vessel')
    evidence.mkdir(parents=True,exist_ok=True)
    timeline=evidence/'commissioning-timeline.jsonl'

    def api(url):
        try:
            return httpx.get(url,timeout=1.5).json()
        except Exception as e:
            return {'ready':False,'error':str(e)}

    def record(phase,note):
        item={
            'ts':time.time(),
            'phase':phase,
            'note':note,
            'cargo_ir':read_ir(c,7),'cargo_di':read_di(c,4),
            'pms_ir':read_ir(p,10),'pms_di':read_di(p,9),
            'propulsion_ir':read_ir(m,7),'propulsion_di':read_di(m,4),
            'vessel':api('http://vessel-coordinator:8600/state'),
            'alarms':api('http://alarm-engine:8400/alarms'),
        }
        with timeline.open('a') as f: f.write(json.dumps(item)+'\n')
        print(f"\n[{phase}] {note}")
        print('  Vessel links:',item['vessel'].get('links',{}))
        print('  Cargo IR/DI:',item['cargo_ir'],item['cargo_di'])
        print('  PMS IR/DI:',item['pms_ir'],item['pms_di'])
        print('  Prop IR/DI:',item['propulsion_ir'],item['propulsion_di'])

    def reset():
        for a in [0,1,2,3,4,5,20,21]: p.write_coil(a,False,device_id=1)
        for a in [0,1,2]: p.write_register(a,0,device_id=1)
        for a in [0,20,21]: c.write_coil(a,False,device_id=1)
        for a in [0,20]: c.write_register(a,0,device_id=1)
        for a in [0,1,20]: m.write_coil(a,False,device_id=1)
        for a in [0,1]: m.write_register(a,0,device_id=1)

    try:
        print("""
INTEGRATED COMMISSIONING — OpenPLC is deliberately bypassed.
The three physical teaching models remain coupled through the Vessel Coordinator:
  Cargo pump kW + propulsion auxiliary kW → PMS load
  PMS bus availability → Cargo and propulsion auxiliary power
The final course repeats this event through OpenPLC after controller commissioning.
""")
        if timeline.exists(): timeline.unlink()
        reset(); wait('Reset all direct-I/O commands',2); record('0-neutral','All domains at known neutral state')

        # Phase 1: energize bus using Gen 1.
        p.write_coil(0,True,device_id=1)
        wait('Generator 1 prime-mover run-up',7)
        p.write_coil(2,True,device_id=1)
        p.write_register(0,1,device_id=1)   # hotel load
        wait('Establish live bus and hotel load',3)
        record('1-power','Generator 1 supplies the base vessel load')

        # Phase 2: establish propulsion auxiliary demand before engine start.
        m.write_coil(0,True,device_id=1)    # pre-lube
        wait('Propulsion pre-lube establishes lube pressure and auxiliary demand',4)
        record('2-prelube','Propulsion auxiliary electrical load is now coupled into PMS')
        m.write_coil(1,True,device_id=1)
        m.write_register(0,450,device_id=1)
        m.write_register(1,300,device_id=1)
        wait('Engine accelerates under fuel and pitch command',7)
        record('3-propulsion','Mechanical propulsion is running; only auxiliaries load PMS')

        # Phase 3: establish Cargo electrical load.
        c.write_register(0,1000,device_id=1)
        wait('Cargo valve travel',4)
        c.write_coil(0,True,device_id=1)
        wait('Cargo pump bank run-up and electrical demand coupling',5)
        record('4-cargo','Cargo flow is established and its pump power appears as PMS load')

        # Phase 4: start standby generator but trip Gen 1 before redundancy closes.
        p.write_coil(1,True,device_id=1)
        wait('Generator 2 begins run-up; breaker remains open',2)
        record('5-before-trip','Standby generation is not yet connected')
        p.write_coil(20,True,device_id=1)
        wait('Generator 1 trip collapses bus before Generator 2 is connected',3)
        record('6-power-loss','Cargo loses pump power; propulsion pre-lube auxiliary power is unavailable')

        # Phase 5: recover with Gen 2 after ready/sync permissive.
        print('\nWaiting for Generator 2 ready + sync permissive…')
        deadline=time.time()+20
        while time.time()<deadline:
            di=read_di(p,9)
            if len(di)>7 and di[1] and di[7]: break
            time.sleep(0.5)
        else:
            raise RuntimeError('Generator 2 did not reach ready/sync-permissive state')
        p.write_coil(3,True,device_id=1)
        wait('Generator 2 closes to dead bus and restores auxiliary power',5)
        record('7-recovery','Bus and dependent auxiliary services recover')

        print(f"\nIntegrated commissioning evidence: {timeline}")
        print('Use this timeline with PCAPs and the alarm chronicle in the evidence workbook.')
    finally:
        try:
            reset()
            p.write_coil(20,False,device_id=1)
        except Exception: pass
        p.close(); c.close(); m.close()

SCENARIOS={
    "cargo": cargo,
    "pms": pms,
    "propulsion": propulsion,
    "cargo-fault": cargo_fault,
    "pms-trip": pms_trip,
    "propulsion-lube": propulsion_lube,
    "vessel": vessel,
}

ap=argparse.ArgumentParser(description="Controlled process / Modbus commissioning scenarios")
ap.add_argument("scenario",choices=sorted(SCENARIOS))
args=ap.parse_args()
SCENARIOS[args.scenario]()
