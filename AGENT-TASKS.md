# 1. Import Commits from klipper

## 1. Fetch from the remote
jj git fetch --remote klipper

## 2. Identified commits that need duplicating
### Previously committed stuff:
jj log -r 'cb0c38f::388fe1b|eb43b20|8d7e487' 
### WIP in JJ:
jj log -r 'eb220e0d::6c0f50a0'

### Everything combined:
jj log -r 'cb0c38f::388fe1b|eb43b20|8d7e487|eb220e0d::6c0f50a0'

## 3. Duplicate them onto main
jj duplicate -d main -r 'cb0c38f::388fe1b|eb43b20|8d7e487|eb220e0d::6c0f50a0'


# 2. Refactor for Kalico's version of probe.py

In the `kalico` repo I have imported the load cell changes up to the `jj` bookmark `pr-load-cell-tap-analysis`. These changes are not going to work correctly in kalico because kalico did not accept some critical changes from klipper. Many objects and classes that klipper implemented to extend probing are missing in Kalico. Kalico does not want these objects added to its codebase. Instead, the code must be refactored to work in the Kalico codebase. I want you to ask the oracle about how the code can be adapted so that it can work with kalico's existing `probe.py` code. Propose a plan for a refactoring to make this work.

Reference Material:
* `klippy/extras/probe.py` and `klippy/extras/homing.py`. I would read both the version in klipper and in kalico to understand the differences between the two.
* Read an example of another probe implemented in both projects, such as `klippy/extras/probe_eddy_current.py`

Issues that need to be addressed:
* The classes: `probe.ProbeSessionHelper`, `probe.ProbeParameterHelper`, `probe.ProbeCommandHelper`, `probe.ProbeOffsetsHelper` do not exist in Kalico. 
* The `probe.ProbeSession` class and the concept of tracking a "probing session" does not exist in Kalico. The closest analog is the `multi_probe_begin` and `multi_probe_end` methods in the `PrinterProbe` class.
* `probe.lookup_minimum_z` and `probe.LookupZSteppers` does not exist in Kalico. You should look at how other probes get by without this.
* `klippy/extras/load_cell_probe.py` adds a new concept of retrying probes that fail to achieve sufficient quality. The `TapLocation` class, `STRATEGY_CHOICES` and the machinery to use them should be refactored into the `probe.py` file. I expect this can be done in a way that is backwards compatible for all existing probe types and won't require any code changes to them.

Please ask clarifying questions if you don't understand how something is used or how to resolve an issue. I can point you to additional reference material as needed.


# 3. Move tap retry logic to probe.py
In `kalico\klippy\extras\load_cell_probe.py` there is functionality to retry probes if they don't have sufficient quality with several different retry behaviours implemented. I want you to move that functionality into `kalico\klippy\extras\probe.py`.

I would like any probe implementation to be able to, optionally, return an "is_good" flag from probing_move. This shouldn't require changes to existing probes (other than load_cell_probe). This will get the duplicated logic for performing `retract` moves out of `load_cell_probe.py`. It should also mean that the loop inside `TapSession.run_probe()` is moved into `probe.py`.

When you do this you will realize that the `LOAD_CELL_CLEANUP` command would no longer make a lot of sense in `load_cell_probe`, since that module alone could no longer do a retry loop. This functionality should also be moved into `probe.py`. This will stop `load_cell_probe` from having to determine the minimum z value and delete a bunch of duplicated code there. You can rename `LOAD_CELL_CLEANUP` to `NOZZLE_CLEANUP` for the version in `probe.py`.

First consult the oracle and come up with a plan to perform these refactorings.


# 4. Cleanup
Now that cleanup is implemented in probe.py, we can re-arrange the history in jj so that it was never implemented in load_cell_probe.py. Then we can edit out all the code in load_cell_probe.py that had anyhting to do with retries and cleanup.
