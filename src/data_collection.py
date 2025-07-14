import os
import cv2 as cv
import json

from time import time
from imu import IMU
from camera import Camera
from range_finder import RangeFinder
from session_manager import SessionManager


class SensorFuser:
    DIR_PATH = 'data\\Sensors\\'
    RIGHT_PATH = DIR_PATH+'StereoRight'
    LEFT_PATH = DIR_PATH+'StereoLeft'
    IMU_PATH = DIR_PATH+'Imu'
    RANGE_FINDER_PATH = DIR_PATH+'RangeFinder'

    def __init__(self, session_label="data collection"):

        self.imu = IMU()
        self.left_camera = Camera(0)
        self.right_camera = Camera(1)
        self.range_finder = RangeFinder()

        self.session_manager = SessionManager()
        self.session = self.session_manager.create_session(session_label)

    def create_directories(self):
        self.right_dir = os.path.join(self.RIGHT_PATH, str(self.session['session_id']))
        self.left_dir = os.path.join(self.LEFT_PATH, str(self.session['session_id']))
        self.imu_session_file = os.path.join(self.IMU_PATH, str(self.session['session_id']))
        self.range_finder_session_file = os.path.join(self.RANGE_FINDER_PATH, str(self.session['session_id']))

        os.makedirs(self.right_dir, exist_ok=True)
        os.makedirs(self.left_dir, exist_ok=True)


    def collect_data(self):
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

        return fused_data
    
    def store_data(self, data):
        # Here you would implement the logic to store the data, e.g., in a database or file
        right_image_path = f"{self.right_dir}/{data['timestamp']}_right.jpg"
        left_image_path = f"{self.left_dir}/{data['timestamp']}_left.jpg"

        cv.imwrite(right_image_path, data['right_camera'])
        cv.imwrite(left_image_path, data['left_camera'])

        data['imu']['global_timestamp'] = data['timestamp']
        data['range_finder']['global_timestamp'] = data['timestamp']

        with open(self.imu_session_file, 'a') as imu_file:
            imu_file.write(json.dumps(data['imu']) + "\n")

        with open(self.range_finder_session_file, 'a') as range_file:
            range_file.write(json.dumps(data['range_finder']) + "\n")

    def run(self):
        self.create_directories()
        try:
            while True:
                data = self.collect_data()
                self.store_data(data)
                print(f"Data collected at {data['timestamp']}")
        except KeyboardInterrupt:
            print("Data collection stopped.")
        finally:
            self.session_manager.package_session(self.session['session_id'])

if __name__ == "__main__":
    sensor_fuser = SensorFuser(session_label="Test Session")
    sensor_fuser.run()
