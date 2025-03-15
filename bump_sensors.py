class BumpSensor:
    import pyb

    # Initialize bump sensors from HAL
    def __init__(self):
        import HAL
        import task_share
        import pyb

        # Shared variable for bump sensor state (1 = bump detected, 0 = no bump)
        self.bump_flag = task_share.Share("h", thread_protect=True, name="BumpFlag")
        self.bump_flag.put(0)  # Default: No bump detected
        # Initialize bump sensors from HAL
        self.left_sensors = [
            HAL.__BUMP_SENSOR__.LEFT.INSIDE,
            HAL.__BUMP_SENSOR__.LEFT.MIDDLE,
            HAL.__BUMP_SENSOR__.LEFT.OUTSIDE,
        ]
        self.right_sensors = [
            HAL.__BUMP_SENSOR__.RIGHT.INSIDE,
            HAL.__BUMP_SENSOR__.RIGHT.MIDDLE,
            HAL.__BUMP_SENSOR__.RIGHT.OUTSIDE,
        ]

        # Attaching interrupt handlers to each sensor
        for sensor in self.left_sensors + self.right_sensors:
            sensor.irq(trigger=pyb.Pin.IRQ_FALLING, handler=self.bump_callback)

    def bump_callback(self, pin: pyb.Pin):

        # Callback function for bump sensor interrupts
        self.bump_flag.put(1)

    def any_pressed(self):
        # Checking if any bump sensor is pressed
        return any(
            not sensor.value() for sensor in self.left_sensors + self.right_sensors
        )

    def reset_flag(self):
        # Reset the bump flag
        self.bump_flag.put(0)

    def get_collision_side(self):
        # Determine which side the collision occurred on
        left_hit = any(not sensor.value() for sensor in self.left_sensors)
        right_hit = any(not sensor.value() for sensor in self.right_sensors)

        if left_hit and right_hit:
            return "BOTH"
        elif left_hit:
            return "LEFT"
        elif right_hit:
            return "RIGHT"
        return "NONE"

    def get_bump_flag_share(self):
        # Return the bump flag share
        return self.bump_flag
