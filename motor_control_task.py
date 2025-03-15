from prelude import *
from task_share import Share
from closed_loop import ClosedLoop
import HAL
from line_sensor import LineSensor
from bno055 import BNO055
import gc


class MotorControl:
    S1_LINE_PID_CALC = 1
    S2_HEADING_PID_CALC = 2
    S0_STOP = -1

    # FSM states
    def __init__(self, debug=False) -> None:
        print("Init Vehicle Control")
        self.yaw_effort_percent_share: Share | None = None
        self.controler: ClosedLoop | None = None
        self.state = MotorControl.S0_STOP  # Initial FSM state
        self.debug = debug
        self.line_sensor = LineSensor()
        self.imu = BNO055()
        # gc.collect()
        print("\\Init Vehicle Control")

    def pid(
        self,
        error: float,
    ) -> None:
        if self.controler != None and self.yaw_effort_percent_share != None:
            self.new_set_point = self.controler.update(error)
            self.yaw_effort_percent_share.put(self.new_set_point)

    def task(self, shares: tuple):

        line_pid_controler = ClosedLoop(
            # Almost Working, (20, .2, .02)
            kp=2,
            ki=0.02,
            kd=0.0,
        )
        heading_pid_controler = ClosedLoop(
            # Old Values before Cascade Control: (1, 0.0001, 0.001)
            # Values were the old values, but halved, in accordance to the change to the self.pid() function
            kp=1,
            ki=0.1,
            kd=0.001,
        )

        # Get shared variables
        centroid_share: Share
        heading_share: Share
        target_heading_share: Share
        motor_control_state_share: Share
        control_flag: Share
        yaw_effort_percent_share: Share
        (
            centroid_share,
            heading_share,
            target_heading_share,
            motor_control_state_share,
            control_flag,
            yaw_effort_percent_share,
        ) = shares
        self.yaw_effort_percent_share = yaw_effort_percent_share
        motor_control = self
        while True:
            if control_flag.get() == 0:
                if motor_control.state != motor_control.S0_STOP:
                    motor_control.state = motor_control.S0_STOP
            else:
                if motor_control_state_share.get() != motor_control.state:
                    centroid_share.put(self.line_sensor.calculate_centroid())
                    heading_share.put(self.imu.get_euler_angles()[0])

                ## -------------------------------------- Main Course Completion Loop ----------------------------------------------- ##
                # each state should do the following steps:
                # 1. set the appropriate ClosedLoop Controler
                # 2. Defines a set point
                # 3. Defines an error function
                # 4. calculates the error
                # 5. passes the error to the motor_control.pid() function

                # -------------------------------------------Unpacking Share values-------------------------------------------------------- #
                target_heading: float = target_heading_share.get()
                motor_control.state = motor_control_state_share.get()
                # -------------------------------------------\Unpacking Share values-------------------------------------------------------- #

                # --------------- S1: Follow the Line Sensor (Default) ----------------- #
                if motor_control.state == MotorControl.S1_LINE_PID_CALC:
                    motor_control.controler = line_pid_controler
                    centroid_error = self.line_sensor.calculate_centroid()
                    centroid_share.put(centroid_error)
                    motor_control.pid(centroid_error)
                    if motor_control.controler.debug:
                        print(
                            " | ".join(
                                [
                                    f"Error: {centroid_error}",
                                    f"New Set Point: {self.new_set_point}",
                                    f"Left Motor: {HAL.__MOTOR_LEFT__.PWM.pulse_width_percent() * (-1 if HAL.__MOTOR_LEFT__.DIRECTION.value() != MotorDirection.FWD else 1)}",
                                    f"Right Motor: {HAL.__MOTOR_RIGHT__.PWM.pulse_width_percent() * (-1 if HAL.__MOTOR_RIGHT__.DIRECTION.value() != MotorDirection.FWD else 1)}",
                                ]
                            )
                        )
                # --------------- \S1: Follow the Line Sensor (Default) ----------------- #

                # ------------------------- S2: Follow A Heading ------------------------- #
                if motor_control.state == MotorControl.S2_HEADING_PID_CALC:
                    motor_control.controler = heading_pid_controler
                    heading = self.imu.get_euler_angles()[0]
                    error1: int = (int(target_heading) - heading) % 5760
                    error2: int = error1 - 5760 if error1 > 0 else error1 + 5760
                    error = (
                        error1 / 16
                        if min(abs(error1), abs(error2)) == abs(error1)
                        else error2 / 16
                    )
                    motor_control.pid(error)
                    heading_share.put(heading)
                    if motor_control.controler.debug or motor_control.debug:
                        print(
                            " | ".join(
                                [
                                    f"Error: ({error1/16}, {error2/16})",
                                    f"Target: {target_heading}",
                                    f"Heading: {heading}",
                                    f"New Set Point: {self.new_set_point}",
                                    f"Left Motor: {HAL.__MOTOR_LEFT__.PWM.pulse_width_percent() * (-1 if HAL.__MOTOR_LEFT__.DIRECTION.value() != MotorDirection.FWD else 1)}",
                                    f"Right Motor: {HAL.__MOTOR_RIGHT__.PWM.pulse_width_percent() * (-1 if HAL.__MOTOR_RIGHT__.DIRECTION.value() != MotorDirection.FWD else 1)}",
                                ]
                            )
                        )
                # ------------------------- \S2: Follow A Heading ------------------------- #

                # Default Action: Yeild unimplimented State
            yield motor_control.state
