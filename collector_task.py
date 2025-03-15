import utime
import cotask
from collector import Collector

def collector_task(shares=None):
    # Set the sampling interval (dt) in milliseconds
    # Create a Collector instance
    coll = Collector()
    # Zero the encoders
    coll.encoder_left.zero()
    coll.encoder_right.zero()
    
    # Define the number of samples to collect before writing to file
    samples_to_collect = 100
    sample_count = 0

    while True:
        # Update encoder readings and append data to the collector's arrays
        coll.update()
        sample_count += 1

        # Once we've collected enough samples, write them to a CSV file
        if sample_count >= samples_to_collect:
            file_name = "collected_data_{}.csv".format(utime.ticks_ms())
            try:
                with open(file_name, 'w+') as f:
                    # Write CSV header
                    f.write("time,left_position,right_position,left_velocity,right_velocity\n")
                    # Convert each array to a comma-separated string
                    times_str = ",".join(str(x) for x in coll.time)
                    left_pos_str = ",".join(str(x) for x in coll.left_postion)
                    right_pos_str = ",".join(str(x) for x in coll.right_postion)
                    left_vel_str = ",".join(str(x) for x in coll.left_velocity)
                    right_vel_str = ",".join(str(x) for x in coll.right_velocity)
                    # Write data rows to file
                    f.write(times_str + "\n")
                    f.write(left_pos_str + "\n")
                    f.write(right_pos_str + "\n")
                    f.write(left_vel_str + "\n")
                    f.write(right_vel_str + "\n")
                print("Data logged to", file_name)
            except Exception as e:
                print("Error writing data:", e)
            
            # Reset the data arrays for the next collection period
            coll.left_postion = type(coll.left_postion)([])
            coll.right_postion = type(coll.right_postion)([])
            coll.time = type(coll.time)([])
            coll.left_velocity = type(coll.left_velocity)([])
            coll.right_velocity = type(coll.right_velocity)([])
            sample_count = 0

        # Yield control so that other tasks can run
        yield 0
