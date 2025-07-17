import os
import cv2 as cv
import json
import time
from imu import IMU
from camera import Camera
from range_finder import RangeFinder
from session_manager import SessionManager


class SensorFuser:

    def __init__(self, frame_rate=1, session_label="data collection"):
        print("Initializing SensorFuser...")
        self.imu = IMU()
        self.left_camera = Camera(0)
        self.right_camera = Camera(1)
        self.range_finder = RangeFinder()

        self.session_manager = SessionManager() 

        self.imu.start_track_thread()
        self.range_finder.start_reading_thread()

        self.frame_rate = frame_rate
        self.current_fused_data = None

        print("SensorFuser initialized with frame rate:", self.frame_rate)

    def create_frame(self):
        imu_data = self.imu.get_frame()
        left_camera_data = self.left_camera.get_frame()
        right_camera_data = self.right_camera.get_frame()
        range_data = self.range_finder.get_frame()

        print("range: " + str(range_data))
        print("imu: " + str(imu_data))

        # Combine the data from all sensors
        fused_data = {
            'imu': imu_data,
            'left_camera': left_camera_data,
            'right_camera': right_camera_data,
            'range_finder': range_data,
            'timestamp': time.time()
        }
        self.current_fused_data = fused_data
        return fused_data
            
    def run(self):
        print("Starting data collection...")
        try:
            while True:
                print("Collecting data...")
                data = self.create_frame()
                self.session_manager.store_data(data)
                time.sleep(1 / self.frame_rate)
                print("Data collected and stored:", data['timestamp'])
        except KeyboardInterrupt:
            print("Data collection stopped.")
        except Exception as e:
            print(f"An error occurred: {e}")
        #finally:
        #    print("Finalizing session...")
        #    self.session_manager.package_session(self.session_manager.current_session['session_id'])

if __name__ == "__main__":
    sensor_fuser = SensorFuser(session_label="Test Session")
    sensor_fuser.run()
