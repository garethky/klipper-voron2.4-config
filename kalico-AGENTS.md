---
globs:
  - '../kalico/**'
---

# Kalico - 3D Printer Firmware (Klipper fork)

## Overview
This is a hard fork of `klipper`. 

## Build/Test/Lint Commands
- **Test all**: `pytest -n auto` (or `py.test -n auto`)
- **Test single file**: `pytest test/test_imports.py`
- **Lint**: `ruff check --fix` (auto-fix) or `ruff format` (format code)
- **Build firmware**: `make` (after `make menuconfig` to configure board)
- **Pre-commit hooks**: `pre-commit run --all-files`

## Architecture
- **klippy/**: Python host software - core modules (printer.py, mcu.py, toolhead.py, gcode.py)
- **klippy/extras/**: Feature modules (heaters, probes, TMC drivers, input_shaper, etc.)
- **klippy/kinematics/**: Motion systems (cartesian, corexy, delta, etc.)
- **klippy/plugins/**: User plugins directory (git-untracked)
- **src/**: C firmware for microcontrollers (compiled to klipper.elf)
- **scripts/**: Utilities (console.py, calibration tools, install scripts)

## Code Style
- **Python 3.9+** (no Python 2), line length **80 chars**, **4-space indent**
- Use **absolute imports** from klippy (`from klippy import mcu`) or relative (`from . import probe`)
- **No bare except**, use specific exceptions; **logging** over print statements
- **Type hints** encouraged (PEP 563); avoid mutable defaults (`B006`)
- Follow **ruff** rules (see pyproject.toml); ignore E501/E722/E741/F841 as configured
- C code: **gnu11**, function sections, LTO optimization
- Do not write excessive inline comments. The code should speak for itself
- Do not use blank lines in method. If the method needs vertical separation, maybe it needs breaking up into sub-methods

## Source Control
The `kalico` directory is a separate repository. **ALWAYS use `jj` commands, NEVER use `git` commands** in this repo:
- The `jj` command line documentation is here: https://jj-vcs.github.io/jj/latest/cli-reference/
- `jj log` not `git log`
- `jj show <revision>` not `git show`
- `jj diff --git` to get a git formatted diff, which you can correctly understand
- `jj new -m "message"` to create commits

We work in commit stacks, so a chain of commits to implement a feature and tell a good story. There are some important jj bookmarks:
- `main` - the main branch of the public kalico repo
- We work on a stack of commits that is on top of the `main` bookmark. You can see where in the stack the workspace currently is with `jj log`
- We often move up and down the commit stack to do work. Because rebase in jj is fully automatic ths workflow is frictionless vs git.
