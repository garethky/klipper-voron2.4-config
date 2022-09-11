# Heat Soaking Macro

This is a macro that manages heat soaking in klipper. It can be used t get a bed or chamber up to temperature. In your print start macro, it can cut down on time spent waiting for static timers. It can also be canceled allowing you to abort the print during what is usually the longest part of the print start process.

# What do we mean by 'heat soaking'?
Usually we mean waiting for some part of the printer, that is not actively temperature controlled, to reach thermal equilibrium. Previous attempts at heat soaking usually required you to wait a fixed amount of time or specify an exact target temperature. Both of these approaches have problems. The time approach doesn't take into account the current thermal state of the printer. The temperature approach is prone to variation due to the heaters temperature (e.g. bed temps for PLA vs ABS), if the printers enclosure was open, the rooms temperature and so on.

This macro works in terms of rate of change of temperature. It will:
* Wait for the rate of change of the temperature to drop below a specified rate
* Optionally, wait for a minimum temperature to be reached

## Origin and Acknowledgements
This macro started life in [Klipper Interruptible heat soak](https://klipper.discourse.group/t/interruptible-heat-soak/1552/) on the klipper forums. I took @blalor's code and added the idea from [Add MAX_SLOPE capability to TEMPERATURE_WAIT](https://github.com/Klipper3d/klipper/pull/4796) to allow the heat soak to stop when a temperature sensor reaches thermal equilibrium. @mwu added in the ideas needed to pause an ongoing print so this can be used in a print start macro.

## How To Use
Start a heat soak by calling:
`HEAT_SOAK SOAKER='temperature_sensor chamber'`

You can cancel the macro at any time with:
`CANCEL_HEAT_SOAK`

Here is an example that uses all the options:
```
HEAT_SOAK HEATER='heater_bed' TARGET=110 SOAKER='temperature_sensor chamber' SOAK_TEMP=45 RATE=0.25 TEMP_SMOOTH=6 RATE_SMOOTH=30 CONTINUE='PRINT_START_CONTINUE' CANCEL='CANCEL_PRINT' TIMEOUT=90 HEATING_REPORT_INTERVAL=10 SOAKING_REPORT_INTERVAL=30
```

### Required Parameters
`SOAKER` - The full name of the temperature sensor that the macro will monitor. Usually `SOAKER=temperature_sensor chamber` or `SOAKER=temperature_sensor top_bed`. This is assumed to be a sensor that is not attached to a heater.

### Optional Parameters
* `HEATER` - Name of a Heater to set a temperature on. If specified the `HEATER` is set to the `TARGET` temperature and the command wait until that temperature is reached before beginning the heat soak. The advantage of having `HEAT_SOAK` manage the heater is that the heating phase can also be canceled with `CANCEL_HEAT_SOAK`. Default: None
* `TARGET` - The temperature to set the `HEATER` to. Default: None
* `SOAK_TEMP` - Minimum temperature that the `SOAKER` sensor must reach before the heat soak finishes. This will prolong the heat soak even if the target `RATE` is achieved. Default: 0.0
* `RATE` - This is the rate of temperature change that you would like the sensor to be below at the end of the heat soak, expressed in degrees C per minute. Default: 0.3
* `TEMP_SMOOTH` - Number of seconds of smoothing to apply to the soaker temperature. The reading from the `SOAKER` is smoothed using this value. Default: 4
* `RATE_SMOOTH` - Number of seconds of smoothing to apply to the soaker rate of temperature change. This usually needs to be quite a bit large than `TEMP_SMOOTH`. Default: 20
* `TIMEOUT` - The number of minutes before the heat soaking command times out. Default: 30
* `CANCEL` - The macro to run when the heat soak times out or is manually canceled. Usually you would set this to your `CANCEL_PRINT` macro if running a print. Default: None
* `CONTINUE` - A macro to call when the heat soak finishes successfully, see the "Using With `PRINT_START` section for more details". Default: None
* `HEATING_REPORT_INTERVAL` - The heater temperature will be logged to the console at this interval in seconds. Default: 2
* `SOAKING_REPORT_INTERVAL` - The soaking temperature rate of change will be logged to the console at this interval in seconds. Default: 5

### Suggested Settings
For heat soaking a printer bed you want a thermal sensor that is installed into a hole drilled through the bed and in contact with the build sheet or magnet. The stock setting work pretty well for this.
`HEAT_SOAK SOAKER='temperature_sensor top_bed' `

For a chamber you might require a minimum temperature and a lower rate of change. `RATE_SMOOTH` and `RATE` are related, the lower the rate of change you want to reliably detect the longer the `RATE_SMOOTH` needs to be:

```
HEAT_SOAK SOAKER='temperature_sensor chamber' SOAK_TEMP=40 RATE=0.1 RATE_SMOOTH=30
```

This heat soak will end when the chamber is above 40C and the chamber temperature has gone up less than 0.1C over the last 30 seconds.

### Using with `PRINT_START` and other macros
One of the difficulties with klipper macros is that they cannot the control flow of the macro to wait for something. This macro gets around this problem by using a `delayed_gcode` macro. But because of this you need to stop your `PRINT_START` at the call to `HEAT_SOAK`. The parameter `CONTINUE` is used to continue the print when the heat soak finishes.

This is an example of using `HEAT_SOAK` as part of a `PRINT_START` process. Usually we pass some parameters to `PRINT_START` and you might need to pass these on. Please carefully note the `-%}` and `{%-` that wrap the `CONTINUE` variable, these are required to remove any whitespace or newlines around the continue code. Also note the use of quotes in `CONTINUE='{CONTINUE}'`, they are required to have this parsed correctly by klipper.

```
[gcode_macro PRINT_START]
gcode:
    {% set EXTRUDER_TEMP = params.EXTRUDER_TEMP | default(190) | float %}
    {% set BED_TEMP = params.BED_TEMP | default(60) | float %}

    {% set CONTINUE -%}
         PRINT_START_CONTINUE EXTRUDER_TEMP={EXTRUDER_TEMP}
    {%- endset %}

    # wait for the print bed to reach thermal equilibrium
    HEAT_SOAK HEATER='heater_bed' TARGET=95 SOAKER='temperature_sensor top_bed' CONTINUE='{CONTINUE}'

[gcode_macro PRINT_START_CONTINUE]
gcode:
    {% set EXTRUDER_TEMP = params.EXTRUDER_TEMP | float %}
    M109 S{EXTRUDER_TEMP}               # Wait for nozzle to finish heating
```

