---
globs:
  - '../klipper/**'
---

# AGENTS.md - Klipper 3D Printer Firmware

## Overview
Klipper is 3D printer firmware combining general-purpose computer control with micro-controllers. This branch includes experimental load cell probing features.

## Build & Test Commands
- **Build MCU firmware**: `make` (requires .config file - use `make menuconfig` to create)
- **Build for specific platform**: Configure with `make menuconfig`, then `make`
- **Run all tests**: `python3 scripts/test_klippy.py -d out/ test/klippy/*.test`
- **Run single test**: `python3 scripts/test_klippy.py -d out/ test/klippy/load_cell.test`
- **Test file format**: Each `.test` file references a `.cfg` config file and contains DICTIONARY, CONFIG, and gcode commands

## Architecture
- **klippy/**: Python host software - main control logic, gcode parsing, motion planning
- **klippy/extras/**: Modular Python components for peripherals (sensors, probes, heaters, etc.)
- **klippy/kinematics/**: Motion system implementations (cartesian, corexy, delta, etc.)
- **src/**: C firmware for micro-controllers, compiled per-platform
- **scripts/**: Build tools, test runners, utilities for flashing and debugging
- **test/klippy/**: Regression tests with `.test` and `.cfg` file pairs

## Code Style & Conventions
- **License**: All new files must include GPLv3 copyright header (see existing files)
- **Python version**: Support both Python 2.7+ and 3.x (use compatible patterns like `izip`/`zip`)
- **Imports**: Group standard library first, then relative imports (`from . import module`)
- **Classes**: Explicitly inherit from object: `class Name(object):`
- **Naming**: snake_case for functions/variables, CapitalCase for classes
- **Config parsing**: Use `config.get()`, `config.getint()`, `config.getchoice()`, etc.
- **Error handling**: Use `raise config.error("message")` for config errors, `raise gcmd.error()` for gcode errors

## Source Control
This directory is a git repo. It also set up to use jj/jujutsu locally. We work in commit stacks, so chains of commits to implement a feature and tell a good story. There are some important jj bookmarks (and ths git branches):
- `master` - the main branch of the public klipper repo
- `pr-load-cell-tap-analysis` - this is a series of commits that contain the probing work yet to be accepted into to `master`.
- `pr-nozzle-z-thermal-adjust` - This is a PR to allow multiple z thermal adjust configurations
- `load-cell-probe-community-testing` - this is a public facing branch that includes additional work that testers are using for validation. This is the "contains everything" bookmark.
