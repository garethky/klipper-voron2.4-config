# Build Sheets For Klipper

* Klipper discourse thread: [Build Sheet Manager & “Adjust Live Z”](https://klipper.discourse.group/t/build-sheet-manager-adjust-live-z/4013)

**Requirements:**
* You have [[save_variables]](https://www.klipper3d.org/Config_Reference.html#save_variables) set up
* You need to call the `APPLY_BUILD_SHEET_ADJUSTMENT` in your `PRINT_START` macro ***after*** you calibrate your Z offset. This is when the sheet offset is applied.
* Last but most important: Your `PRINT_START` macro must set your Z Offset. You can do this with a plugin like [CALIBRATE_Z](https://github.com/protoloft/klipper_z_calibration). Or, you can add a line to your `PRINT_START` to reset the Z offset to the correct value for your printer: `SET_GCODE_OFFSET Z=0.0`. This macro doesn't try to keep track of the state of the z offset between prints, that's on you. If you don't do this the `APPLY_BUILD_SHEET_ADJUSTMENT` call will apply the same adjustment multiple times and you will crash your printer.

### Commands

#### INSTALL_BUILD_SHEET
Create or install a build sheet. If the sheet doesnt exist it will be created.
If the sheet already exists its will replace the currently installed build
sheet.
- `NAME` name of the build sheet
- `OFFSET` optional size of the offset for the sheet in mm

#### SHOW_BUILD_SHEET
Shows the currently installed build sheet

#### SET_BUILD_SHEET_OFFSET
Set the offset of the current build sheet
- `OFFSET` optional size of the offset for the sheet in mm

#### RESET_BUILD_SHEET_OFFSET
Set the offset of the current build sheet to 0.0

#### APPLY_BUILD_SHEET_ADJUSTMENT
This needs to go into your buint start routine to activate the offset of the
current sheet.
