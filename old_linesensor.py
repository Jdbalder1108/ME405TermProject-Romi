import HAL
import task_share
from prelude import *

class LineSensor:
    # Define finite state machine (FSM) states
    S0_CALIBRATING = 0  # State when the sensor is gathering calibration data (min/max values)
    S2_PROCESSING = 2   # State when the sensor data is processed to compute the centroid

    def __init__(self):
        # Initialize the line sensor object
        self.sensors = HAL.__LINE_SENSOR__.CHANNELS         # Ensure CHANNELS is a list of sensor objects
        self.calibration_min = [4095] * 13                  # Initial high values for calibration (min)
        self.calibration_max = [0] * 13                     # Initial low values for calibration (max)
        self.state = self.S2_PROCESSING                    # Start in the CALIBRATING state
        self.calibration_samples = 100                      # Total number of calibration samples required
        self.calibration_data: list[tuple[float, float]] = []
        self.sample_count = 0                               # Counter for calibration samples taken
        self.centroid = None                                # Last computed centroid value


        from os import listdir
        filelist = listdir()
        if "IR_cal.txt" not in filelist:
            self.calibrate_step()
        else:
            if self.calibration_data == []:
                with open("IR_cal.txt", "r") as f:
                    self.calibration_data = list(filter(lambda item: item != '', map(lambda str_list: ((((str_list[0]+(-6))) / (float(str_list[1][0]) - float(str_list[1][1]))), float(str_list[1][1])), enumerate(filter(lambda item: item != '', map(lambda item_str: item_str.split("(")[1].split(","), filter(lambda item: item != '', f.readline().split("[")[1].split("]")[0].split(")"))))))))

    def calibrate_step(self):
        # Calibration step to update min/max values for each sensor
        # if self.sample_count < self.calibration_samples:
        #     # For each sensor, update calibration bounds based on the current reading
        #     for i, sensor in enumerate(self.sensors):
        #         reading = sensor.read()
        #         # self.calibration_min[i] = min(self.calibration_min[i], reading)
        #         # self.calibration_max[i] = max(self.calibration_max[i], reading)
        #     self.sample_count += 1  # Increment the calibration sample counter
        # else:
        #     # Once enough samples have been collected, finish calibration
        #     print("Calibration complete.")
        #     self.state = self.S1_READING  # Transition to the READING state
        continue_min = input("Place on White. Ready to continue [Y]/N: ")
        if continue_min == "N":
            raise BaseException("Calibration Stopped")
        data_min = []
        for sensor in self.sensors:
            sensor_values = []
            while len(sensor_values) < self.calibration_samples:
                sensor_values.append(sensor.read())
            data_min.append(sum(sensor_values) / len(sensor_values))
        continue_max = input("Place on Black. Ready to continue [Y]/N: ")
        print(continue_max)
        if continue_max == "N":
            raise BaseException("Calibration Stopped")
        data_max = []
        for sensor in self.sensors:
            sensor_values = []
            while len(sensor_values) < self.calibration_samples:
                sensor_values.append(sensor.read())
            data_max.append(sum(sensor_values) / len(sensor_values))
        with open("IR_cal.txt", "wt+") as f:
            data = list(zip(data_max, data_min))
            print(data)
            print(data, file=f)
            self.calibration_data = data


    def calculate_centroid(self) -> float:
        # Read normalized sensor values from each sensor
        # normalized: float = 0.0
        # for i, value in enumerate(raw_values):
        #     min_val = self.calibration_min[i]
        #     max_val = self.calibration_max[i]
        #     if max_val > min_val:
        #         normalized_value = (value - min_val) * 1000 // (max_val - min_val)
        #         normalized.append(min(max(normalized_value, 0), 1000))
        #     else:
        #         normalized.append(0)
        # weight = -6
        # for i, sensor in enumerate(self.sensors):
        #     value = sensor.read()
        #     computed_weight = self.calibration_data[i][1]
        #     max_val = self.calibration_data[i][0]
        #     val = clamp(sensor.read(), self.calibration_data[i][1], self.calibration_data[i][0])
        #     normalized.append(((val-min_val)/(max_val - min_val)) * weight)
        #     weight += 1
        # Pre computed static values to optimize sensor reading speed.
        # ((val-min_val)/(max_val - min_val)) * weight ==> val-min_val*pre_computed_weight
        # The clamp fuction calls were also removed for speed reasons. 
        return sum([(sensor.read()-self.calibration_data[i][1])*self.calibration_data[i][0] for (i, sensor) in enumerate(self.sensors)])

    
    def task(self, shares):
        # Task function to run the line sensor FSM
        # print(shares)
        centroid_share: task_share.Share = shares  # Shared variable to store the centroid value for other tasks
        line_sensor = self

        # Main loop for the line sensor task
        while True:
                # PROCESSING: Calculate the centroid from sensor readings.
                # line_sensor.centroid = line_sensor.calculate_centroid()
                # yield line_sensor.state
                # print(line_sensor.centroid)
                # Update the shared variable with the new centroid value
                centroid_share.put(sum([(sensor.read()-self.calibration_data[i][1])*self.calibration_data[i][0] for (i, sensor) in enumerate(self.sensors)]))
                # After processing, return to the READING state for the next cycle.
                yield line_sensor.state
