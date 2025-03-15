from prelude import *
import HAL, motor_control_task
from task_share import Share
import gc


class CourseCompletion:
    S5_DISTANCE_SET_POINT = 150
    S10_HEADING_SET_POINT = 45 * 16  # Turn to Checkpoint 1
    S10_DISTANCE_SET_POINT = 160  # Move ToCheckpoint 1
    S20_HEADING_SET_POINT = int(-29 * 16)  # Turn to Checkpoint 2
    S20_DISTANCE_SET_POINT = 235  # Move ToCheckpoint 2
    S30_HEADING_SET_POINT = 90 * 16  # Turn to Checkpoint 3
    S30_DISTANCE_SET_POINT = 225  # Move ToCheckpoint 3
    S40_HEADING_SET_POINT = 180 * 16  # Turn to Checkpoint 4
    S40_DISTANCE_SET_POINT = 100  # Deadhead toward Cage
    S45_DISTANCE_SET_POINT = 160  # Turn off Line Sensor Fail over distance
    # S50_HEADING_SET_POINT = None
    S50_DISTANCE_SET_POINT = 235  # Move in Cage
    S60_HEADING_SET_POINT = -90 * 16  # Turn to Wall
    S60_DISTANCE_SET_POINT = 1000  # Arbitariliy large move into wall
    # S55_DISTANCE_SET_POINT = None

    ## After Wall
    S100_HEADING_SET_POINT = 0
    S100_DISTANCE_SET_POINT = 150
    S110_HEADING_SET_POINT = -90 * 16
    S110_DISTANCE_SET_POINT = 150
    S120_HEADING_SET_POINT = 180 * 16
    S120_DISTANCE_SET_POINT = 150

    def __init__(self, debug=False) -> None:
        print("Init course.py")
        self.debug = debug
        self.button_function = self.default_button
        self.distance_set_point: None | int = None
        self.control_flag_share: None | Share = None
        self.motor_control_state_share: None | Share = None
        self.target_heading_share: None | Share = None
        self.left_motor_position_share: None | Share = None
        self.right_motor_position_share: None | Share = None
        self.heading_share: None | Share = None
        self.centroid_share: None | Share = None
        self.left_motor_position_reset_flag: None | Share = None
        self.right_motor_position_reset_flag: None | Share = None
        self.startng_heading_share: None | Share = None
        self.bump_sensor: None | Share = None
        print("\\Init course.py")
        gc.collect()

    def default_button(self):
        raise BaseException("Button Hit")

    def get_around_wall(self):
        import HAL, utime

        HAL.__MOTOR_LEFT__.ENABLE.low()
        HAL.__MOTOR_RIGHT__.ENABLE.low()
        HAL.__MOTOR_LEFT__.DIRECTION.value(MotorDirection.REV)
        HAL.__MOTOR_RIGHT__.DIRECTION.value(MotorDirection.REV)
        HAL.__MOTOR_LEFT__.PWM.pulse_width_percent(50)
        HAL.__MOTOR_RIGHT__.PWM.pulse_width_percent(50)
        HAL.__MOTOR_LEFT__.ENABLE.high()
        HAL.__MOTOR_RIGHT__.ENABLE.high()
        utime.sleep_ms(40)
        HAL.__MOTOR_LEFT__.ENABLE.low()
        HAL.__MOTOR_RIGHT__.ENABLE.low()
        HAL.__MOTOR_LEFT__.DIRECTION.value(MotorDirection.FWD)
        HAL.__MOTOR_RIGHT__.DIRECTION.value(MotorDirection.FWD)
        self.state = 100

    def debug_print(self):
        if (
            self.left_motor_position_share != None
            and self.control_flag_share != None
            and self.motor_control_state_share != None
            and self.target_heading_share != None
            and self.left_motor_position_share != None
            and self.right_motor_position_share != None
            and self.heading_share != None
            and self.centroid_share != None
            and self.left_motor_position_reset_flag != None
            and self.right_motor_position_reset_flag != None
            and self.startng_heading_share != None
            and self.bump_sensor != None
        ):
            print(
                " | ".join(
                    [
                        f"State: {self.state}",
                        f"Target Heading: ({get_relative_angle(self.target_heading_share.get(), self.startng_heading_share.get()) / 16}, {self.target_heading_share.get()})",
                        f"Heading: ({get_relative_angle(self.heading_share.get(), self.startng_heading_share.get()) / 16}, {self.heading_share.get()})",
                        f"Distance: {(self.left_motor_position_share.get() + self.right_motor_position_share.get()) / 2}",
                        f"Target Distance: {self.distance_set_point}",
                    ]
                )
            )
        return

    def task(self, shares):

        (
            self.control_flag_share,
            self.motor_control_state_share,
            self.target_heading_share,
            self.left_motor_position_share,
            self.right_motor_position_share,
            self.heading_share,
            self.centroid_share,
            self.left_motor_position_reset_flag,
            self.right_motor_position_reset_flag,
            self.startng_heading_share,
            self.bump_sensor,
        ) = shares
        self.state = 0

        if (
            self.control_flag_share != None
            and self.motor_control_state_share != None
            and self.target_heading_share != None
            and self.left_motor_position_share != None
            and self.right_motor_position_share != None
            and self.heading_share != None
            and self.centroid_share != None
            and self.left_motor_position_reset_flag != None
            and self.right_motor_position_reset_flag != None
            and self.startng_heading_share != None
            and self.bump_sensor != None
        ):
            self.motor_control_state_share.put(
                motor_control_task.MotorControl.S1_LINE_PID_CALC
            )
            while True:
                if self.bump_sensor.get() == 1 and self.state != 60:
                    self.button_function()
                # gc.collect()
                if self.control_flag_share.get() == 0:
                    if self.state != 0:
                        self.state = 0
                else:
                    ## self.state Map:
                    # S0: Starting ==>
                    # S5: Checkpoint 0 ==> Checkpoint 1
                    # S10: Checkpoint 1 ==> Checkpoint 2
                    # S20: Checkpoint 2 ==> Target 2
                    # S30: Target 2 ==> Checkpoint 3
                    # S40: Checkpoint 3 ==>
                    # S50: Grid ==>
                    # S55: Grid Middle Point ==>
                    # S57: To Wall ==>
                    # S60: Target 1 ==>
                    # S70: End ==>
                    # S80: Restart ↩

                    # """
                    # S0: Starting:
                    # while <all ir sensors are reading a value>:
                    #     <drive straight following starting heading>
                    # encoder_left.zero()
                    # encoder_right.zero()
                    # self.state = S5
                    # """
                    if self.state == 0:
                        print(f"Course State: {self.state }")
                        while (
                            self.centroid_share.get() == 0.0
                            and self.bump_sensor.get() == 0
                        ):
                            if self.debug:
                                " | ".join(
                                    [f"Centroid Error: {self.centroid_share.get()}"]
                                )
                            print(f"Course State: {self.state }")
                            yield self.state
                        self.motor_control_state_share.put(
                            motor_control_task.MotorControl.S0_STOP
                        )
                        print(f"Course State: {self.state }")
                        yield self.state
                        self.startng_heading_share.put(self.heading_share.get())
                        self.target_heading_share.put(self.heading_share.get())
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)
                        self.startng_heading_share.put(self.startng_heading_share.get())
                        print(f"Starting Heading: {self.startng_heading_share.get()}")
                        self.state = 5
                    # '''
                    # S5: Checkpoint One:
                    #     while heading < starting_heading - 90°:
                    #         motor_control_state ==> Line Following
                    #     target_heading.put(starting_heading - 90°)
                    #     motor_control_state ==> Heading Following
                    #     while (<Left Motor Position> + <Right Motor Position>) / 2 < CHECKPOINT_ONE_DISTANCE_SET_POINT:
                    #         yeild
                    #     self.state = S10
                    # '''
                    elif self.state == 5:
                        print(f"Course State: {self.state}")
                        self.distance_set_point = CourseCompletion.S5_DISTANCE_SET_POINT
                        self.target_heading_share.put(self.startng_heading_share.get())
                        self.motor_control_state_share.put(
                            motor_control_task.MotorControl.S2_HEADING_PID_CALC
                        )
                        while (
                            self.left_motor_position_share.get()
                            + self.right_motor_position_share.get()
                        ) / 2 < self.distance_set_point and self.bump_sensor.get() == 0:
                            if self.debug:
                                self.debug_print()
                            print(f"Course State: {self.state }")
                            yield self.state
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)
                        self.state = 10
                    elif self.state == 10:
                        print(f"Course State: {self.state }")
                        self.target_heading_share.put(
                            get_relative_angle(
                                self.S10_HEADING_SET_POINT,
                                self.startng_heading_share.get(),
                            )
                        )
                        self.distance_set_point = (
                            CourseCompletion.S10_DISTANCE_SET_POINT
                        )
                        while (
                            self.left_motor_position_share.get()
                            + self.right_motor_position_share.get()
                        ) / 2 < self.distance_set_point and self.bump_sensor.get() == 0:
                            if self.debug:
                                self.debug_print()
                            yield self.state
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)
                        self.state = 20
                    elif self.state == 20:
                        print(f"Course State: {self.state}")
                        self.target_heading_share.put(
                            get_relative_angle(
                                self.S20_HEADING_SET_POINT,
                                self.startng_heading_share.get(),
                            )
                        )
                        self.distance_set_point = (
                            CourseCompletion.S20_DISTANCE_SET_POINT
                        )
                        while (
                            self.left_motor_position_share.get()
                            + self.right_motor_position_share.get()
                        ) / 2 < self.distance_set_point and self.bump_sensor.get() == 0:
                            if self.debug:
                                self.debug_print()
                            yield self.state
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)
                        self.state = 30
                    elif self.state == 30:
                        print(f"Course State: {self.state}")
                        self.target_heading_share.put(
                            get_relative_angle(
                                self.S30_HEADING_SET_POINT,
                                self.startng_heading_share.get(),
                            )
                        )
                        self.distance_set_point = (
                            CourseCompletion.S30_DISTANCE_SET_POINT
                        )
                        while (
                            self.left_motor_position_share.get()
                            + self.right_motor_position_share.get()
                        ) / 2 < self.distance_set_point and self.bump_sensor.get() == 0:
                            if self.debug:
                                self.debug_print()
                            yield self.state
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)
                        self.state = 40
                    elif self.state == 40:
                        print(f"Course State: {self.state}")
                        self.target_heading_share.put(
                            get_relative_angle(
                                self.S40_HEADING_SET_POINT,
                                self.startng_heading_share.get(),
                            )
                        )
                        self.distance_set_point = (
                            CourseCompletion.S40_DISTANCE_SET_POINT
                        )
                        while (
                            self.left_motor_position_share.get()
                            + self.right_motor_position_share.get()
                        ) / 2 < self.distance_set_point and self.bump_sensor.get() == 0:
                            if self.debug:
                                self.debug_print()
                            yield self.state
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)
                        self.state = 45
                        self.motor_control_state_share.put(
                            motor_control_task.MotorControl.S1_LINE_PID_CALC
                        )
                    elif self.state == 45:
                        print(f"Course State: {self.state}")
                        # self.target_heading_share.put(
                        #     get_relative_angle(
                        #         self.S40_HEADING_SET_POINT,
                        #         self.startng_heading_share.get(),
                        #     )
                        # )
                        self.distance_set_point = (
                            CourseCompletion.S45_DISTANCE_SET_POINT
                        )
                        while (
                            self.centroid_share.get() != 0.0
                            and self.bump_sensor.get() == 0
                            # and (
                            #     (
                            #         self.left_motor_position_share.get()
                            #         + self.right_motor_position_share.get()
                            #     )
                            #     / 2
                            # )
                            # > self.distance_set_point
                        ):
                            if self.debug:
                                print(
                                    " | ".join(
                                        [
                                            f"Centroid Error: {self.centroid_share.get()}",
                                            f"Distance: {(self.left_motor_position_share.get() + self.right_motor_position_share.get()) / 2}",
                                        ]
                                    )
                                )
                                # self.debug_print()
                                if (
                                    (
                                        self.left_motor_position_share.get()
                                        + self.right_motor_position_share.get()
                                    )
                                    / 2
                                ) > self.distance_set_point:
                                    break
                            yield self.state
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)
                        self.state = 50
                        self.motor_control_state_share.put(
                            motor_control_task.MotorControl.S2_HEADING_PID_CALC
                        )
                    elif self.state == 50:
                        print(f"Course State: {self.state}")
                        self.distance_set_point = (
                            CourseCompletion.S50_DISTANCE_SET_POINT
                        )

                        while (
                            self.left_motor_position_share.get()
                            + self.right_motor_position_share.get()
                        ) / 2 < self.distance_set_point and self.bump_sensor.get() == 0:
                            if self.debug:
                                self.debug_print()
                            yield self.state
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)
                        self.state = 60
                    elif self.state == 60:
                        print(f"Course State: {self.state}")
                        # Charge the button function
                        self.button_function = self.get_around_wall
                        self.target_heading_share.put(
                            get_relative_angle(
                                self.S60_HEADING_SET_POINT,
                                self.startng_heading_share.get(),
                            )
                        )
                        self.distance_set_point = (
                            CourseCompletion.S60_DISTANCE_SET_POINT
                        )
                        while self.bump_sensor.get() == 0:
                            if self.debug:
                                self.debug_print()
                            yield self.state
                        self.get_around_wall()
                        self.bump_sensor.put(0)
                        self.button_function = self.default_button
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)

                        # After Button
                    elif self.state == 100:
                        print(f"Course State: {self.state}")
                        self.target_heading_share.put(
                            get_relative_angle(
                                self.S100_HEADING_SET_POINT,
                                self.startng_heading_share.get(),
                            )
                        )
                        self.distance_set_point = (
                            CourseCompletion.S100_DISTANCE_SET_POINT
                        )
                        while (
                            self.left_motor_position_share.get()
                            + self.right_motor_position_share.get()
                        ) / 2 < self.distance_set_point and self.bump_sensor.get() == 0:
                            if self.debug:
                                self.debug_print()
                            yield self.state
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)
                        self.state = 110
                    elif self.state == 110:
                        print(f"Course State: {self.state}")
                        self.target_heading_share.put(
                            get_relative_angle(
                                self.S110_HEADING_SET_POINT,
                                self.startng_heading_share.get(),
                            )
                        )
                        self.distance_set_point = (
                            CourseCompletion.S110_DISTANCE_SET_POINT
                        )
                        while (
                            self.left_motor_position_share.get()
                            + self.right_motor_position_share.get()
                        ) / 2 < self.distance_set_point and self.bump_sensor.get() == 0:
                            if self.debug:
                                self.debug_print()
                            yield self.state
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)
                        self.state = 120
                    elif self.state == 120:
                        print(f"Course State: {self.state}")
                        self.target_heading_share.put(
                            get_relative_angle(
                                self.S120_HEADING_SET_POINT,
                                self.startng_heading_share.get(),
                            )
                        )
                        self.distance_set_point = (
                            CourseCompletion.S120_DISTANCE_SET_POINT
                        )
                        while (
                            self.left_motor_position_share.get()
                            + self.right_motor_position_share.get()
                        ) / 2 < self.distance_set_point and self.bump_sensor.get() == 0:
                            if self.debug:
                                self.debug_print()
                            yield self.state
                        self.left_motor_position_reset_flag.put(1)
                        self.right_motor_position_reset_flag.put(1)
                        self.state = 130
                    else:
                        return
                gc.collect()
                yield self.state
