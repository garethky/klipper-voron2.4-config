# AGENTS.md - Klipper Configuration Repository

## Overview
This is a Voron 2.4 config repo for experimental load cell probing work. 

## Workspace Structure
- This repo configurs and deploys code to a physical printer. The code for the printer is contained in two adjacent repos: 
  - **klipper**: This is the original project. Read @klipper-AGENTS.md for more details.
  - **kalico**: This is a hard fork of klipper. We will be porting the load cell probing features into kalico. Read @kalico-AGENTS.md for more details.
- The printer is running *kalico*. *klipper* is provided as a reference.

## 3D Printer Details
- The printer can be reached via `ssh pi@voron24.local`. Certificates are deployed to provide authentication.
- Code is deployed to the printer using `rsync` and testing is carried out there
- Logs are in the `~/printer_data/logs` directory on the printer. Of particular interest is `klipper.log` which will contain any errors or debug outputs.

## Architecture
- **Config files**: `printer_data/config/` - Printer configuration
- `machine.cfg` contains the basic definition of the printer
- `load_cell.cfg` contains load cell probing specific configuration
- Config is deployed using `rsync` to the `/home/pi/printer_data/config/` directory on the printer

## Code Style & Conventions
Since this repo is just config we don't usually write any code here.

## Refactoring Guidelines
When working on code in the adjacent kalico/klipper repos:

- **Encapsulation**: Move toward better encapsulation - make classes self-contained with minimal external dependencies
- **Break circular dependencies**: Constructor parameters should be primitive types/values, not references to other complex objects that create circular dependencies
- **Method extraction**: Extract complex logic into well-named methods first, then progressively internalize side effects (like logging) into those methods
- **Progressive refinement**: Refactor in small, testable steps rather than big rewrites
- **Naming**: Prefer shorter, clearer names that hint at side effects (e.g., `evaluate_probe()` over `should_accept_probe()`)
- **Consolidation**: Look for opportunities to merge helper classes into their primary consumer when the helper is single-use
- **Static methods**: Keep utility functions as static methods within the class that uses them to prevent them getting lost in future refactors

## Tasks
This repo contains a set of tasks in `.vscode/tasks.json`. These can be executed with the `vtr` command + a task name.
