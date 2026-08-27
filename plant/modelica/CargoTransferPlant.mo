model CargoTransferPlant
  // Teaching-scale aggregate inspired by public LNG-carrier cargo equipment
  // references. The pump bank represents eight 1700 m3/h submerged cargo pumps
  // (4 tanks x 2 pumps) as one equivalent train. Pump head/efficiency are model
  // assumptions, not vendor ratings.
  parameter Real rho = 450 "Representative LNG-like liquid density kg/m3";
  parameter Real g = 9.81 "Gravity m/s2";
  parameter Real areaSource = 6000.0 "Aggregate source tank area m2";
  parameter Real areaDestination = 12000.0 "Aggregate receiving tank area m2";
  parameter Real nominalBankFlow = 13600.0/3600.0 "8 x 1700 m3/h converted to m3/s";
  parameter Real pumpHeadNominal = 100.0 "Teaching total head m";
  parameter Real pumpEfficiency = 0.72 "Teaching aggregate efficiency";
  parameter Real tauValve = 2.0 "Valve actuator time constant s";
  parameter Real tauPump = 3.0 "Cargo pump-bank run-up time constant s";
  parameter Real tauSensor = 0.7 "Flow transmitter response time s";
  parameter Real minSourceLevel = 1.0 "Low-low source level m";
  parameter Real maxDestinationLevel = 24.0 "High-high destination level m";

  input Boolean pumpCmd;
  input Boolean powerAvailable;
  input Real valveCommand(min=0,max=1);
  input Boolean faultValveStuck;
  input Boolean faultPumpFail;
  input Boolean faultFlowPathBlocked;
  input Real flowSensorBiasPct;

  output Real levelSource(start=23.0, fixed=true) "m";
  output Real levelDestination(start=4.0, fixed=true) "m";
  output Real flow "m3/s actual aggregate cargo flow";
  output Real flowMeasured(start=0, fixed=true) "m3/s transmitter value";
  output Real pressureSource "kPa hydrostatic teaching value";
  output Real pressureDestination "kPa hydrostatic teaching value";
  output Real pumpSpeed(start=0, fixed=true) "per-unit";
  output Real valvePosition(start=0, fixed=true) "0..1";
  output Real pumpPowerKW "aggregate electrical demand estimate";
  output Boolean pumpFeedback;
  output Boolean valveFeedback;
  output Boolean highHighDestination;
  output Boolean lowLowSource;

protected
  Real pumpTarget;
  Real availableHead;
  Real headFactor;
  Real idealFlow;
  Real hydraulicPowerW;
  Real nominalShaftPowerKW;
  Real blockedFlowFactor;

equation
  pumpTarget = if pumpCmd and powerAvailable and not faultPumpFail then 1.0 else 0.0;
  der(pumpSpeed) = (pumpTarget - pumpSpeed) / tauPump;
  der(valvePosition) = if faultValveStuck then 0 else (valveCommand - valvePosition) / tauValve;

  // Static level difference reduces the available pump head.
  availableHead = max(0.0, pumpHeadNominal*pumpSpeed*pumpSpeed - max(0.0,levelDestination-levelSource));
  headFactor = sqrt(max(0.0, min(1.10, availableHead/pumpHeadNominal)));
  blockedFlowFactor = if faultFlowPathBlocked then 0.0 else 1.0;
  idealFlow = nominalBankFlow * max(0.0,valvePosition) * headFactor;
  flow =
    if levelSource > minSourceLevel and levelDestination < maxDestinationLevel then
      idealFlow * blockedFlowFactor
    else 0.0;
  der(flowMeasured) = ((flow * (1.0 + flowSensorBiasPct/100.0)) - flowMeasured) / tauSensor;

  der(levelSource) = -flow / areaSource;
  der(levelDestination) = flow / areaDestination;

  pressureSource = rho * g * max(levelSource,0.0) / 1000.0;
  pressureDestination = rho * g * max(levelDestination,0.0) / 1000.0;

  hydraulicPowerW = rho*g*flow*max(0.0,pumpHeadNominal*pumpSpeed*pumpSpeed);
  nominalShaftPowerKW = rho*g*nominalBankFlow*pumpHeadNominal/max(0.1,pumpEfficiency)/1000.0;

  // A centrifugal pump can continue drawing power at blocked/near-zero flow.
  // The 25% floor is a teaching assumption, not a vendor pump curve.
  pumpPowerKW =
    if pumpSpeed > 0.05 then
      max(hydraulicPowerW/max(0.1,pumpEfficiency)/1000.0,
          0.25*nominalShaftPowerKW*pumpSpeed)
    else 0.0;

  pumpFeedback = pumpSpeed > 0.90;
  valveFeedback = valvePosition > 0.95;
  highHighDestination = levelDestination >= maxDestinationLevel;
  lowLowSource = levelSource <= minSourceLevel;
end CargoTransferPlant;
