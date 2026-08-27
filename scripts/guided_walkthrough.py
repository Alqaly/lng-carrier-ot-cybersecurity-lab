#!/usr/bin/env python3
import json, urllib.request

def get(url):
    with urllib.request.urlopen(url, timeout=2) as r:
        return json.loads(r.read())

def section(title, url, fields):
    print(f"\n=== {title} ===")
    try:
        s = get(url)
        if not s.get('ready', True):
            print('NOT READY:', s)
            return
        for k, label, unit, scale in fields:
            v = s.get(k)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                print(f"{label:24} {v*scale:10.3f} {unit}")
            else:
                print(f"{label:24} {v}")
    except Exception as e:
        print('UNAVAILABLE:', e)

print("LNG Carrier OT Cybersecurity Lab - Guided State Walkthrough")
print("This script reads live lab services. It does not create process values.")
section('Cargo','http://127.0.0.1:8100/state',[
 ('levelSource','Source level','m',1),('levelDestination','Destination level','m',1),('flowMeasured','Measured flow','L/min',60000),('pressureSource','Source pressure','kPa',1),('valvePosition','Valve position','%',100),('pumpSpeed','Pump speed','%',100),('valveFeedback','Valve feedback','',1),('pumpFeedback','Pump feedback','',1)])
section('Power Management','http://127.0.0.1:8200/state',[
 ('frequencyHz','Bus frequency','Hz',1),('voltagePU','Bus voltage','p.u.',1),('totalLoadKW','Total load','kW',1),('spinningReserveKW','Spinning reserve','kW',1),('gen1PowerKW','Generator 1','kW',1),('gen2PowerKW','Generator 2','kW',1),('underFrequency','Under-frequency','',1),('blackout','Blackout','',1)])
section('Propulsion','http://127.0.0.1:8300/state',[
 ('engineRPM','Engine speed','rpm',1),('lubeOilPressureBar','Lube pressure','bar',1),('coolantTempC','Coolant temperature','C',1),('engineLoadPct','Engine load','%',1),('vesselSpeedKn','Vessel speed','kn',1),('engineRunning','Running','',1)])
print('\n=== Current alarms ===')
try:
    alarms = [a for a in get('http://127.0.0.1:8400/alarms') if a.get('active')]
    if not alarms:
        print('No active alarms.')
    for a in alarms:
        print(f"{a['priority']:8} {a['domain']:11} {a['id']}: {a['message']} ({'ACK' if a['acked'] else 'UNACK'})")
except Exception as e:
    print('UNAVAILABLE:', e)
print("\nNext: pick one value and trace model -> I/O -> Modbus -> PLC -> operator/historian -> evidence.")
