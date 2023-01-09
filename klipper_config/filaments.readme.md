# Filament Handling Macros

## What this does
* Keep a number of filament presets stored in save variables by name. Filaments can be created and updated with `SETUP_FILAMENT`.
* Assign a preset to the printer with `SET_FILAMENT`, the assignment survives printer restarts
    * If you have a multi-tool printer you can assign a filament to each tool by tool index
* A set of simple macros that use the assigned filament to heat up the Extruder and Heater Bed. They check that a filament is selected and stop any containing macro or print if not.
* Display all of the filaments with `LIST_FILAMENT` and show what filament is configured now with `FILAMENT_STATUS`

## Why would you want to use this?
* Simplify your filament loading and unloading process. Automatically heat the extruder without having to re-select the same preset over and over again.
* Simplify tuning macros, they don't have to ask fo temperature inputs, they can use the values from filament assigned to the extruder. E.g. perform Pressure Advance tuning or Live-Z calibration prints without having to ask for temperatures as inputs.
* Simplify your printer preheating routine, now you just run `PREHEAT_BED` and it knows what temp to heat up to.

## Multi-tool Printer Support
All macros require a `TOOL_INDEX=n` parameter when used in a multi-extruder printer. Different filament types can be configured on independent extruders for IDEX and tool changer setups.

The bed can also be heated based on the tool to be used. E.g. if you are printing PETG in T0 with PLA supports in T3 you can specify that the bed temperature from T0 is the one to use for heating the bed with `PREHEAT_BED TOOL_INDEX=0`.

Multi-tool printers also get a different `FILAMENT_STATUS` output that shows the status of each tool individually:
```
T0: None
T1: PETG: Exruder: 250C, Heater Bed: 85C
T2: None
T3: PLA: Exruder: 220C, Heater Bed: 60C
```

## Filaments Starter Pack
```
SETUP_FILAMENT NAME=PLA EXTRUDER=215 BED=60
SETUP_FILAMENT NAME=PETG EXTRUDER=250 BED=85
SETUP_FILAMENT NAME=ASA EXTRUDER=260 BED=100
SETUP_FILAMENT NAME=PC EXTRUDER=275 BED=100
SETUP_FILAMENT NAME=PVB EXTRUDER=215 BED=75
SETUP_FILAMENT NAME=ABS EXTRUDER=255 BED=100
SETUP_FILAMENT NAME=HIPS EXTRUDER=220 BED=100
SETUP_FILAMENT NAME=PP EXTRUDER=240 BED=100
SETUP_FILAMENT NAME=FLEX EXTRUDER=240 BED=50
```

## Integrating with Fluidd
Fluidd provides a spot to run G-Code when the filament presets are selected. We can use this to create/update filaments based on the data from Fluidd. We can also cancel heating if we want those buttons to act as just a filament switcher and not a command to heat anything up.


## TODO
* Implement tracking of the state of filament loading, so a tool would have an object that says what filament is assigned but also if it is loaded or unloaded. This could then be checked before extruding. E.g. `CHECK_FILAMENT_LOADED TOOL_INDEX=2`.