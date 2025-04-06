sudo service klipper stop
cd klipper-ads1220/klipper
ls -la /dev/serial/by-id/*
make flash FLASH_DEVICE=/dev/serial/by-id/usb-Klipper_stm32f103xe_38FF6F063133433358400643-if00
ls -la /dev/serial/by-id/*
sudo service klipper start
