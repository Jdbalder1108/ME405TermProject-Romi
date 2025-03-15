from prelude import *
from array import array
import time
from motor import Motor
from encoder import Encoder
import os
import HAL


class Collector:
    def __init__(self) -> None:

        # Initalize Motors and Encoders
        self.motor_left = Motor(Vehicle_Side.LEFT)
        self.motor_right = Motor(Vehicle_Side.RIGHT)
        self.encoder_left = Encoder(Vehicle_Side.LEFT)
        self.encoder_right = Encoder(Vehicle_Side.RIGHT)
        self.encoder_left.zero()
        self.encoder_right.zero()
        self.left_postion: array = array("f")
        self.right_postion: array = array("f")
        self.left_velocity: array = array("f")
        self.right_velocity: array = array("f")
        self.time: array = array("i")
        self.speed: int = 0

    def set_speed(self, speed: int):
        self.speed = speed
        self.motor_left.effort(speed)
        self.motor_right.effort(speed)

    def update(self) -> None:
        self.time.append(time.ticks_us())
        if len(self.time) == 5:
            self.motor_left.enable()
            self.motor_right.enable()
        else:
            self.encoder_left.update()
            self.encoder_right.update()
            self.left_postion.append(self.encoder_left.position())
            self.right_postion.append(self.encoder_right.position())
            self.left_velocity.append(self.encoder_left.velocity())
            self.right_velocity.append(self.encoder_right.velocity())

    def run_speed(self, speed: int) -> str:
        self.motor_left.effort(0)
        self.motor_left.disable()
        self.motor_right.effort(0)
        self.motor_right.disable()
        self.encoder_left.zero()
        self.encoder_left.zero()

        print(f"speed: {speed}")
        import gc

        gc.collect()
        for i in range(2, 0, -1):
            print(f"run in {i}")
            time.sleep(1)
        self.set_speed(speed)
        print(speed)
        for _ in range(100):
            time.sleep_ms(5)
            self.update()
        self.set_speed(0)
        self.motor_left.disable()
        self.motor_right.disable()
        self.encoder_left.zero()
        self.encoder_right.zero()
        gc.collect()
        file_name = f"{speed}_data.csv"
        file_exsists = False
        try:
            _ = os.stat(file_name)
            file_exsists = True
            raise BaseException("Remove the files in the rom before running again")
        except:
            file_exsists = False
        if file_exsists:
            raise BaseException("Remove the files in the rom before running again")
        else:
            with open(file_name, "w+") as f:
                csv_output_string = ""
                csv_output_string += "time, "
                csv_output_string += f"{self.time}".split("[")[1].split("]")[0]
                csv_output_string += "\n"
                csv_output_string += "left_position, "
                csv_output_string += f"{self.left_postion}".split("[")[1].split("]")[0]
                csv_output_string += "\n"
                csv_output_string += "right_position, "
                csv_output_string += f"{self.right_postion}".split("[")[1].split("]")[0]
                csv_output_string += "\n"
                csv_output_string += f"left_velocity, "
                csv_output_string += f"{self.right_velocity}".split("[")[1].split("]")[
                    0
                ]
                csv_output_string += "\n"
                csv_output_string += f"right_velocity, "
                csv_output_string += f"{self.left_velocity}".split("[")[1].split("]")[0]
                print(csv_output_string, file=f)
            print(f"time: {self.time}")
            print(f"lelft pos: {self.left_postion}")
            print(f"right pos: {self.left_postion}")
            print(f"left_velocity: {self.left_velocity}")
            print(f"right_velocity: {self.right_velocity}")
            self.left_postion = array("f")
            self.right_postion = array("f")
            self.time = array("i")
            self.left_velocity = array("f")
            self.right_velocity = array("f")
        return file_name

    @classmethod
    def run(cls) -> list[str]:
        output = []
        # Initialize collector class
        # Main While Loop
        motor_speeds = range(100, 0, -10)
        coll = cls()
        coll.encoder_left.zero()
        coll.encoder_right.zero()
        for speed in motor_speeds:
            output.append(coll.run_speed(speed))
        return output
