sudo service klipper stop
cd klipper
ls -la /dev/serial/by-id/*
make flash FLASH_DEVICE=/dev/serial/by-id/usb-katapult_stm32f446xx_240050000F51383438343939-if00
ls -la /dev/serial/by-id/*
sudo service klipper start