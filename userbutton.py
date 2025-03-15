import pyb
import HAL
import task_share
from pyb import Pin

# Shared variable to store button state (1 = enabled, 0 = disabled)

def get_control_flag_share():
    # Returns the control flag shared variable
    control_flag = task_share.Share('h', thread_protect=True, name="ControlFlag")
    control_flag.put(0)  # Initial state: Disabled (0)

    def button_callback(pin):
        # Callback function for button press
        pyb.delay(50)  # Debounce delay to prevent multiple triggers
        if HAL.__USER_BUTTON__.PIN.value() == 0:  # Check if button is still pressed
            current_state = control_flag.get()
            control_flag.put(1 if current_state == 0 else 0)  # Toggle control state
            print("Control State Changed:", control_flag.get())

    # Configure interrupt on PC13 (B1 button) for falling edge detection (button press)
    HAL.__USER_BUTTON__.PIN.irq(trigger=Pin.IRQ_FALLING, handler=button_callback)
    return control_flag
