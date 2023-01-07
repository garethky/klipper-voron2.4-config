# Heat Soaking Macro

This is a macro that manages heat soaking in klipper. It can be used t get a bed or chamber up to temperature. In your print start macro, it can cut down on time spent waiting for static timers. It can also be canceled allowing you to abort the print during what is usually the longest part of the print start process.

## What do we mean by 'heat soaking'?
Usually we mean waiting for some part of the printer, that is not actively temperature controlled, to reach thermal equilibrium. Previous attempts at heat soaking usually required you to wait a fixed amount of time or specify an exact target temperature. Both of these approaches have problems. The time approach doesn't take into account the current thermal state of the printer. The temperature approach is prone to variation due to the heaters temperature (e.g. bed temps for PLA vs ABS), if the printers enclosure was open, the rooms temperature and so on.

This macro works in terms of rate of change of temperature. It will:
* Wait for the rate of change of the temperature to drop below a specified rate
* Optionally, wait for a minimum temperature to be reached

## Origin and Acknowledgements
This macro started life in [Klipper Interruptible heat soak](https://klipper.discourse.group/t/interruptible-heat-soak/1552/) on the klipper forums. I took @blalor's code and added the idea from [Add MAX_SLOPE capability to TEMPERATURE_WAIT](https://github.com/Klipper3d/klipper/pull/4796) to allow the heat soak to stop when a temperature sensor reaches thermal equilibrium. @mwu added in the ideas needed to pause an ongoing print so this can be used in a print start macro.

# How To Use
Include the heatsoak macro in your printers config after any overrides of `CANCEL_PRINT` and `RESUME`

```
[include heatsoak.cfg]
```

Start a heat soak by calling:

```
HEAT_SOAK SOAKER='temperature_sensor chamber'
```

You can cancel the heat soak at any time with:

```
CANCEL_HEAT_SOAK`
```

Here is an example that uses all the options which are described below:
```
HEAT_SOAK HEATER='heater_bed' TARGET=110 SOAKER='temperature_sensor chamber' SOAK_TEMP=45 RATE=0.25 TEMP_SMOOTH=6 RATE_SMOOTH=30 COMPLETE='SOAKING_COMPLETE' CANCEL='CANCEL_PRINT' TIMEOUT=90 HEATING_REPORT_INTERVAL=10 SOAKING_REPORT_INTERVAL=30
```

## Required Parameters
`SOAKER` - The full name of the temperature sensor that the macro will monitor. Usually `SOAKER=temperature_sensor chamber` or `SOAKER=temperature_sensor top_bed`. This is assumed to be a sensor that is not attached to a heater.

## Optional Parameters
* `HEATER` - Name of a Heater to set a temperature on. If specified the `HEATER` is set to the `TARGET` temperature and the command will wait until that temperature is reached before beginning the heat soak. The advantage of having `HEAT_SOAK` manage the heating is that the heating phase can also be canceled with `CANCEL_HEAT_SOAK`. Default: None
* `TARGET` - The temperature to set the `HEATER` to. The heating phase ends when the heater reaches this temperature. Default: None
* `SOAK_TEMP` - Minimum temperature that the `SOAKER` sensor must reach before the heat soak finishes. This will prolong the heat soak even if the target `RATE` is achieved. Default: 0.0
* `RATE` - This is the rate of temperature change that you would like the sensor to be below at the end of the heat soak, expressed in degrees C per minute. Default: 0.3
* `TEMP_SMOOTH` - Number of seconds of smoothing to apply to the soaker temperature. The reading from the `SOAKER` is smoothed using this value. Default: 4
* `RATE_SMOOTH` - Number of seconds of smoothing to apply to the soaker rate of temperature change. This usually needs to be quite a bit large than `TEMP_SMOOTH`. Default: 20
* `TIMEOUT` - The number of minutes before the soaking phase times out. Default: 30
* `CANCEL` - The macro to run when the heat soak times out or is canceled with `CANCEL_HEAT_SOAK`. Usually you would set this to your `CANCEL_PRINT` macro if running a print. Default: None
* `COMPLETE` - A macro to call when the heat soak completes successfully. Useful for notifications. It is strongly recommended that you do not move the toolhead in this macro without reading [this warning](#be-careful-with-COMPLETE). Default: None
* `HEATING_REPORT_INTERVAL` - The heater temperature will be logged to the console at this interval in seconds. Default: 2
* `SOAKING_REPORT_INTERVAL` - The soaking temperature rate of change will be logged to the console at this interval in seconds. Default: 5

## Suggested Settings
For heat soaking a printer bed you want a thermal sensor that is installed into a hole drilled through the bed and in contact with the build sheet or magnet. The stock setting work pretty well for this.

```
HEAT_SOAK SOAKER='temperature_sensor top_bed'
```

For a chamber you might require a minimum temperature and a lower rate of change. `RATE_SMOOTH` and `RATE` are related, the lower the rate of change you want to reliably detect the longer the `RATE_SMOOTH` needs to be:

```
HEAT_SOAK SOAKER='temperature_sensor chamber' SOAK_TEMP=40 RATE=0.1 RATE_SMOOTH=30
```

This heat soak will end when the chamber is above 40C and the chamber temperature has gone up less than 0.1C over the last 30 seconds.

# Heat Soaking as part of `PRINT_START`
The recommended approach is to split your `PRINT_START` macro into two macros: a `PRINT_WARMUP` and a `PRINT_START`. Then call both of these macros from your slicer's startup gcode. The warmup macro does the initial startup routine and ends with the call to `HEAT_SOAK`. The call to `HEAT_SOAK` must be the **last** line of the `PRINT_WARMUP`. Then `PRINT_START` performs post heat-soak tasks and starts the actual print. You can read more about why we recommend this [here](#why-the-split-PRINT_START?) if you are curious.

```
[gcode_macro PRINT_WARMUP]
description: Perform initial homing and heating tasks
gcode:
    {% set EXTRUDER_TEMP = params.EXTRUDER_TEMP | default(190) | float %}
    {% set BED_TEMP = params.BED_TEMP | default(60) | float %}

    # Homing, QGL, pre-warming print nozzle etc.
    M104 S{EXTRUDER_TEMP * 0.75}        # set extruder temperature to 75%
    M140 S{BED_TEMP}                    # set bed temperature
    G32                                 # home printer

    # wait for the print bed to reach thermal equilibrium
    HEAT_SOAK HEATER='heater_bed' TARGET={BED_TEMP} SOAKER='temperature_sensor top_bed'

[gcode_macro PRINT_START]
description: perform calibration and get ready to print
gcode:
    {% set EXTRUDER_TEMP = params.EXTRUDER_TEMP | default(190) | float %}
    {% set BED_TEMP = params.BED_TEMP | default(60) | float %}

    # For safety, in case some old prints don't call PRINT_WARMUP:
    # if not homed, perform homing, check that the bed is hot etc.
    {% if not 'xyz' in printer.toolhead.homed_axes %}
        G32                             ; home all axes if not homed
    {% endif %}
    M190 S{BED_TEMP}

    # Mesh bed leveling and auto calibrate Z, final nozzle heating etc.
    # prime nozzle
```

Then in your slicer make this your startup GCode (sample from Prusa Slicer):

```
PRINT_WARMUP EXTRUDER_TEMP=[first_layer_temperature] BED_TEMP=[first_layer_bed_temperature]
PRINT_START EXTRUDER_TEMP=[first_layer_temperature] BED_TEMP=[first_layer_bed_temperature]
```

`HEAT_SOAK` will pause the print when it runs at the end of `PRINT_WARMUP` and wont resume the print until the heat soak is complete. When complete it will resume the print and `PRINT_START` will run.

# Additional Macros & Overrides

* `CANCEL_HEAT_SOAK` - Cancels an in-progress `HEAT_SOAK` and runs the cancel callback if it is defined
* `STOP_HEAT_SOAK` - Stops any in-progress `HEAT_SOAK` without running any callbacks
* `HEAT_SOAK_RESUME ON_RESUME=_BASE_RESUME` - Macro that resumes the print if
    * In the heating phase, tells `HEAT_SOAK` to shortcut the soaking phase when heating is complete.
    * In the soaking phase the heat soak is stopped immediately, any complete callback is run.
    * Runs the supplied `ON_RESUME` macro if the print is supposed to resume.
* `RESUME` - the RESUME macro is overridden to provide additional support for `HEAT_SOAK` by calling `HEAT_SOAK_RESUME`. If you want to use your own override you are free to use `HEAT_SOAK_RESUME` to get back the same behavior.


# For The Adventurous User

## Why the split PRINT_START?
One of the difficulties with klipper macros is that the macro itself cannot stop the control flow to wait for something. `HEAT_SOAK` does pause the print, but that only stops the next line of the print file from executing. If you just put `HEAT_SOAK` in the middle of you `PRINT_START` macro, the macro would continue to execute past the `HEAT_SOAK` call. Because of this you need to end your `PRINT_START` at the call to `HEAT_SOAK` so the control flow yields back to the printer, which then pauses the print.

More than likely you want to run some additional startup code after the heat soak finishes, like mesh bed leveling or heating the extruder. Hence the split into 2 macros. The second one runs after `HEAT_SOAK` resumes the print.

## Be careful with `COMPLETE`

An alternative is to do the remaining `PRINT_START` work in the `COMPLETE` macro. You still have to split the `PRINT_START` macro up but you could call 1 macro from your sliver. We got this to work but it comes with a bunch of headaches and surprises:
* Passing parameters to `COMPLETE` is difficult to do correctly and almost impossible to debug
* 

We tried using callbacks as a mechanism for continuing the print but they had downsides when mixed with pause/resume, see [this issue](https://github.com/garethky/klipper-voron2.4-config/issues/3).

If you want to use the `COMPLETE` to perform tasks like homing you should be aware that the `RESUME` macro will be called **after** `COMPLETE`. This will reset any homing, z-calibration etc. that you perform. `RESUME` will also move the toolhead back to where it was when heat soak paused the print which could cause a crash. You can overwrite the setting stored on `PAUSE` with:

```
SAVE_GCODE_STATE NAME=PAUSE_STATE
```

Just be sure you understand the consequences of overwriting this state as it also overwrites things like relative vs absolute moves.
