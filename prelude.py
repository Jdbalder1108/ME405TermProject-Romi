class Vehicle_Side:
    LEFT = 0
    RIGHT = 1


class MotorDirection:
    FWD = 0
    REV = 1


def get_voltage(start_up=False) -> float:
    import HAL

    voltage = HAL._ADC_A5.read() * (3.3 / 4095) * (14.7 / 4.7)
    if voltage < 5.5 and start_up:
        raise BaseException(f"Voltage Too Low, Change Batteries. Voltage: {voltage}")
    return voltage


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


# Motor Set Points
SPEED_SET_POINT = 50
MOTOR_SET_POINT_PERCENT = clamp((SPEED_SET_POINT * (3.11 / 7.2)), 0, 100) / 100


# Course Set Points
def get_relative_angle(angle: float | None, starting_angle: float) -> float:
    # if angle == 0, relative angle = 0 - starting angle
    #   if 0 - starting angle > 0
    #   else 0 - starting angle + 5760
    if angle == None:
        angle = int(input("Enter a Heading (16th of a degree)"))
        print(angle)
    return (angle + starting_angle) % 5760
