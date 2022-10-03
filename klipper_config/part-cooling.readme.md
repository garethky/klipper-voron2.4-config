#part-cooling.readme.md



## Simple Adjustments

The ADJUST parameter can be used to shift the existing fan values by a fixed amount. This applied across the whole range of values. If values

0 |      [========]    | 100

M106.1 ADJUST=20

0 |          [========]| 100

M106.1 ADJUST=-20

0 |  [========]        | 100

# Complex Adjustments

The ADJUST parameter also has a mode that treats the fan rage as if it was a rubber band. You can grab the rubber band at 2 places and pull on it in either direction. This can stretch the 


0 |   [=======]        | 100

M106.1 ADJUST=20->20|60->80

This maps the value 20 to 20, meaning no change. And it maps the value 60 to 80. The stretches the fan range from 20->60 to 20->80.

0 |   [===========]    | 100

You can do the same as the simple adjust parameter with:
M106.1 ADJUST=20
M106.1 ADJUST=0->20|100->120

M106.1 ADJUST=-20
M106.1 ADJUST=0->-20|100->80

The default values for adjust are:
M106.1 ADJUST=0->0|100->100

If you omit one side of the pair, you will get the default values for that side:
M106.1 ADJUST=|100->80

M106.1 ADJUST=20->10|

The left side of the arrow must be between 0 and 100, the right side can be a value from -100 to +200. Fan output values larger than 100 or less than 0 are clipped to the 0-100 rage after the fan speed is computed.

Values 

### The value 0 is Special
0 is how the slicer tells the printer to turn the fan off. Your slicer might also also use M107 but that is optional. The value 0 is not changed with the ADJUST parameter unless the "ALWAYS" parameter is set to "ON".


