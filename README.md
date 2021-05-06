# klipper-voron2.4-config
Klipper Config for my Voron 2.4


# Klipper "Extra" Development Quick Start

I'm developing on my Mac and deploying to Raspberry Pi. I do my prototyping in this project rather than a fork of the Klipper project. This lets me keep my Klipper fork clean and work on multiple plugins at the same time without having to worry about how the git history will look.

## The Code -> Deploy -> Test loop
1. Write python code in an "my_extra.py" file
    This step is pretty self explanatory. I only have to keep the extras I'm building in this project and as a bonus I get a working printer.cfg to go along with it. 

1. Use rsync to copy the python code to the Pi
    To do this without having to type in a password, set up an SSH certificate on the Mac so you get authorized by SSH automatically. Follow these instructions: https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md

    Then you can run this command from the Mac to deploy your "extras:"
    ```
    rsync -iahp --exclude=\".*\" ./klipper/klippy/extras/* pi@your-pi.local:/home/pi/klipper/klippy/extras/
    ```

1. Restart the Klipper service on the Pi
    Klipper wont pick up your changes with a regular `RESTART` or `FIRMWARE_RESTART` command. You have to restart the service to get the new code parsed again. You do this on the Pi by running:
    ```
    sudo service klipper restart
    ```

    But that requires logging into the pi and typing your password far too often for a development process. So instead we can allow the `pi@` user to run the `service` command without a password: follow rhe answer here: https://stackoverflow.com/questions/21659637/how-to-fix-sudo-no-tty-present-and-no-askpass-program-specified-error
    ```
    sudo visudo
    ```

    and then add a line like this at the end:
    ```
    pi ALL = NOPASSWD: /sbin/service
    ```

    Then on the Mac you can run this from the command line to restart Klipper:
    ```
    ssh pi@your-pi.local 'sudo service klipper restart'
    ```

## Automation
You can drop everything about into a config file for VS Code and run it all automatically as your build command. 1 button deploy and restart. See the VSCode project in this repo for an example.