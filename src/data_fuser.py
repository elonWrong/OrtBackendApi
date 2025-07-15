import os
import cv2 as cv
import json

from time import time
from imu import IMU
from camera import Camera
from range_finder import RangeFinder
from session_manager import SessionManager


class SensorFuser:

    def __init__(self, frame_rate=1, session_label="data collection"):

        self.imu = IMU()
        self.left_camera = Camera(0)
        self.right_camera = Camera(1)
        self.range_finder = RangeFinder()

        self.session_manager = SessionManager() 
        self.session = self.session_manager.create_session(session_label)

        self.frame_rate = frame_rate
        self.current_fused_data = None


    def create_frame(self):
        imu_data = self.imu.get_data()
        left_camera_data = self.left_camera.get_frame()
        right_camera_data = self.right_camera.get_frame()
        range_data = self.range_finder.read_distance()

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
        try:
            while True:
                data = self.create_frame()
                self.session_manager.store_data(data)
                time.sleep(1 / self.frame_rate)
        except KeyboardInterrupt:
            print("Data collection stopped.")
        finally:
            self.session_manager.package_session(self.session['session_id'])

if __name__ == "__main__":
    sensor_fuser = SensorFuser(session_label="Test Session")
    sensor_fuser.run()
