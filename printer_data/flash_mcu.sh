sudo service klipper stop
sleep 5
cd klipper
ls -la /dev/serial/by-id/*
make flash FLASH_DEVICE=/dev/serial/by-id/usb-Klipper_stm32f446xx_2D002900085053424E363420-if00
sleep 5
ls -la /dev/serial/by-id/*
sudo service klipper start
