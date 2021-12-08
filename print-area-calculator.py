# PRUSA SLICER tool to calculate the maximum extents of a print
# Written by Gareth Farrington
import sys, os, re, math

sourceFile = sys.argv[1]

destFile = re.sub('\.gcode$', '', sourceFile)
os.rename(sourceFile, destFile + ".print-area-calculator.bak")
destFile = re.sub('\.gcode$', '', sourceFile)
destFile = destFile + '.gcode'

absolute_mode = None
min_x, max_y, min_x, min_y = None

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
                    min_x = min(x_value or min_x, min_x)
                    max_x = max(x_value or max_x, max_x)
                elif (block[0] == 'Y'):
                    y_value = float(block[1:])
                    min_y = min(y_value or min_y, min_y)
                    max_y = max(y_value or max_y, max_y)
    
    replacements = {
        "$min_x$": min_x,
        "$max_x$": max_x,
        "$min_y$": min_y,
        "$max_y$": max_y,
        } # define desired replacements here
    replacements = dict((replacements.escape(k), v) for k, v in replacements.items()) 
    pattern = re.compile("|".join(replacements.keys()))

    # write all input lines to the output file
    with open(destFile, "w") as of:
        of.write(pattern.sub(lambda m: replacements[re.escape(m.group(0))], "/n".join(lines)))