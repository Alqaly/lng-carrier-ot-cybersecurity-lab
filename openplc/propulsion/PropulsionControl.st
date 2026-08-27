PROGRAM PropulsionControl
VAR
    Propulsion_Enable : BOOL := FALSE;
    RPM_Setpoint_x10 : INT := 0;
    Pitch_Setpoint_Permille : INT := 0;

    (* Remote-I/O discrete inputs *)
    DI_EngineRunning : BOOL := FALSE;
    DI_LowLubePressure : BOOL := FALSE;
    DI_HighCoolantTemp : BOOL := FALSE;
    DI_Overspeed : BOOL := FALSE;

    (* Remote-I/O input registers *)
    AI_EngineRPM_x10 : INT := 0;
    AI_LubeBar_x100 : INT := 0;
    AI_CoolantC_x10 : INT := 0;
    AI_VesselSpeed_kn_x100 : INT := 0;
    AI_EngineLoad_pct_x10 : INT := 0;
    AI_PropellerTorque_10Nm : INT := 0;
    AI_AuxLoad_kW : INT := 0;

    (* Remote-I/O outputs *)
    DO_PreLube : BOOL := FALSE;
    DO_EngineEnable : BOOL := FALSE;
    AO_FuelPermille : INT := 0;
    AO_PitchPermille : INT := 0;

    (* Engineering-unit values for HMI / OPC UA / historian *)
    EngineRPM : REAL := 0.0;
    LubeBar : REAL := 0.0;
    Coolant_C : REAL := 0.0;
    VesselSpeed_kn : REAL := 0.0;
    EngineLoad_pct : REAL := 0.0;
    PropellerTorque_Nm : REAL := 0.0;
    AuxLoad_kW : REAL := 0.0;
    RPM_Setpoint : REAL := 0.0;
    ErrorRPM : REAL := 0.0;
    Trip : BOOL := FALSE;
END_VAR

EngineRPM := INT_TO_REAL(AI_EngineRPM_x10)/10.0;
LubeBar := INT_TO_REAL(AI_LubeBar_x100)/100.0;
Coolant_C := INT_TO_REAL(AI_CoolantC_x10)/10.0;
VesselSpeed_kn := INT_TO_REAL(AI_VesselSpeed_kn_x100)/100.0;
EngineLoad_pct := INT_TO_REAL(AI_EngineLoad_pct_x10)/10.0;
PropellerTorque_Nm := INT_TO_REAL(AI_PropellerTorque_10Nm)*10.0;
AuxLoad_kW := INT_TO_REAL(AI_AuxLoad_kW);
RPM_Setpoint := INT_TO_REAL(RPM_Setpoint_x10)/10.0;

Trip := DI_LowLubePressure OR DI_HighCoolantTemp OR DI_Overspeed;
DO_PreLube := Propulsion_Enable AND NOT Trip;
DO_EngineEnable := Propulsion_Enable AND LubeBar > 2.5 AND NOT Trip;
ErrorRPM := RPM_Setpoint - EngineRPM;
AO_PitchPermille := SEL(DO_EngineEnable,0,MAX(0,MIN(1000,Pitch_Setpoint_Permille)));
IF DO_EngineEnable THEN
    AO_FuelPermille := REAL_TO_INT(MAX(0.0,MIN(1000.0,350.0 + ErrorRPM*12.0)));
ELSE
    AO_FuelPermille := 0;
END_IF;
END_PROGRAM
