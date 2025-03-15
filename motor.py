from prelude import *
import HAL
from closed_loop import ClosedLoop
from task_share import Share, Queue
from encoder import Encoder
import gc


class Motor:
    def __init__(self, side: int, debug=False) -> None:
        print(f"Initilizing Motor {"Left" if side == Vehicle_Side.LEFT else "Right"}")
        self.debug = debug
        self._side: int = side
        self.GAIN_INV = 7.2 / 3.11
        self.__hal__ = (
            HAL.__MOTOR_LEFT__ if side == Vehicle_Side.LEFT else HAL.__MOTOR_RIGHT__
        )
        self.voltage_measurement = HAL.__MOTOR__.VOLTAGE_MESUREMENT
        self.direction = (
            MotorDirection.FWD
            if self.__hal__.DIRECTION.value() == MotorDirection.FWD
            else MotorDirection.REV
        )
        self.is_on = bool(self.__hal__.ENABLE.value())
        self.controller: ClosedLoop = ClosedLoop(
            kp=0.8,
            ki=-0.1,
            kd=0.005,
        )
        self.set_point = SPEED_SET_POINT
        self.encoder = Encoder(side)
        gc.collect()
        print(f"\\Initilizing Motor {"Left" if side == Vehicle_Side.LEFT else "Right"}")

    def set_dir(self, dir: int):
        self.direction = dir
        self.__hal__.DIRECTION.value(dir)

    def effort(self, value: int | float | None = None) -> int | float:
        if value == None:
            self.__hal__.PWM.pulse_width_percent()
            return self.__hal__.PWM.pulse_width_percent()
        self.set_dir(MotorDirection.FWD if value > 0 else MotorDirection.REV)
        self.__hal__.PWM.pulse_width_percent(
            abs(value)
            # if value > 10
            # else abs(value) + 5
        )

        return value

    def enable(self):
        if self.is_on:
            return
        self.is_on = True
        self.__hal__.ENABLE.high()
        return

    def disable(self):
        if not self.is_on:
            return
        self.is_on = False
        self.__hal__.ENABLE.low()

    def task(self, shares):
        control_flag: Share
        yaw_effort_percent_share: Share
        position_reset_flag: Share
        position_share: Queue
        (
            control_flag,
            yaw_effort_percent_share,
            position_reset_flag,
            position_share,
        ) = shares
        while True:
            # if self.debug:
            #     print(
            #         f"{"Left" if self._side == Vehicle_Side.LEFT else "Right"} Motor Task"
            #     )
            self.encoder.update()
            if bool(position_reset_flag.get()):
                self.encoder.zero()
                position_reset_flag.put(0)
            position_share.put(self.encoder.position())
            # -------------- <On-Off Button> -------------- #
            if control_flag.get() == 0:
                if self.is_on:
                    # print(
                    #     f'Motor {"Left" if self._side == Vehicle_Side.LEFT else "Right"} Off'
                    # )
                    self.disable()
            else:
                if not self.is_on:
                    self.enable()
                # -------------- </On-Off Button> -------------- #

                # -------------- <Velocity Calcs> -------------- #

                velocity_set_point = (
                    yaw_effort_percent_share.get() * get_voltage() / self.GAIN_INV
                    if self._side == Vehicle_Side.LEFT
                    else -yaw_effort_percent_share.get() * get_voltage() / self.GAIN_INV
                ) + SPEED_SET_POINT  # Speed Set Point

                # -------------- <Motor Control> --------------- #

                # error = (velocity_set_point) - self.encoder.velocity()
                # adjustment = (
                #     self.controller.update(
                #         (velocity_set_point) - self.encoder.velocity()
                #     )
                #     # if self._side == Vehicle_Side.RIGHT
                #     # else self.controller.update(error)
                # )
                self.effort(
                    ((self.GAIN_INV / get_voltage()) * velocity_set_point)
                    + self.controller.update(
                        (velocity_set_point) - self.encoder.velocity()
                    )
                )
                if self.controller.debug or self.debug:
                    print(
                        f"{"Left" if self._side == Vehicle_Side.LEFT else "Right"} Motor=> "
                        + " | ".join(
                            [
                                f"Gain Value: {((self.GAIN_INV / get_voltage()) * velocity_set_point)}",
                                f"Velocity: {self.encoder.velocity() * (-1 if HAL.__MOTOR_LEFT__.DIRECTION.value() != MotorDirection.FWD else 1)}",
                                f"Error: {(velocity_set_point) - self.encoder.velocity()}",
                                f"PID Adjustment: {self.controller.update((velocity_set_point) - self.encoder.velocity())}",
                                f" PWM Percent: {self.effort()}",
                            ]
                        )
                    )
            yield
            # -------------- </Motor Control> --------------- #
