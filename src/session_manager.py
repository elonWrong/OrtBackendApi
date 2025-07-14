import json
import os
import time
import shutil
import cv2 as cv
import numpy as np


class SessionManager:
    DIR_PATH = 'data\\Sensors\\'
    RIGHT_PATH = DIR_PATH+'StereoRight'
    LEFT_PATH = DIR_PATH+'StereoLeft'
    IMU_PATH = DIR_PATH+'Imu'
    RANGE_FINDER_PATH = DIR_PATH+'RangeFinder'

    def __init__(self):
        self.sessions = []
        with open(os.path.join(self.DIR_PATH, 'Sessions', 'session_data.jsonl'), "r") as f:
            self.sessions = [json.loads(line) for line in f]

    def create_session(self, label="data collection"):
        session = {
            'session_id': self.sessions[-1]['session_id'] + 1 if self.sessions else 1,
            'start_time': time.time(),
            'label': label,
        }
        with open(os.path.join(self.DIR_PATH, 'Sessions', 'session_data.jsonl'), "a") as f:
            f.write(json.dumps(session) + "\n")
        return session
    
    def package_session(self, session_id):
        session = next((s for s in self.sessions if s['session_id'] == session_id), None)
        if not session:
            raise ValueError(f"Session with ID {session_id} not found.")

        right_dir = os.path.join(self.RIGHT_PATH, str(session_id))
        left_dir = os.path.join(self.LEFT_PATH, str(session_id))

        imu_session_file = os.path.join(self.IMU_PATH, str(session_id))
        range_finder_session_file = os.path.join(self.RANGE_FINDER_PATH, str(session_id))

        right_images = self.read_all_images_to_np(right_dir)
        left_images = self.read_all_images_to_np(left_dir)

        session_package_dir = os.path.join(self.DIR_PATH, 'SessionPackages', str(session_id))
        os.makedirs(session_package_dir, exist_ok=True)
        right_images_packaged_file = os.path.join(session_package_dir, f"{session_id}_right_images.npy")
        left_images_packaged_file = os.path.join(session_package_dir, f"{session_id}_left_images.npy")
        np.save(right_images_packaged_file, right_images)
        np.save(left_images_packaged_file, left_images)

        shutil.copy(imu_session_file, session_package_dir)
        shutil.copy(range_finder_session_file, session_package_dir)
    
    def read_all_images_to_np(dir_path):
        images = []
        for file in os.listdir(dir_path):
            if file.endswith('.jpg') or file.endswith('.png'):
                img = cv.imread(os.path.join(dir_path, file))
                if img is not None:
                    images.append(img)
        images = np.array(images)
        return images

    def delete_session(self, session_ids):
        sessions_to_delete = set(session_ids)
        for session in self.sessions:
            if session['session_id'] in sessions_to_delete:
                # Remove directories
                shutil.rmtree(os.path.join(self.RIGHT_PATH, str(session['session_id'])), ignore_errors=True)
                shutil.rmtree(os.path.join(self.LEFT_PATH, str(session['session_id'])), ignore_errors=True)
                os.rmdir(os.path.join(self.IMU_PATH, str(session['session_id'])))
                os.rmdir(os.path.join(self.RANGE_FINDER_PATH, str(session['session_id'])))
        self.sessions = [session for session in self.sessions if session['session_id'] not in sessions_to_delete]
        with open(os.path.join(self.DIR_PATH, 'Sessions', 'session_data.jsonl'), "w") as f:
            for session in self.sessions:
                f.write(json.dumps(session) + "\n")
                