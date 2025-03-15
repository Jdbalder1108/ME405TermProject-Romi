from prelude import *


class Shares:
    def __init__(self):
        self.is_built = False

    def build(self):
        import task_share, userbutton, bump_sensors

        self.is_built = True
        ## ----------------------- <Shares> -------------------------- ##

        # Create shared variable for centroid data
        self.centroid_share = task_share.Share("f", True, "Centroid")

        # Get shared control flag from userbutton.py
        self.control_flag = userbutton.get_control_flag_share()

        # Create an IMU Angle Share
        self.heading_share = task_share.Share("h", True, "Heading Angle")

        # Target Heading Share
        self.target_heading_share = task_share.Share("h", True, "Target Heading")

        # Motor Velocity Share
        # self.left_motor_velocity_set_point_share =task_share.Share(
        #     "f", True, "Left Motor Velocity"
        # )
        # self.right_motor_velocity_set_point_share =task_share.Share(
        #     "f", True, "Right Motor Velocity"
        # )
        self.yaw_velocity_share = task_share.Share("f", True, "Yaw Velocity Share")

        # Position Shares
        self.left_motor_position_share = task_share.Share(
            "f", True, "Left Motor Position"
        )
        self.right_motor_position_share = task_share.Share(
            "f", True, "Right Motor Position"
        )
        self.right_motor_position_reset_flag = task_share.Share(
            "H", True, "Right Motor Position Reset Flag"
        )
        self.left_motor_position_reset_flag = task_share.Share(
            "H", True, "Left Motor Position Reset Flag"
        )

        # Motor Control State Share
        self.motor_control_state_share = task_share.Share(
            "h", True, "Motor Control State"
        )
        self.bump_sensor = bump_sensors.BumpSensor().get_bump_flag_share()

        self.startng_heading_share = task_share.Share(
            "h", True, "Starting Heading Share"
        )

        ## ----------------------- </Shares> ----------------------- ##
        return self

    def __repr__(self) -> str:
        if not self.is_built:
            self.build()
        return "\n".join(
            [
                f"{self.centroid_share}: {self.centroid_share.get()}",
                f"{self.control_flag}: {self.control_flag.get()}",
                f"{self.heading_share}: {self.heading_share.get()}",
                f"{self.target_heading_share}: {self.target_heading_share.get()}",
                f"{self.yaw_velocity_share}: {self.yaw_velocity_share.get()}",
                f"{self.left_motor_position_share}: {self.left_motor_position_share.get()}",
                f"{self.right_motor_position_share}: {self.right_motor_position_share.get()}",
                f"{self.right_motor_position_reset_flag}: {self.right_motor_position_reset_flag.get()}",
                f"{self.left_motor_position_reset_flag}: {self.left_motor_position_reset_flag.get()}",
                f"{self.motor_control_state_share}: {self.motor_control_state_share.get()}",
                f"{self.bump_sensor}: {self.bump_sensor.get()}",
                f"{self.startng_heading_share}: {self.startng_heading_share.get()}",
            ]
        )


class TaskBuilder:
    import cotask

    def __init__(self) -> None:
        import cotask

        self.task_list: list[cotask.Task] = []
        self.shares = Shares()
        self.is_built = False
        self.vehicle_conrol_task: cotask.Task | None = None
        self.line_task: cotask.Task | None = None
        self.left_motor_task: cotask.Task | None = None
        self.right_motor_task: cotask.Task | None = None
        self.imu_task: cotask.Task | None = None
        self.course_task: cotask.Task | None = None
        self.debug_speed = False

    def vehicle_conrol(self, debug=False):
        import cotask, motor_control_task

        if self.is_built:
            self.fail()
        if not self.shares.is_built:
            self.shares.build()
        if debug and not self.debug_speed:
            self.debug_speed = True
        self.vehicle_conrol_task = cotask.Task(
            motor_control_task.MotorControl(debug).task,
            name="MotorControl",
            priority=20,
            period=40,
            profile=True,
            trace=True,
            shares=(
                self.shares.centroid_share,
                self.shares.heading_share,
                self.shares.target_heading_share,
                self.shares.motor_control_state_share,
                self.shares.control_flag,
                self.shares.yaw_velocity_share,
            ),
        )
        self.append(self.vehicle_conrol_task)
        return self

    def line_sensor(self, debug=False, ignore_button=False):
        import cotask, line_sensor

        if ignore_button:
            print("Profiling Line Sensor Check, in task builder")
        if debug:
            print("Debug Flag set when making line sensor task")
        if self.is_built:
            self.fail()
        if not self.shares.is_built:
            self.shares.build()
        if debug and not self.debug_speed:
            self.debug_speed = True
        self.line_task = cotask.Task(
            line_sensor.LineSensor(debug, ignore_button).task,
            name="LineSensor",
            priority=30,
            period=40,
            profile=True,
            trace=True,
            shares=(
                self.shares.control_flag,
                self.shares.centroid_share,
            ),
        )
        self.append(self.line_task)
        return self

    def imu(self, debug=False, profiler=True):
        import cotask, bno055

        if self.is_built:
            self.fail()
        if not self.shares.is_built:
            self.shares.build()
        if debug and not self.debug_speed:
            self.debug_speed = True
        self.imu_task = cotask.Task(
            bno055.BNO055(debug, profiler).task,
            name="IMU",
            priority=10,
            period=40,
            profile=True,
            trace=True,
            shares=(self.shares.heading_share, self.shares.target_heading_share),
        )
        self.append(self.imu_task)
        return self

    def motor(self, side: int, debug=False):
        import cotask, motor

        if self.is_built:
            self.fail()
        if not self.shares.is_built:
            self.shares.build()
        if debug and not self.debug_speed:
            self.debug_speed = True
        task = cotask.Task(
            motor.Motor(side, debug).task,
            "Left Motor Task" if side == Vehicle_Side.LEFT else "Right Motor Task",
            priority=40,
            period=40,
            profile=True,
            shares=(
                self.shares.control_flag,
                self.shares.yaw_velocity_share,
                (
                    self.shares.left_motor_position_reset_flag
                    if side == Vehicle_Side.LEFT
                    else self.shares.right_motor_position_reset_flag
                ),
                (
                    self.shares.left_motor_position_share
                    if side == Vehicle_Side.LEFT
                    else self.shares.right_motor_position_share
                ),
            ),
        )
        if side == Vehicle_Side.LEFT:
            self.left_motor_task = task
        else:
            self.right_motor_task = task
        self.append(task)
        return self

    def course(self, debug=False):
        import cotask, course

        if self.is_built:
            self.fail()
        if not self.shares.is_built:
            self.shares.build()
        self.course_task = cotask.Task(
            course.CourseCompletion(debug).task,
            "Course",
            priority=5,
            period=40,
            profile=True,
            shares=(
                self.shares.control_flag,
                self.shares.motor_control_state_share,
                self.shares.target_heading_share,
                self.shares.left_motor_position_share,
                self.shares.right_motor_position_share,
                self.shares.heading_share,
                self.shares.centroid_share,
                self.shares.left_motor_position_reset_flag,
                self.shares.right_motor_position_reset_flag,
                self.shares.startng_heading_share,
                self.shares.bump_sensor,
            ),
        )
        self.append(self.course_task)
        return self

    def append(self, task: cotask.Task):
        if not self.shares.is_built:
            self.shares.build()
        if task not in self.task_list:
            self.task_list.append(task)
        return self

    def motors(self, debug=False):
        if self.is_built:
            self.fail()
        if not self.shares.is_built:
            self.shares.build()
        self.motor(Vehicle_Side.LEFT, debug).motor(Vehicle_Side.RIGHT, debug)
        return self

    def all(self, debug=False):
        if not self.shares.is_built:
            self.shares.build()
        self.vehicle_conrol().motors().course()
        return self

    def build(self):
        import cotask

        if not self.shares.is_built:
            self.shares.build()

        for task in self.task_list:
            cotask.task_list.append(task)

        self.is_built = True

    def run(self):
        import cotask, gc

        print(gc.mem_free())
        gc.collect()
        print(gc.mem_free())

        if not self.is_built:
            self.build()
        gc.collect()
        if self.course_task in self.task_list and self.course_task != None:
            print("Running Main")
            while True:
                cotask.task_list.pri_sched()
        else:
            print("Not Running Main")
            while self.shares.bump_sensor.get() == 0:
                cotask.task_list.pri_sched()

        self.exit()

    def fail(self):
        raise BaseException(
            "TaskShare has already been built, are you trying to run more than one control function"
        )

    def exit(self):
        import HAL, cotask

        print("\nTerminating Program")
        HAL.__MOTOR_LEFT__.ENABLE.low()
        HAL.__MOTOR_RIGHT__.ENABLE.low()
        print(self.shares)
        print(cotask.task_list)
        print(f"Voltage: {get_voltage(start_up=True)}")


task_builder = TaskBuilder()
