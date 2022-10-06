# ADJUST_M106 - Comprehensive Part Cooling Modifier

This is a tool for changing the behavior of the M106 command. It allows you to change the fan speed for the rest of the print in a way that works smoothly with slicers that vary the fan speed throughout the print.

## ADJUST_M106 Command
All of the parameters of ADJUST_M106 are optional. If a parameter is not specified no changes occur to that parameter (except for ENABLE).

* `ADJUST` - Either a number or N->N|N->N syntax for mapping fan speed ranges (more on this below). Numbers are percentages, floating point is supported. Default: 0.
* `ALWAYS` - one of "ON", "OFF" or "SLICER". Default is "SLICER". ON forces the fan to always run, it also allows mapping the 0 value to another value. OFF shuts the fan off. SLICER returns the fan to slier control.
* `ENABLED` - true/false value. Default is false. If you don't specify this parameter it gets set to true. This allows adjustments to take effect immediately without having to explicitly add ENABLED=true. Toggling `ENABLED` on/off will changed the fan speed between the overridden value and the last slicer provided value.
* `MIN` - The minimum allowed fan speed value. Fan speeds lower than this value will be raised to MIN. This is applied after any adjustment. Note that 0 fan speed is always allowed unless ALWAYS is set to ON. Then, the minimum fan speed is the larger of the fans `off_below` value and MIN. Default: 0
* `MAX` - The maximum allowed fan speed value. Fan speeds larger than this value will be set to MAX. This is applied after any adjustments Default: 100
* `FAN` - This is the name of the config section containing the part cooling fan, used to find the `off_below` value. Default is `'fan'`.

Sample call with all parameters:

```
ADJUST_M106 ADJUST=-15 ALWAYS=ON ENABLED=false MIN=10 MAX=95 FAN='temperature_fan my_fan'
```

## Additional Macros & Overrides

* `SHOW_M106` - displays the detailed state of M106 adjustments
* `RESET_M106` - Resets all `ADJUST_M106` parameters, except for the `FAN` value, to the their defaults and turns off any override.
* `M106` - This macro overrides M106 to permit adjustments
* `M107` - This macro overrides M107 to permit the always on functionality to work correctly.

## Use of the ADJUST parameter
This section covers how the ADJUST parameter works in detail.

### Simple Adjustments
A single number can be used to increase or decrease the fan speed by that percentage value value. 

```
ADJUST_M106 ADJUST=20
```

This raises all fan speeds by 20%. Speed requests above 80% will become 100%. Speed requests lower than 20% will all become 20%.

Negative numbers lower the fan speed:

```
ADJUST_M106 ADJUST=-20
```

### Complex Adjustments

The ADJUST parameter also has a mode that treats the fan rage as if it was a rubber band. You can grab the rubber band at 2 places and pull each point in either direction.

The syntax is 2 pairs of numbers separated by a pipe `|`. The left side is the mapping of the lower value and the right side is the mapping of the upper value. Each mapping is a pair of numbers separated by an arrow `->`.

```
ADJUST_M106 ADJUST=20->25|60->80
```

This command maps 20% fan speed to 25% and 60% fan speed to 80%. The effect is to slightly increase the base cooling to 25% fan speed but to provide increased part cooling of 80% when the slicer asks for 60%. 

ADJUST_M106 smoothly maps all input values between 0% and 100% to an output range of 0% to 100%:
* Numbers between 20% and 60% are mapped smoothly to 25%->80%.
* Numbers between 0% and 20% are mapped smoothly to the range 0%->25%
* Numbers between 60% and 100% are mapped to the range 80%->100%

### Mapping to 'imaginary' fan values
The target range of the mapping can be anywhere between -100% and 200%. This is actually how simple adjustments work:

```
ADJUST_M106 ADJUST=20
```

Is the same as:

```
ADJUST_M106 ADJUST=0->20|100->120
```

If you map to a range outside the real 0% to 100% range of the fan the values will be smoothly mapped onto that imaginary range but then they will be clipped to fit the real 0% to 100% range. So the real output range of the above example is 20% to 100%.

### Partial Mappings

The default values for the individual mappings are:

```
ADJUST_M106 ADJUST=0->0|100->100
```

If you omit one side of the pair of mappings, you will get the default values for that side. Both of these are valid ways to apply an adjustment:

```
ADJUST_M106 ADJUST=|100->80
ADJUST_M106 ADJUST=0->20|
```

### The value 0 is Special

0 is how the slicer tells the printer to turn the fan off. (Your slicer might also also use M107 but that is optional.) The value 0 is not changed with the ADJUST parameter unless the "ALWAYS" parameter is set to "ON". Mapping definitions allow the value 0 to be used for convenience but it is ignored so long as the slicer is in control of the fan on/off setting.

## `ADJUST_M106` Cookbook
This is a cookbook of part cooling issues and a sample recipe for solving them with `ADJUST_M106`.

### Increase cooling for bridges
The slicer set the maximum cooling speed for bridges to 60%. You want that to be 80%.
```
ADJUST_M106 ADJUST=|60->80
```

### Increase the base fan speed
The slicer set the fan to always on speed at 15%. You want the fan always on at 35%.

```
ADJUST_M106 ADJUST=15->35|
```

### Make the fan run at exactly 35%
Dynamic cooling is on and you want to just force the fan to run at a single speed for the rest of the print, specifically 35%:

```
ADJUST_M106 ADJUST=0->35|100->35 ALWAYS=ON
```

### Map the fan range above the `off_below` value to 0%-100%
Lets say your cooling fan is `off_below` 8%. You want 0% in the slicer to shut the fan off but 1% to 100% in the slicer mapped smoothly to the fans 8% to 100% range:

```
ADJUST_M106 ADJUST=0->8|
```

### Force the fan on
The slicer isn't set to have the fan always on, but you want some cooling all the time. Specifically you want a minimum of 25%.

```
ADJUST_M106 MIN=25 ALWAYS=ON
```

### Disable the Fan
Part cooling is warping your part and you want the fan to stop running for the rest of the print

```
ADJUST_M106 ALWAYS=OFF
```

### Increase cooling by layer height
You want to print a fan tuning tower, increasing part cooling by 10% every 25 layers. Example for Prusa Slicer's layer change GCocde:

```
ADJUST_M106 ADJUST={(layer_z % 25) * 10}
```

### Adjust cooling with chamber temperature
You are running an enclosed printer that has chamber temps between 30C and 60C. You would like to increase the fan speed by 20% across that temp range. You can do this with a background task that checks the temp and adjusts the fan:

```
TODO
```

