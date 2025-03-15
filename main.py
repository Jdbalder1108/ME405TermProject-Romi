def run(fun, *args):
    import cotask, tasks, gc

    try:
        if tasks.task_builder.is_built:

            print("Reseting Task List")
            tasks.task_builder = tasks.TaskBuilder()
            tasks.task_builder.shares = tasks.Shares()
            cotask.task_list = cotask.TaskList()
            gc.collect()
        gc.collect()
        print("in run")
        fun(args)
        tasks.task_builder.run()

    except BaseException as e:
        print(e)
    finally:
        tasks.task_builder.exit()
    return


def main(in_run=False):
    import tasks, utime

    if not in_run:
        run(main, True)
        return
    ## ------------------------ <Tasks> ------------------------ ##
    tasks.task_builder.vehicle_conrol().motors().course(debug=True)
    print("Tasks Added")
    if not tasks.task_builder.shares.is_built:
        tasks.task_builder.shares.build()
    print("Sleeping")
    utime.sleep(0.5)
    tasks.task_builder.shares.control_flag.put(1)
    ## ------------------------ </Tasks> ------------------------ ##
    return


def line_sensor_test(in_run=False):
    import HAL

    if not in_run:
        run(line_sensor_test, True)
        return
    while True:
        print([channel.read() for channel in HAL.__LINE_SENSOR__.CHANNELS])


def test_imu(in_run=False):
    import bno055

    if not in_run:
        run(test_imu, True)
        return
    imu = bno055.BNO055()  # Initialize the IMU using HAL-configured I2C
    import pyb

    print("\n[BNO055] Checking Calibration Status...")
    imu.calibrate_if_needed()  # Load calibration or start manual calibration

    print("\n[BNO055] IMU is ready! Printing Euler angles...\n")
    pyb.delay(1000)

    while True:
        heading, pitch, roll = imu.get_euler_angles()
        sys, gyro, accel, mag = imu.get_calibration_status()

        print(
            f"Euler Angles - Heading: {heading:.2f}, Pitch: {pitch:.2f}, Roll: {roll:.2f}"
        )
        print(
            f"Calibration Status - System: {sys}, Gyro: {gyro}, Accel: {accel}, Mag: {mag}\n"
        )

        pyb.delay(500)  # Delay between readings


def I2C_test(in_run=False):
    import HAL, pyb

    if not in_run:
        run(I2C_test, True)
        return
    print(HAL._PB8)
    print(HAL._PB9)
    iic = pyb.I2C(1)
    iic = pyb.I2C(1, pyb.I2C.CONTROLLER)
    iic.init(pyb.I2C.CONTROLLER)
    print(iic)
    addrs = []
    while addrs == []:
        addrs = iic.scan()
        print(addrs)
    # for i in range(100):
    #     print(f'addr: {i} | is_ready: {iic.is_ready(i)}')
    #     utime.sleep_ms(100)


def motor_characterization(in_run=False):
    import utime

    if not in_run:
        run(motor_characterization, True)
        return
    from collector import Collector

    for i in range(15, 0, -1):
        print(f"run in {i}")
        utime.sleep(1)
    Collector.run()
    return


def motor_test(test_pwm_percent: int, in_run=False):
    import motor, task_share, tasks, utime, cotask, prelude

    if not in_run:
        run(motor_test, test_pwm_percent, True)
        return
    print("Motor Test Start")

    if prelude.SPEED_SET_POINT != 0:
        prelude.SPEED_SET_POINT = 0

    left_motor_velocity_set_point_share = task_share.Share(
        "f", True, "Left Motor Velocity"
    )
    right_motor_velocity_set_point_share = task_share.Share(
        "f", True, "Right Motor Velocity"
    )
    shares = tasks.task_builder.shares.build()
    while shares.control_flag.get() == 0:
        continue
    while shares.control_flag.get() == 1:
        left_motor = motor.Motor(prelude.Vehicle_Side.LEFT)
        right_motor = motor.Motor(prelude.Vehicle_Side.RIGHT)
        left_motor.__hal__.PWM.pulse_width_percent(test_pwm_percent)
        right_motor.__hal__.PWM.pulse_width_percent(test_pwm_percent)
        left_motor.set_dir(prelude.MotorDirection.FWD)
        right_motor.set_dir(prelude.MotorDirection.REV)
        left_motor.enable()
        right_motor.enable()
        ticks = 0
        while ticks < 5:
            right_motor.encoder.update()
            left_motor.encoder.update()
            utime.sleep(0.5)
            ticks += 1
        left_velocity = left_motor.encoder.__velocity__
        right_velocity = right_motor.encoder.__velocity__
        left_motor.disable()
        right_motor.disable()
        print(
            f"for {test_pwm_percent}% PWN Pecent: Left Motor Velocity = {left_velocity}"
        )
        print(
            f"for {test_pwm_percent}% PWN Pecent: Right Motor Velocity = {right_velocity}"
        )
        left_motor_velocity_set_point_share.put(left_velocity)
        right_motor_velocity_set_point_share.put(right_velocity)
        left_motor_task = cotask.Task(
            left_motor.task,
            "Left Motor Task",
            priority=40,
            period=10,
            profile=True,
            shares=(
                shares.control_flag,
                left_motor_velocity_set_point_share,
                shares.left_motor_position_reset_flag,
                shares.left_motor_position_share,
            ),
        )

        right_motor_task = cotask.Task(
            motor.Motor(prelude.Vehicle_Side.RIGHT).task,
            "Right Motor Task",
            priority=40,
            period=10,
            profile=True,
            shares=(
                shares.control_flag,
                right_motor_velocity_set_point_share,
                shares.right_motor_position_reset_flag,
                shares.right_motor_position_share,
            ),
        )
        cotask.task_list.append(right_motor_task)
        cotask.task_list.append(left_motor_task)
    return


def follow_line_test(in_run=False):
    import tasks, prelude, motor_control_task

    if not in_run:
        run(follow_line_test, True)
        return
    tasks.task_builder.vehicle_conrol().line_sensor().motor(
        prelude.Vehicle_Side.LEFT
    ).motor(prelude.Vehicle_Side.RIGHT)
    tasks.task_builder.shares.motor_control_state_share.put(
        motor_control_task.MotorControl.S1_LINE_PID_CALC
    )
    return


def line_task_test(in_run=False):
    import tasks

    if not in_run:
        run(line_task_test, True)
        return
    tasks.task_builder.line_sensor(True)


def line_task_profiler(in_run=False):
    import tasks

    if not in_run:
        run(line_task_profiler, True)
        return
    tasks.task_builder.line_sensor(debug=False, ignore_button=True)


def imu_profiler(in_run=False):
    import tasks

    if not in_run:
        run(imu_profiler, True)
        return
    tasks.task_builder.imu(profiler=True)


def bump_sensor_test(in_run=False):
    import tasks

    if not in_run:
        run(bump_sensor_test, True)
        return
    print(f"is course task in task_builder: {tasks.task_builder.course_task != None}")


def drive_strait(in_run=False):
    import tasks, prelude

    if not in_run:
        run(drive_strait, True)
        return
    tasks.task_builder.motor(prelude.Vehicle_Side.LEFT, debug=True).motor(
        prelude.Vehicle_Side.RIGHT, debug=True
    )


def heading_test(in_run=False):
    import tasks, prelude, motor_control_task, utime

    if not in_run:
        run(heading_test, True)
        return

    prelude.SPEED_SET_POINT = 0
    tasks.task_builder.motor(prelude.Vehicle_Side.LEFT).motor(
        prelude.Vehicle_Side.RIGHT
    ).vehicle_conrol(debug=True)
    starting_heading = tasks.task_builder.shares.target_heading_share.get()
    print({f"Starting Heading: {starting_heading}"})
    utime.sleep(0.5)
    tasks.task_builder.shares.control_flag.put(1)
    tasks.task_builder.shares.motor_control_state_share.put(
        motor_control_task.MotorControl.S2_HEADING_PID_CALC
    )
    target_angle = prelude.get_relative_angle((-90 * 16), starting_heading)
    print(f"Target Angl: {target_angle}")
    tasks.task_builder.shares.target_heading_share.put(target_angle)


def dead_reconing_test(in_run=False):
    import tasks, cotask, utime, motor_control_task

    if not in_run:
        run(dead_reconing_test, True)
        return
    if not tasks.task_builder.shares.is_built:
        tasks.task_builder.shares.build()
    prelude.SPEED_SET_POINT = 25
    starting_heading = tasks.task_builder.shares.target_heading_share.get()
    print({f"Starting Heading: {starting_heading}"})
    utime.sleep(0.5)
    tasks.task_builder.shares.control_flag.put(1)
    tasks.task_builder.shares.motor_control_state_share.put(
        motor_control_task.MotorControl.S2_HEADING_PID_CALC
    )
    target_angle_two = prelude.get_relative_angle((180 * 16), starting_heading)
    target_angle_one = starting_heading

    def heading_test_loop(shares):
        import task_share

        heading_share: task_share.Share
        target_heading_share: task_share.Share
        left_position_share: task_share.Share
        left_position_reset: task_share.Share
        right_position_share: task_share.Share
        right_position_reset: task_share.Share
        # yaw_rate_share: task_share.Share
        (
            heading_share,
            target_heading_share,
            left_position_share,
            left_position_reset,
            right_position_share,
            right_position_reset,
            # yaw_rate_share,
        ) = shares

        target_distance = 20
        while True:
            if (
                target_heading_share.get() == target_angle_one
                and ((left_position_share.get() + right_position_share.get()) / 2)
                >= target_distance
            ):
                left_position_reset.put(1)
                right_position_reset.put(1)
                target_heading_share.put(target_angle_two)
            elif (
                target_heading_share.get() == target_angle_two
                # and yaw_rate_share.get() <= 1
                and ((left_position_share.get() + right_position_share.get()) / 2)
                >= target_distance
            ):
                left_position_reset.put(1)
                right_position_reset.put(1)
                target_heading_share.put(target_angle_one)
            # else:
            #     print(
            #         " | ".join(
            #             [
            #                 # f"Left Position: {left_position_share.get()}",
            #                 # f"Right Position: {right_position_share.get()}",
            #                 # f"Average Position: {(right_position_share.get() + left_position_share.get()) / 2}",
            #                 f"Heading: {heading_share.get()}",
            #                 f"Target Heading: {target_heading_share.get()}",
            #                 # f"Change: {(right_position_share.get() + left_position_share.get()) / 2 >= target_distance}",
            #             ]
            #         ),
            #     )
            yield

    course_loop = cotask.Task(
        heading_test_loop,
        "Heading Test Loop",
        priority=5,
        period=40,
        profile=True,
        trace=True,
        # heading_share: task_share.Share
        # target_heading_share: task_share.Share
        # left_position_share: task_share.Share
        # left_position_reset: task_share.Share
        # right_position_share: task_share.Share
        # right_position_reset: task_share.Share
        shares=(
            tasks.task_builder.shares.heading_share,
            tasks.task_builder.shares.target_heading_share,
            tasks.task_builder.shares.left_motor_position_share,
            tasks.task_builder.shares.left_motor_position_reset_flag,
            tasks.task_builder.shares.right_motor_position_share,
            tasks.task_builder.shares.right_motor_position_reset_flag,
        ),
    )
    tasks.task_builder.motors().vehicle_conrol(debug=True).append(course_loop)


if __name__ == "__main__":
    import prelude

    print(f"Voltage: {prelude.get_voltage(start_up=True)}")
    print(f"Speed Set Point: {prelude.SPEED_SET_POINT}")
    print(f"Estimated PWM Percent: {prelude.MOTOR_SET_POINT_PERCENT}")
    # main()
