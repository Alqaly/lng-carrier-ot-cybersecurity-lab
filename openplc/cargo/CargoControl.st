PROGRAM CargoControl
VAR
    (* Operator / sequence input *)
    Transfer_Enable : BOOL := FALSE;

    (* Remote-I/O discrete inputs *)
    DI_ValveOpenFB : BOOL := FALSE;
    DI_PumpRunFB : BOOL := FALSE;
    DI_HighHighDestination : BOOL := FALSE;
    DI_LowLowSource : BOOL := FALSE;

    (* Remote-I/O input registers *)
    AI_LevelSource_mm : INT := 0;
    AI_LevelDestination_mm : INT := 0;
    AI_Flow_m3h : INT := 0;
    AI_Pressure_kPa_x10 : INT := 0;
    AI_ValvePosition_x1000 : INT := 0;
    AI_PumpSpeed_x1000 : INT := 0;
    AI_PumpPower_kW : INT := 0;

    (* Remote-I/O outputs *)
    DO_Pump : BOOL := FALSE;
    AO_ValvePermille : INT := 0;

    (* Engineering-unit values for HMI / OPC UA / historian *)
    LevelSource_m : REAL := 0.0;
    LevelDestination_m : REAL := 0.0;
    Flow_m3h : REAL := 0.0;
    Pressure_kPa : REAL := 0.0;
    ValvePosition : REAL := 0.0;
    PumpSpeed : REAL := 0.0;
    PumpPower_kW : REAL := 0.0;

    Permit_Transfer : BOOL := FALSE;
    Alarm_CommandFeedbackMismatch : BOOL := FALSE;
    Alarm_NoFlow : BOOL := FALSE;
    Safety_Trip : BOOL := FALSE;
END_VAR

LevelSource_m := INT_TO_REAL(AI_LevelSource_mm)/1000.0;
LevelDestination_m := INT_TO_REAL(AI_LevelDestination_mm)/1000.0;
Flow_m3h := INT_TO_REAL(AI_Flow_m3h);
Pressure_kPa := INT_TO_REAL(AI_Pressure_kPa_x10)/10.0;
ValvePosition := INT_TO_REAL(AI_ValvePosition_x1000)/1000.0;
PumpSpeed := INT_TO_REAL(AI_PumpSpeed_x1000)/1000.0;
PumpPower_kW := INT_TO_REAL(AI_PumpPower_kW);

Safety_Trip := DI_HighHighDestination OR DI_LowLowSource;
Permit_Transfer := Transfer_Enable AND NOT Safety_Trip;

AO_ValvePermille := SEL(Permit_Transfer,0,1000);
DO_Pump := Permit_Transfer AND DI_ValveOpenFB;

Alarm_CommandFeedbackMismatch :=
    (AO_ValvePermille > 950 AND NOT DI_ValveOpenFB)
    OR
    (DO_Pump AND NOT DI_PumpRunFB);

Alarm_NoFlow := DI_PumpRunFB AND DI_ValveOpenFB AND Flow_m3h < 50.0;
END_PROGRAM
