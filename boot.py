# boot.py -- run on boot to configure USB and filesystem
# Put app code in main.py

import machine
import pyb

# pyb.main('main.py') # main script to run after this one
# pyb.usb_mode('VCP+MSC') # act as a serial and a storage device
# pyb.usb_mode('VCP+HID') # act as a serial device and a mouse
# import network
# network.country('US') # ISO 3166-1 Alpha-2 code, eg US, GB, DE, AU or XX for worldwide
# network.hostname('...') # DHCP/mDNS hostname

# Set REPL to use Bluetooth UART (HC-05 on UART1)
pyb.repl_uart(pyb.UART(1, 115200, timeout=100))
# pyb.repl_uart(None) # disable REPL on Bluetooth UART
