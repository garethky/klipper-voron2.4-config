# Removeable Build Sheet Manager
This is a system for using removable build sheets with Klipper. Build sheets are considered a consumable and can be swapped between prints. The main problem with swapping sheets is getting the correct Z-offset for that sheet. Different kinds of sheet textures, sheet materials, nozzle geometries and even filaments cause the optimal gap between the sheet's surface and the nozzle to be different. Also if using a non-contact sensor like an inductive probe the measured Z-distance is to metal sheet, not the surface of the non-conductive layer on top. So each sheet needs its own Z-offset. In a tool changing 3D Printer you may need an offset per tool to account for nozzle and filament differences.

This module is an implementation of "Live-Z" where the Z-offset for the sheet is saved immediatly as it is adjusted. You do not have to save and restart Klipper or remember to save changes at the end of a printing session. The offsets are stored in a separate JSON file in the same directory as you `printer.cfg`.

## Setup in Printer.cfg
`[build_sheets]`

`is_toolchanger:` Set this to `True` if your printer is a tool changer and you want to enable per-tool Z-offsets. Defaults to `False`.

`default_z_offset:` This is the inital Z-Offset value assigned to a new sheet (or new tool, in the case of a tool changer). Defaults to `0.0`. You may wish to set this to a positive value, like `1.0`, as a safety feature so new sheets (or tools) do not run the risk of hitting the build sheet.

`empty_z_offset:` This is the Z-Offset value reported by the build sheet system when no build sheet is installed in the printer (or no tool is selected, in the case of a toolchanger). Defaults to `0.0`.

`override_set_gcode_offset:` Override the `SET_GCODE_OFFSET` command and use any Z-values as inputs for the build_sheet offset. This allows you to set the Live-Z value for the sheet using the baby-stepping controls in your favorite front end. If you dont want this behaviour, set this to False. Defaults to `True`.

`set_gcode_offset_override_name` controls the how `SET_GCODE_OFFSET` is renamed when it is overriden with `override_set_gcode_offset`. Defaults to `BASE_SET_GCODE_OFFSET`.

## Display Build Sheet Status
`BUILD_SHEETS_STATUS`
Prints a human readable status to the console, including the current sheet, z-offset and a full listing of all sheets and their current offsets. If the machine is configured as a tool changer the status will include the current tool and Z-offsets for all configured tools on each sheet.

## Adding and Deleting Build Sheets
`ADD_BUILD_SHEET SHEET="My New Sheet Name"`
Adds a new sheet to the library named "My New Sheet Name".

`DELETE_BUILD_SHEET SHEET="My New Sheet Name"`
Deletes an existing build sheet from the library named "My New Sheet Name".

## Installing the Sheet into the Printer

## Swapping and Removing Sheets

## Adjusting Live-Z
To have the live-z value of the sheet reflected in the printer you can use the baby stepping controls in your front end (Fluidd etc.) or use the `SET_GCODE_OFFSET` command.

If you disabled the automatic inegration with babystepping by setting `override_set_gcode_offset: False` in the config there is a separate command to set the Live-Z value:

`SET_BUILD_SHEET_LIVE_Z`
This command lets you set the Live-Z offset for the current sheet and tool. It also allows setting Live-Z for sheets/tools that are not currently installed in the printer, this can be useful for front ends that want to provide a GUI for managing build sheets and allow any-time adjustment of the Live-Z offsets.
* `Z`
Set the absolute Live-Z offset for the installed sheet
* `Z_ADJUST`
Adjust the Live-Z offset for the installed sheet. One of `Z` and `Z_ADJUST` is required.
* `SHEET`
Select which sheet to adjust Live-Z for. This allows adjustments of a sheet not currently installed in the printer.
* `TOOL`
Select which tool to adjust Live-Z for. This allows adjustments of a tool that is not cuurrently selected.

## Toolchanger Support
The build sheet system needs to know which tool it currently selected. There is no agreed system for this in Klipper as an Extruder is no necessarily the same as a Tool. You are free to make up whatever tool names you want.

