PROGRAM PowerManagement
VAR
    Plant_Enable : BOOL := FALSE;
    Demand_Hotel : BOOL := FALSE;
    Demand_Cargo : BOOL := FALSE;
    Demand_Propulsion : BOOL := FALSE;

    (* Remote-I/O discrete inputs *)
    DI_Gen1Ready : BOOL := FALSE;
    DI_Gen2Ready : BOOL := FALSE;
    DI_Gen1BreakerFB : BOOL := FALSE;
    DI_Gen2BreakerFB : BOOL := FALSE;
    DI_UnderFrequency : BOOL := FALSE;
    DI_Blackout : BOOL := FALSE;
    DI_Gen1SyncPermissive : BOOL := FALSE;
    DI_Gen2SyncPermissive : BOOL := FALSE;
    DI_BusEnergized : BOOL := FALSE;

    (* Remote-I/O input registers *)
    AI_Frequency_x100 : INT := 0;
    AI_Voltage_x1000 : INT := 0;
    AI_Gen1Power_kW : INT := 0;
    AI_Gen2Power_kW : INT := 0;
    AI_TotalLoad_kW : INT := 0;
    AI_Reserve_kW : INT := 0;
    AI_Gen1Speed_x1000 : INT := 0;
    AI_Gen2Speed_x1000 : INT := 0;
    AI_CargoLoad_kW : INT := 0;
    AI_AuxLoad_kW : INT := 0;

    (* Remote-I/O outputs *)
    DO_Gen1Start : BOOL := FALSE;
    DO_Gen2Start : BOOL := FALSE;
    DO_Gen1Breaker : BOOL := FALSE;
    DO_Gen2Breaker : BOOL := FALSE;
    DO_ShedHotel : BOOL := FALSE;
    DO_ShedCargo : BOOL := FALSE;
    AO_LoadHotel : INT := 0;
    AO_LoadCargo : INT := 0;
    AO_LoadPropulsion : INT := 0;

    (* Engineering-unit values for HMI / OPC UA / historian *)
    Frequency_Hz : REAL := 0.0;
    Voltage_PU : REAL := 0.0;
    Gen1Power_kW : REAL := 0.0;
    Gen2Power_kW : REAL := 0.0;
    TotalLoad_kW : REAL := 0.0;
    Reserve_kW : REAL := 0.0;
    Gen1Speed_PU : REAL := 0.0;
    Gen2Speed_PU : REAL := 0.0;
    CargoLoad_kW : REAL := 0.0;
    AuxLoad_kW : REAL := 0.0;
END_VAR

Frequency_Hz := INT_TO_REAL(AI_Frequency_x100)/100.0;
Voltage_PU := INT_TO_REAL(AI_Voltage_x1000)/1000.0;
Gen1Power_kW := INT_TO_REAL(AI_Gen1Power_kW);
Gen2Power_kW := INT_TO_REAL(AI_Gen2Power_kW);
TotalLoad_kW := INT_TO_REAL(AI_TotalLoad_kW);
Reserve_kW := INT_TO_REAL(AI_Reserve_kW);
Gen1Speed_PU := INT_TO_REAL(AI_Gen1Speed_x1000)/1000.0;
Gen2Speed_PU := INT_TO_REAL(AI_Gen2Speed_x1000)/1000.0;
CargoLoad_kW := INT_TO_REAL(AI_CargoLoad_kW);
AuxLoad_kW := INT_TO_REAL(AI_AuxLoad_kW);

AO_LoadHotel := SEL(Demand_Hotel,0,1);
AO_LoadCargo := SEL(Demand_Cargo,0,1);
AO_LoadPropulsion := SEL(Demand_Propulsion,0,1);

DO_Gen1Start := Plant_Enable;
DO_Gen1Breaker := Plant_Enable AND DI_Gen1Ready AND DI_Gen1SyncPermissive;

(* Establish the first bus before making a reserve-based second-generator decision. *)
DO_Gen2Start :=
    Plant_Enable
    AND DI_Gen1BreakerFB
    AND (Reserve_kW < 1500.0 OR DI_UnderFrequency);

DO_Gen2Breaker :=
    DO_Gen2Start
    AND DI_Gen2Ready
    AND DI_Gen2SyncPermissive;

(* Staged shedding: Cargo is removed at the first threshold; hotel/auxiliary load is removed only after a deeper frequency excursion. *)
DO_ShedCargo := DI_BusEnergized AND Frequency_Hz < 57.5;
DO_ShedHotel := DI_BusEnergized AND Frequency_Hz < 57.0;
END_PROGRAM
