model PowerManagementPlant
  parameter Real nominalFrequency = 60.0 "Hz";
  parameter Real generatorRatedKW = 4500.0 "Teaching generator rating kW";
  parameter Real hotelLoadKW = 1000.0 "Teaching hotel/aux load";
  parameter Real cargoLoadKW = 2500.0 "Standalone PMS cargo load exercise";
  parameter Real propulsionLoadKW = 3000.0 "Optional electric-propulsion exercise load";
  parameter Real tauPrimeMover = 4.0;
  parameter Real tauGovernor = 1.0;
  parameter Real freqInertia = 1600.0 "scaled kW*s/Hz";
  parameter Real damping = 260.0 "scaled kW/Hz";

  input Boolean gen1StartCmd;
  input Boolean gen2StartCmd;
  input Boolean gen1BreakerCmd;
  input Boolean gen2BreakerCmd;
  input Boolean loadHotelDemand;
  input Boolean loadCargoDemand;
  input Boolean loadPropulsionDemand;
  input Boolean shedHotel;
  input Boolean shedCargo;
  input Boolean faultGen1Trip;
  input Boolean faultGen2Trip;

  // Cross-system loads from the vessel coordinator. These are additive to the
  // standalone exercise demand flags and allow Cargo/auxiliary models to drive
  // the electrical bus without inventing dashboard-only values.
  input Real externalCargoLoadKW;
  input Real externalAuxLoadKW;

  output Real frequencyHz(start=0, fixed=true);
  output Real voltagePU;
  output Real gen1PowerKW(start=0, fixed=true);
  output Real gen2PowerKW(start=0, fixed=true);
  output Real totalLoadKW;
  output Real cargoLoadActualKW;
  output Real auxiliaryLoadActualKW;
  output Real spinningReserveKW;
  output Real gen1SpeedPU(start=0, fixed=true);
  output Real gen2SpeedPU(start=0, fixed=true);
  output Boolean gen1Ready;
  output Boolean gen2Ready;
  output Boolean gen1BreakerFB;
  output Boolean gen2BreakerFB;
  output Boolean gen1SyncPermissive;
  output Boolean gen2SyncPermissive;
  output Boolean busEnergized;
  output Boolean underFrequency;
  output Boolean blackout;

protected
  Real onlineCount;
  Real capacityKW;
  Real shareKW;
  Real g1Target;
  Real g2Target;
  Real hotelEffective;
  Real cargoEffective;
  Real propulsionEffective;
  Real frequencyDerivative;

equation
  der(gen1SpeedPU) = ((if gen1StartCmd and not faultGen1Trip then 1 else 0) - gen1SpeedPU)/tauPrimeMover;
  der(gen2SpeedPU) = ((if gen2StartCmd and not faultGen2Trip then 1 else 0) - gen2SpeedPU)/tauPrimeMover;
  gen1Ready = gen1SpeedPU > 0.95 and not faultGen1Trip;
  gen2Ready = gen2SpeedPU > 0.95 and not faultGen2Trip;

  // The first generator may close onto a dead bus. A subsequent generator must
  // be close to the live bus frequency. Phase-angle and AVR dynamics are outside
  // this teaching model and remain an explicit limitation.
  gen1SyncPermissive = (not gen2BreakerFB) or abs(gen1SpeedPU*nominalFrequency-frequencyHz) < 0.5;
  gen2SyncPermissive = (not gen1BreakerFB) or abs(gen2SpeedPU*nominalFrequency-frequencyHz) < 0.5;

  // Breaker feedback follows a valid command once the generator is ready.
  // The PLC uses the sync permissive before issuing the breaker command.
  // Keeping the physical feedback equation separate avoids a circular Boolean
  // dependency between both breaker states in this phasor-free model.
  gen1BreakerFB = gen1BreakerCmd and gen1Ready;
  gen2BreakerFB = gen2BreakerCmd and gen2Ready;

  hotelEffective = if loadHotelDemand and not shedHotel then hotelLoadKW else 0;
  cargoEffective =
    if shedCargo then 0
    else (if loadCargoDemand then cargoLoadKW else 0) + max(0.0,externalCargoLoadKW);
  propulsionEffective =
    (if loadPropulsionDemand then propulsionLoadKW else 0) + max(0.0,externalAuxLoadKW);

  cargoLoadActualKW = cargoEffective;
  auxiliaryLoadActualKW = propulsionEffective;
  totalLoadKW = hotelEffective + cargoEffective + propulsionEffective;

  onlineCount = (if gen1BreakerFB then 1 else 0) + (if gen2BreakerFB then 1 else 0);
  capacityKW = onlineCount * generatorRatedKW;

  shareKW =
    if onlineCount > 0 then
      min(generatorRatedKW, totalLoadKW/onlineCount + max(0,nominalFrequency-frequencyHz)*180)
    else
      0;

  g1Target = if gen1BreakerFB then shareKW else 0;
  g2Target = if gen2BreakerFB then shareKW else 0;
  der(gen1PowerKW) = (g1Target - gen1PowerKW)/tauGovernor;
  der(gen2PowerKW) = (g2Target - gen2PowerKW)/tauGovernor;

  frequencyDerivative =
    if onlineCount > 0 then
      ((gen1PowerKW+gen2PowerKW)-totalLoadKW-damping*(frequencyHz-nominalFrequency))/freqInertia
    else
      -6.0*frequencyHz;

  der(frequencyHz) = frequencyDerivative;

  voltagePU =
    if onlineCount > 0 then
      max(0.0,min(1.05,1.0 - 0.10*max(0,totalLoadKW-capacityKW)/generatorRatedKW))
    else 0.0;

  spinningReserveKW = max(0.0,capacityKW-totalLoadKW);
  busEnergized = onlineCount > 0.5 and frequencyHz > 50.0;
  underFrequency = busEnergized and frequencyHz < 58.5;
  blackout = onlineCount < 0.5 or frequencyHz < 10.0;

  // Only energizing a dead bus establishes the nominal reference.
  when (gen1BreakerFB or gen2BreakerFB) and pre(blackout) then
    reinit(frequencyHz, nominalFrequency);
  end when;
end PowerManagementPlant;
