from pyb import Pin, ADC, Timer, UART, I2C

MAX_FREQ = 0xFFFF


# Verified \/

# #----------Motor Setup-----------
# Left Motor PWM
_PB3 = Pin(Pin.cpu.B3)  # TIM1_CH2
# Right Motor PWM
_PA15 = Pin(Pin.cpu.A15)  # TIM1_CH1

_TIM2 = Timer(2, freq=20000)
_TIM2_CH1 = _TIM2.channel(1, Timer.PWM, pin=_PA15, pulse_width_percent=10)  # type: ignore
_TIM2_CH2 = _TIM2.channel(2, Timer.PWM, pin=_PB3, pulse_width_percent=10)  # type: ignore


# #+++++++++Enable Pins+++++++++++++
# Right
_PC10 = Pin(Pin.cpu.C10, mode=Pin.OUT_PP, value=0)  # EVENTOUT
_PC11 = Pin(Pin.cpu.C11, Pin.OUT_PP, value=0)  # EVENTOUT
# Left
_PC12 = Pin(Pin.cpu.C12, mode=Pin.OUT_PP, value=0)  # EVENTOUT
_PD2 = Pin(Pin.cpu.D2, Pin.OUT_PP, value=0)  # EVENTOUT

# #+++++Voltage Measurement#+++++
_PA5 = Pin(Pin.cpu.A5)
_ADC_A5 = ADC(_PA5)


class __MOTOR_LEFT__:
    PWM = _TIM2_CH2
    ENABLE = _PC12
    DIRECTION = _PD2


class __MOTOR_RIGHT__:
    PWM = _TIM2_CH1
    ENABLE = _PC10
    DIRECTION = _PC11


class __MOTOR__:
    LEFT = __MOTOR_LEFT__
    RIGHT = __MOTOR_RIGHT__
    VOLTAGE_MESUREMENT = _ADC_A5


# ---------------------------------------------------------------------

# #------ Encoder Setup ---------
# #Left
_PC6 = Pin(Pin.cpu.C6)  # TIM3_CH1 (Encoder Channel A)
_PC7 = Pin(Pin.cpu.C7)  # TIM3_CH2 (Encoder Channel B)
_TIM3 = Timer(3, period=MAX_FREQ, prescaler=0)
_TIM3_CH1 = _TIM3.channel(1, pin=_PC6, mode=Timer.ENC_AB)
_TIM3_CH2 = _TIM3.channel(2, pin=_PC7, mode=Timer.ENC_AB)
# #Right
_PA8 = Pin(Pin.cpu.A8)  # TIM1_CH1 (Encoder Channel B)
_PA9 = Pin(Pin.cpu.A9)  # TIM1_CH2 (Encoder Channel A)
_TIM1 = Timer(1, period=MAX_FREQ, prescaler=0)
_TIM1_CH1 = _TIM1.channel(1, pin=_PA8, mode=Timer.ENC_AB)
_TIM1_CH2 = _TIM1.channel(2, pin=_PA9, mode=Timer.ENC_AB)


class __ENCODER_LEFT__:
    CHA = _TIM3_CH1
    CHB = _TIM3_CH2
    TIM = _TIM3


class __ENCODER_RIGHT__:
    CHA = _TIM1_CH1
    CHB = _TIM1_CH2
    TIM = _TIM1


class __ENCODER__:
    LEFT = __ENCODER_LEFT__
    RIGHT = __ENCODER_RIGHT__


# #------------------------------


# #---------Line Sensor----------
_PA0 = Pin(Pin.cpu.A0)  # ADC_IN
_ADC_A0 = ADC(_PA0)

_PA1 = Pin(Pin.cpu.A1)  # ADC_IN
_ADC_A1 = ADC(_PA1)

_PA4 = Pin(Pin.cpu.A4)  # ADC_IN
_ADC_A4 = ADC(_PA4)

_PA6 = Pin(Pin.cpu.A6)  # ADC_IN
_ADC_A6 = ADC(_PA6)

_PA7 = Pin(Pin.cpu.A7)  # ADC_IN
_ADC_A7 = ADC(_PA7)

_PB0 = Pin(Pin.cpu.B0)  # ADC_IN
_ADC_B0 = ADC(_PB0)

_PB1 = Pin(Pin.cpu.B1)  # ADC_IN
_ADC_B1 = ADC(_PB1)

_PC0 = Pin(Pin.cpu.C0)  # ADC_IN
_ADC_C0 = ADC(_PC0)

_PC1 = Pin(Pin.cpu.C1)  # ADC_IN
_ADC_C1 = ADC(_PC1)

_PC2 = Pin(Pin.cpu.C2)  # ADC_IN
_ADC_C2 = ADC(_PC2)

_PC3 = Pin(Pin.cpu.C3)  # ADC_IN
_ADC_C3 = ADC(_PC3)

_PC4 = Pin(Pin.cpu.C4)  # ADC_IN
_ADC_C4 = ADC(_PC4)

_PC5 = Pin(Pin.cpu.C5)  # ADC_IN
_ADC_C5 = ADC(_PC5)

# #-------Enable Pins---------
_PA10 = Pin(Pin.cpu.A10, mode=Pin.OUT_PP, pull=Pin.PULL_DOWN, value=0)  # EVENTOUT
_PC9 = Pin(Pin.cpu.C9, mode=Pin.OUT_PP, pull=Pin.PULL_DOWN, value=0)  # EVENTOUT
_PA10.high()
_PC9.high()


class __LINE_SENSOR__:
    ENABLE_EVEN = _PA10
    ENABLE_ODD = _PC9
    CHANNELS = [
        _ADC_B1,
        _ADC_C5,
        _ADC_A7,
        _ADC_C4,
        _ADC_C2,
        _ADC_A6,
        _ADC_C3,
        _ADC_B0,
        _ADC_C0,
        _ADC_A4,
        _ADC_C1,
        _ADC_A1,
        _ADC_A0,
    ]


# #--------------------------------


# #----------------------------------

# #-------------Bump Sensor----------

# _PC8 = Pin(Pin.cpu.C8, mode = Pin.IN) #DIGITAL_IN
# _PB4 = Pin(Pin.cpu.B4, mode = Pin.IN) #DIGITAL_IN
# _PB5 = Pin(Pin.cpu.B5, mode = Pin.IN) #DIGITAL_IN
# _PB13 = Pin(Pin.cpu.B13, mode = Pin.IN) #DIGITAL_IN
# _PB14 = Pin(Pin.cpu.B14, mode = Pin.IN) #DIGITAL_IN
# _PB15 = Pin(Pin.cpu.B15, mode = Pin.IN) #DIGITAL_IN

# class __BUMP_SENSOR_LEFT__:
#   INSIDE = _PC8
#   MIDDLE = _PB4
#   OUTSIDE = _PB5

# class __BUMP_SENSOR_RIGHT__:
#   INSIDE = _PB15
#   MIDDLE = _PB14
#   OUTSIDE = _PB13

# class __BUMP_SENSOR__:
#   LEFT = __BUMP_SENSOR_LEFT__
#   RIGHT = __BUMP_SENSOR_RIGHT__

# #-----------------------------------

# #-------------Bump Sensor---------- (Joseph's Version)

_PC8 = Pin(Pin.cpu.C8, mode=Pin.IN, pull=Pin.PULL_UP)  # Left Inside
_PB4 = Pin(Pin.cpu.B4, mode=Pin.IN, pull=Pin.PULL_UP)  # Left Middle
_PB5 = Pin(Pin.cpu.B5, mode=Pin.IN, pull=Pin.PULL_UP)  # Left Outside
_PB12 = Pin(Pin.cpu.B12, mode=Pin.IN, pull=Pin.PULL_UP)  # Right Outside
_PB14 = Pin(Pin.cpu.B14, mode=Pin.IN, pull=Pin.PULL_UP)  # Right Middle
_PB15 = Pin(Pin.cpu.B15, mode=Pin.IN, pull=Pin.PULL_UP)  # Right Inside


class __BUMP_SENSOR_LEFT__:
    INSIDE = _PC8
    MIDDLE = _PB4
    OUTSIDE = _PB5


class __BUMP_SENSOR_RIGHT__:
    INSIDE = _PB15
    MIDDLE = _PB14
    OUTSIDE = _PB12


class __BUMP_SENSOR__:
    LEFT = __BUMP_SENSOR_LEFT__
    RIGHT = __BUMP_SENSOR_RIGHT__


# #-----------------------------------


# #----------------IMU----------------

# _PB2 = Pin(Pin.cpu.B2) #EVENTOUT
# _PB2.init(Pin.OUT_PP, value=0)
# _PB8 = Pin(Pin.cpu.B8) #I2C1_SCL
# _PB9 = Pin(Pin.cpu.B9) #I2C1_SDA

# class __IMU__:
#   RESET = _PB2
#   SCL = _PB8
#   SDA = _PB9
#   I2C_CHANNEL = 1

# # ----------------IMU (BNO055)---------------- (Joseph's Version)

_PB2 = Pin(Pin.cpu.B2, mode=Pin.OUT_PP, value=1)  # RESET pin (EVENTOUT)
_PB8 = Pin(Pin.cpu.B8)  # I2C1_SCL (ALT function 4)
_PB9 = Pin(Pin.cpu.B9)  # I2C1_SDA (ALT function 4)


class __IMU__:
    RESET = _PB2
    SCL = _PB8
    SDA = _PB9
    I2C_CHANNEL = 1  # Define the I2C channel number

    # Initialize I2C for IMU
    I2C = I2C(
        I2C_CHANNEL, I2C.CONTROLLER
    )  # This can change, I put an arbitrary Fast-mode 400kHz


# #-----------------------------------

# -------------Bluetooth-------------

# # _PB6 = Pin(Pin.cpu.B6, mode=Pin.ALT, alt=7) # USART1_TX
# # _PB7 = Pin(Pin.cpu.B7, mode=Pin.ALT, alt=7) # USART1_RX
# _PB10 = Pin(Pin.cpu.B10, mode=Pin.OUT_PP, value=0) # EVENOUT, ENABLE pin (set low initially)
_PB11 = Pin(Pin.cpu.B11, mode=Pin.IN)  # DIGITAL_IN, STATE pin


class __BLUE_TOOTH__:
    #   TX = _PB6
    #   RX = _PB7
    #   UART_CHANNEL = 1
    UART = UART(1, 115200, timeout=100)
    #   ENABLE = _PB10
    STATE = _PB11


# -----------------------------------

# -------------USER Button (B1)-------------

_PC13 = Pin(
    Pin.cpu.C13, mode=Pin.IN, pull=Pin.PULL_UP
)  # Configure PC13 as an input with a pull-up resistor


class __USER_BUTTON__:
    PIN = _PC13  # Assign the pin to the class

    def is_pressed(self):
        return (
            not _PC13.value()
        )  # Active low: returns True when pressed, False otherwise


# ------------------------------------------


class HAL:
    ENCODER = __ENCODER__
    LINE_SENSOR = __LINE_SENSOR__
    MOTOR = __MOTOR__
    #   BUMP_SENSOR = __BUMP_SENSOR__
    #   IMU = __IMU__
    BLUE_TOOTH = __BLUE_TOOTH__
