import pyb
import struct
import HAL
from task_share import Share
import gc


class BNO055:
    # BNO055 I2C Address
    I2C_ADDR = 0x28

    # Register addresses
    REG_OPR_MODE = 0x3D  # Operation Mode Register
    REG_CALIB_STAT = 0x35  # Calibration Status Register
    REG_EULER_ANGLES = 0x1A  # Euler Angles Data Register
    REG_GYRO_DATA = 0x14  # Gyroscope Data Register
    REG_CALIBRATION_DATA = 0x55  # Starting register for calibration coefficients

    # BNO055 Modes 
    MODE_CONFIG = 0x00          # Configuration mode
    MODE_ACCONLY = 0x01         # Accelerometer only mode
    MODE_MAGONLY = 0x02         # Magnetometer only mode
    MODE_GYRONLY = 0x03         # Gyroscope only mode
    MODE_ACCMAG = 0x04          # Accelerometer and Magnetometer mode
    MODE_ACCGYRO = 0x05         # Accelerometer and Gyroscope mode
    MODE_MAGGYRO = 0x06         # Magnetometer and Gyroscope mode
    MODE_AMG = 0x07             # Accelerometer, Magnetometer, and Gyroscope mode
    MODE_IMUPLUS = 0x08         # IMU mode with additional features
    MODE_COMPASS = 0x09         # Compass mode
    MODE_M4G = 0x0A             # 4th Generation mode
    MODE_NDOF_FMC_OFF = 0x0B    # Fusion mode with no sensor fusion
    MODE_NDOF = 0x0C            # Full sensor fusion mode


    # Task State Variables
    S0_CALIBRATION = 0
    S1_ANGLES = 1
    S2_VELCOITY = 2
    S3_HOLDING = 3

    def __init__(self, debug=False, profiler=False):
        # Initialize I2C
        print("Initilizing IMU")
        self.profiler = profiler
        self.i2c = HAL.__IMU__.I2C  # Use the pre-configured I2C instance
        self.state = self.S1_ANGLES
        self.initialize_imu()
        self.calibrate_if_needed()
        self.debug = debug
        print("\\Initilizing IMU")
        gc.collect()

    def initialize_imu(self):
        # Initialize the BNO055 in NDOF mode
        self.set_mode(self.MODE_CONFIG)
        try:
            self.set_mode(self.MODE_NDOF)
            print("[BNO055] Initialized in NDOF Mode.")
        except:
            print("[ERROR] BNO055 not detected. Check wiring!")

    def set_mode(self, mode):
        try:
            # Set the operation mode of the BNO055
            self.i2c.mem_write(mode, self.I2C_ADDR, self.REG_OPR_MODE)
            pyb.delay(10)
        except OSError as e:
            print("[ERROR] BNO055 cannot set mode")
            raise e

    def get_calibration_status(self) -> tuple[int, int, int, int]:
        # Read the calibration status
        status = self.i2c.mem_read(1, self.I2C_ADDR, self.REG_CALIB_STAT)[0]
        sys = (status >> 6) & 0x03  # System calibration status
        gyro = (status >> 4) & 0x03  # Gyroscope calibration status
        accel = (status >> 2) & 0x03  # Accelerometer calibration status
        mag = status & 0x03  # Magnetometer calibration status
        return (sys, gyro, accel, mag)

    def get_euler_angles(self) -> tuple[int, int, int]:
        # Reads Euler angles (heading, pitch, roll) from the IMU
        raw_data = self.i2c.mem_read(6, self.I2C_ADDR, self.REG_EULER_ANGLES)
        heading, pitch, roll = struct.unpack("<hhh", raw_data)
        return (
            heading,
            pitch,
            roll,
        )  # Undid conversion in order to possibly improve performance

    def get_angular_velocity(self) -> tuple[float, float, float]:
        # Reads angular velocity (gyroscope data) from the IMU
        raw_data = self.i2c.mem_read(6, self.I2C_ADDR, self.REG_GYRO_DATA)
        gyro_x, gyro_y, gyro_z = struct.unpack("<hhh", raw_data)
        return (
            gyro_x,
            gyro_y,
            gyro_z,
        )  # Undid conversion in order to possibly improve performance

    def get_calibration_data(self):
        # Reads calibration coefficients from the IMU
        return self.i2c.mem_read(22, self.I2C_ADDR, self.REG_CALIBRATION_DATA)

    def write_calibration_data(self, data):
        # Writes calibration coefficients to the IMU
        if len(data) != 22:
            print("[ERROR] Invalid calibration data size.")
            return
        self.i2c.mem_write(data, self.I2C_ADDR, self.REG_CALIBRATION_DATA)

    def save_calibration(self, filename="IMUcalibration.txt"):
        # Saves calibration data to a file
        try:
            with open(filename, "wb") as f:
                f.write(self.get_calibration_data())
            print("[BNO055] Calibration saved successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to save calibration: {e}")

    def load_calibration(self, filename="IMUcalibration.txt"):
        # Loads calibration data from a file

        from os import listdir

        file_list = listdir()
        if filename in file_list:
            with open(filename, "rb") as f:
                data = f.read()
                self.write_calibration_data(data)
            print("[BNO055] Calibration loaded from file.")
            return True
        else:
            print(f"[BNO055] Needs to be done manually:")
            return False

    def calibrate_if_needed(self):
        # Check and perform calibration if needed
        # if not self.load_calibration():
        # self.set_mode(self.MODE_CONFIG)
        # print("[BNO055] Manual calibration required. Move IMU in all directions.")
        if not self.load_calibration():
            calibration_done = False
            while not calibration_done:  # Wait for full system calibration
                status = self.get_calibration_status()
                calibration_done = (status[1] + status[2] + status[3]) == 9
                print("Calibrating...", self.get_calibration_status())
                pyb.delay(500)
            self.save_calibration()
        print("[BNO055] Calibration complete and saved.")
        # self.set_mode(self.MODE_NDOF)

    def task(self, shares):
        import gc

        heading_share: Share
        target_heading: Share
        (heading_share, target_heading) = shares
        imu = self
        while True:
            gc.collect()
            angles = imu.get_euler_angles()
            if self.debug:
                print(
                    f"Target Heading: {target_heading.get()} | Measured Heading: {heading_share.get()}"
                )
            heading_share.put(angles[0])
            yield imu.state
