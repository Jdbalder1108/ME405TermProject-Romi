# Instructions for usage:
# 1) Use a Nucleo with nothing else plugged into it.
# 2) Disconnect the USB cable from your computer but
#    leave it plugged into the Shoe of Brian.
# 3) Connect the Bluetooth module to the Nucleo
#    BT TX  -> Nucleo UART1 RX (PB7 on Shoe of Brian)
#    BT RX  <- Nucleo UART1 TX (PB6 on Shoe of Brian)
#    BT VCC <- Nucleo 5V (on Shoe of Brian)
#    BT GND <- Nucleo GND (on Shoe of Brian)
# 4) While holding down the enable button on the
#    Bluetooth module plug in the USB cable to your
#    laptop. Continue holding down the enable button
#    until you get a very slow blink on the Bluetooth
#    module's LED (about 2 sec on / 2 sec off).
# 5) Modify the editable parameters listed below to
#    select desired UART settings, module name, and
#    password. Choose a name and password unique for
#    your lab group.
# 6) Transfer the code to the Nucleo and run the code
#    from PuTTY to send the configuration to the module
# 7) If everything worked correctly, that should be it!

from pyb import Pin, UART
from time import sleep_ms

# User Editable Parameters
baudrate = 115200
stopbit  = 1
parity   = 0
pswd     = "mecha23"
name     = "mecha23"

# Allowable ranges
al_baudrate = [9600, 19200, 38400, 57600,
               115200, 230400, 460800]
al_stopbit  = [1, 2]
al_parity   = [0, 1, 2]

# Check the selected settings for errors
if baudrate not in al_baudrate:
    raise ValueError(f"Invalid Baudrate Selected; choose from {al_baudrate}")

if stopbit not in al_stopbit:
    raise ValueError(f"Invalid Stopbit Selected; choose from {al_stopbit}")

if parity not in al_parity:
    raise ValueError(f"Invalid Baudrate Selected; choose from {al_parity}")

# UART 1 Uses B6 and B7 by default
ser = UART(1, 38400, timeout=1000)

input("Press enter to send configuration to Bluetooth Module\n")

# # Reset Device
# s = "AT+ORGL\r\n"
# print("Device Factory Reset")
# print(f"Sending command: {repr(s)}\n")
# ser.write(s)
# s = ser.readline()
# print(f"Device Response: {repr(s)}\n")
# if s != b"OK\r\n":
#     raise Exception("Reset command not accepted")
# sleep_ms(500)

# Rename device
s = f"AT+NAME={name}\r\n"
print("Renaming Device")
print(f"Sending command: {repr(s)}")
ser.write(s)
s = ser.readline()
print(f"Device Response: {repr(s)}\n")
if s != b"OK\r\n":
    raise Exception("Rename command not accepted")
sleep_ms(500)

# Reset password
s = f"AT+PSWD=\"{pswd}\"\r\n"
print("Resetting Password")
print(f"Sending command: {repr(s)}\n")
ser.write(s)
s = ser.readline()
print(f"Device Response: {repr(s)}\n")
if s != b"OK\r\n":
    raise Exception("Password reset command not accepted")
sleep_ms(500)

# Configure UART
s = f"AT+UART={baudrate},{stopbit},{parity}\r\n"
print("Configuring UART")
print(f"Sending command: {repr(s)}\n")
ser.write(s)
s = ser.readline()
print(f"Device Response: {repr(s)}\n")
if s != b"OK\r\n":
    raise Exception("UART config command not accepted")
sleep_ms(500)

# Reset
s = f"AT+RESET\r\n"
print("Resetting Module")
print(f"Sending command: {repr(s)}\n")
ser.write(s)
s = ser.readline()
print(f"Device Response: {repr(s)}\n")
if s != b"OK\r\n":
    raise Exception("Reset failed")