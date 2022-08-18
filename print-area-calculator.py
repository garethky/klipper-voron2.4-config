#!/usr/local/opt/python/libexec/bin/python
# PRUSA SLICER tool to calculate the maximum extents of a print
# Written by Gareth Farrington
import sys, os, re, math

sourceFile = sys.argv[1]

backupFile = sourceFile + ".print-area-calculator.bak"

absolute_mode = None
max_x = max_y = min_x = min_y = None

# Read the ENTIRE g-code file into memory
with open(sourceFile, "r") as f:
    lines = f.readlines()

    # look for movement commands in all lines
    for line in lines:
        line = line.lstrip()

        if (line.startswith('G91')):
            absolute_mode = False
        if (line.startswith('G90')):
            absolute_mode = True

        # if the printer is moving in absolute mode and this ine is a movement command:
        if (absolute_mode == True and line.startswith('G1')):
            # split the command into blocks
            for block in line.split():
                # look for the X and Y blocks and if found update appropriate tracking variables
                if (block[0] == 'X'):
                    x_value = float(block[1:])
                    min_x = min(min_x or x_value, x_value)
                    max_x = max(max_x or x_value, x_value)
                elif (block[0] == 'Y'):
                    y_value = float(block[1:])
                    min_y = min(min_y or y_value, y_value)
                    max_y = max(max_y or y_value, y_value)
    
replacements = {
    "$min_x$": str(min_x),
    "$max_x$": str(max_x),
    "$min_y$": str(min_y),
    "$max_y$": str(max_y),
    } # define desired replacements here
replacements = dict((re.escape(k), v) for k, v in replacements.items()) 
pattern = re.compile("|".join(replacements.keys()))
processed_gcode = pattern.sub(lambda m: replacements[re.escape(m.group(0))], "".join(lines))

# write all input lines to the output file
os.rename(sourceFile, backupFile)
with open(sourceFile, "w") as of:
    of.write(processed_gcode)