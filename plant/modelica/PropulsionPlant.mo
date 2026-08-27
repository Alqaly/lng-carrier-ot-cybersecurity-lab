model PropulsionPlant
  parameter Real maxRPM = 95.0;
  parameter Real maxTorqueNm = 55000.0;
  parameter Real shaftInertia = 12000.0;
  parameter Real friction = 120.0;
  parameter Real propLoadCoeff = 1500.0 "Teaching propeller torque coefficient";
  parameter Real tauLube = 1.2;
  parameter Real tauCool = 25.0;
  parameter Real normalTempGain = 0.48;
  parameter Real coolingFaultTempGain = 0.90;
  parameter Real highCoolantTripC = 92.0;
  parameter Real vesselMassScale = 200.0 "Teaching vessel response inertia";

  input Boolean preLubeCmd;
  input Boolean auxPowerAvailable;
  input Boolean engineEnable;
  input Real fuelCommand(min=0,max=1);
  input Real pitchCommand(min=0,max=1);
  input Boolean faultLubePumpFail;
  input Boolean faultCoolingFail;

  output Real engineRPM(start=0, fixed=true);
  output Real lubeOilPressureBar(start=0, fixed=true);
  output Real coolantTempC(start=35, fixed=true);
  output Real vesselSpeedKn(start=0, fixed=true);
  output Real engineLoadPct;
  output Real shaftTorqueNm;
  output Real propellerTorqueNm;
  output Real auxiliaryElectricalLoadKW;
  output Boolean engineRunning;
  output Boolean lowLubePressure;
  output Boolean highCoolantTemp;
  output Boolean overspeed;

protected
  Real omega;
  Real engineTorque;
  Real propTorque;
  Real lubeTarget;
  Real tempTarget;
  Real thrust;
  Real drag;

equation
  omega = engineRPM * 2*3.14159265/60;
  engineTorque =
    if engineEnable and lubeOilPressureBar > 1.8 then
      maxTorqueNm*max(0,min(1,fuelCommand))*max(0,1-engineRPM/(maxRPM*1.15))
    else 0;

  propTorque = propLoadCoeff * max(0,pitchCommand) * omega*omega;
  propellerTorqueNm = propTorque;
  shaftTorqueNm = engineTorque - propTorque;

  der(engineRPM) =
    if engineRPM <= 0 and (shaftTorqueNm - friction*omega) <= 0 then
      0
    else
      (shaftTorqueNm - friction*omega) * 60/(2*3.14159265*shaftInertia);

  // Pre-lube is electrically dependent. Once the engine is turning, the
  // teaching model represents an engine-driven main lube-pump contribution.
  lubeTarget =
    if faultLubePumpFail then 0
    else if engineRPM > 5 then 3.8 + 0.018*engineRPM
    else if preLubeCmd and auxPowerAvailable then 3.8
    else 0;

  der(lubeOilPressureBar) = (lubeTarget-lubeOilPressureBar)/tauLube;

  engineLoadPct = min(100,max(0,100*propTorque/maxTorqueNm));
  tempTarget = 35 + (if faultCoolingFail then coolingFaultTempGain else normalTempGain)*engineLoadPct;
  der(coolantTempC) = (tempTarget-coolantTempC)/tauCool;

  thrust = max(0,pitchCommand)*omega*omega*2.0;
  drag = 0.08*vesselSpeedKn*vesselSpeedKn;

  der(vesselSpeedKn) =
    if vesselSpeedKn <= 0 and (thrust-drag) <= 0 then
      0
    else
      (thrust-drag)/vesselMassScale;

  // Selected training profile: electrical auxiliaries are a small PMS load;
  // mechanical shaft propulsion itself is not placed on the electrical bus.
  auxiliaryElectricalLoadKW =
    if engineRPM > 5 then 180
    else if preLubeCmd and auxPowerAvailable then 120
    else 40;

  engineRunning = engineRPM > 15;
  lowLubePressure = engineRunning and lubeOilPressureBar < 2.0;
  highCoolantTemp = coolantTempC > highCoolantTripC;
  overspeed = engineRPM > 102.0;
end PropulsionPlant;
