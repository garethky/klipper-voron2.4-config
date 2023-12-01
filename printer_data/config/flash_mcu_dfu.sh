sudo service klipper stop
cd klipper
ls -la /dev/serial/by-id/*
make flash FLASH_DEVICE=0483:df11
ls -la /dev/serial/by-id/*
sudo service klipper start
