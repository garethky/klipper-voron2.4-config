# garethky/klipper-voron2.4-config

This is the Klipper Config for my 300mm Voron 2.4. This repo has additional macros and other things that I'm developing.

## About this repo

This is the real actual config that I run on my, very customized, printer. I keep it all in git and deploy to the printer via `rsync`. That means I don't modify config files on my printer because they are always overwritten from here. This is pretty much always a work in progress. It's likely a good place to get ideas but **not** a good place to outright copy values for your printer. ***Use at your own risk.***

## Goals for this printer

* A printer that gets used for printing functional parts. I commonly print in ASA, PETG & Polycarbonate. The goal was a useful printer, not a hobby project, it just turned into a hobby project.
* Reliability, Repeatability & Usability -  I wanted to create something that is as easy to use as my Prusa MK3S. I'm still chasing this but its close now.
* Low Noise - loud printers are banned from my office
* Print Quality - I don't necessarily care about absolute maximum print speed

## About the Printer's Hardware

This is a Voron 2.4 built in early 2021. The X axis and Y tensioners have been upgraded to the parts released in 2022. It also has these mods:

* [GE5C Z joint](https://github.com/VoronDesign/VoronUsers/tree/master/printer_mods/hartk1213/Voron2.4_GE5C) by heartk with the IGUS bearings. This greatly reduced the "hunting" I had experienced during Quad Gantry Leveling and increased the repeatability. I regularly see variance less than 0.004mm.
* Bondtech LGX mounted with this mod: https://www.printables.com/model/240124-lgx-adapter-for-voron-mgn12-x-carrige
* A [Euclid Probe](https://euclidprobe.github.io/) mounted to the above carriage mount. Sightly customized dock arm because the one that works well is missing a magnet. I tried Klicky and liked it, this is just a more reliable design.
* ANNEX Engineering [Carabiner toolboard](https://github.com/Annex-Engineering/Annex_Engineering_PCBs/tree/master/carabiner-toolboard) mounted to the LGX with a custom adapter plate. I picked this board because it supports independent 12V power for fans. It is short on pins for the Steakthbuner LEDs but that is solved with a Y on one of the power lines. I'm not going CANBUS until I see a toolboard that does 12V fans and 24V stepper drivers.
* Stealthbuner running the Voron version of the E3D Revo. Very happy with this upgrade over the Afterburner!
* Custom carbon filter "backpack" that holds 7 pounds of carbon pellets in a removable filter. Uses 2 x 120mm low RPM Noctua fans and a HEPA filter. Very quiet and I smell nothing. Its not a design I would publish because of some usability quirks around mounting but I may design a smaller unit that I could see publishing info on.
* Mandala Rose Works cast aluminum build plate with an extra thermistor stuck through one of the empty holes to measure the temperature at the top of the bed.
* [Kenematic bed mounts](https://github.com/tanaes/whopping_Voron_mods/blob/main/kinematic_bed/README_v2_assembly.md) by whoppingchard. I was honestly fine before installing these but I had ordered them so...
* Custom 6mm Polycarbonate side panels, top and door. Custom door handle and hinges. The hinges allow the door to swing 270 degrees to be out of the way. The door also lifts off easily for maintenance or printing PETG & PLA.
* 4.3 inch touch screen running Klipper Screen mounted with [this mod](https://github.com/VoronDesign/VoronUsers/tree/master/printer_mods/jeoje/4.3_Inch_Touchscreen_Mount) by jeojo.
* Ti Rail backers on X and Y.

## Klipper Software Customization
* [Z Calibration](https://github.com/protoloft/klipper_z_calibration) by Protoloft
* [Frame Expansion](https://github.com/alchemyEngine/klipper_frame_expansion_comp) - honestly im still experimenting with this.
* Heat Soak - waits for the bed to be in thermal equilibrium before a print starts.
* Build Sheet Manager - tracks the "squish" of each of my build sheets and makes adjustments effortless. Works exactly like Prusa's "Live Z" system.
* "Klicky-probe.cfg" -  To handle the Euclid probe. This is my own fork, im not sure there is an authoritative source for this other than discord.

## Slicer Customization
* [Klipper Estimator](https://github.com/Annex-Engineering/klipper_estimator) - this fixes the print time estimates in the gcode to be accurate with the printers configuration and kinematics.
* [Klipper Cancel Object Preprocessor](https://github.com/kageurufu/preprocess_cancellation) - Makes it possible to cancel objects to potentially save a print

## Problems Experienced
I went through a long trial and error process to get reliable first layers. These were the contributing factors:

* MGN9 rails that I bought didn't have much preload, this allowed the entire tool head to rock rotationally around the X axis.
* My X axis was slightly twisted in the middle. I'm not sure if it came that way or if a head crash contributed to the problem. [Twisted X Extrusion](https://voron.dozuki.com/Guide/High+on+One+Side+and+Low+on+the+Other+(Twisted+X+Extrusion)/45) describes the problem well. Not having the sensor the same distance from the X axis as the nozzle means this error is unmeasurable and cant be compensated for. This is a design flaw that is common in a lot of printers. Its also the reason printers like the MK3S have such good first layer performance: their senors are aligned with the nozzle in the Y axis which turns out to be more important than the X.
* The dual MGN9 rail design of the X axis was over constrained. I believe the printer was designed this way to make up for cheap chinese MGN9 rails that have no preload. I loosened the bottom rail and that actually improved things. Switching over to a single MGN12 rail with appropriate preload (Honeybadger brand) solved the rotational slop in the X axis.

Converting to MGN 12 with preload (Honeybadger MGN12) + straightening the X aluminum extrusion solved the bulk of this and really transformed how repeatable my fist layers are.