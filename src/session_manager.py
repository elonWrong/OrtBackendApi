import os
import json
import time
import shutil
import cv2 as cv
import numpy as np


class SessionManager:
    BASE = os.path.dirname(__file__)
    DIR_PATH = os.path.join(BASE, '..', 'data', 'Fusion')
    RIGHT_PATH = os.path.join(DIR_PATH, 'StereoRight')
    LEFT_PATH = os.path.join(DIR_PATH, 'StereoLeft')
    IMU_PATH = os.path.join(DIR_PATH, 'Imu')
    RANGE_FINDER_PATH = os.path.join(DIR_PATH, 'RangeFinder')
    INSTRUCTIONS_PATH = os.path.join(DIR_PATH, 'Instructions')

    def __init__(self, create_session=True):
        sessions_dir = os.path.join(self.DIR_PATH, 'Sessions')

        os.makedirs(sessions_dir, exist_ok=True)
        self.session_file = os.path.join(sessions_dir, 'session_data.jsonl')

        if not os.path.exists(self.session_file):
            with open(self.session_file, "w") as f:
                pass  # create empty file
        with open(self.session_file, "r") as f:
            self.sessions = [json.loads(line) for line in f]
        
        self.current_session = None
        if create_session:
            self.create_session(label="Initial Session")

    def create_session(self, label="data collection"):
        session = {
            'session_id': self.sessions[-1]['session_id'] + 1 if self.sessions else 1,
            'start_time': time.time(),
            'label': label,
        }
        with open(self.session_file, "a") as f:
            f.write(json.dumps(session) + "\n")
        self.sessions.append(session)
        self.current_session = session
        self.create_directories()
        return session
    
    def create_directories(self):

        self.right_dir = os.path.join(self.RIGHT_PATH, "session_" + str(self.current_session['session_id']))
        self.left_dir = os.path.join(self.LEFT_PATH, "session_" + str(self.current_session['session_id']))
        self.imu_session_file = os.path.join(self.IMU_PATH, "session_" + str(self.current_session['session_id']) + ".jsonl")
        self.range_finder_session_file = os.path.join(self.RANGE_FINDER_PATH, "session_" + str(self.current_session['session_id']) + ".jsonl")
        self.instructions_session_file = os.path.join(self.INSTRUCTIONS_PATH, "session_" + str(self.current_session['session_id']) + ".jsonl")

        print("IMU path:", self.imu_session_file)
        print("Range Finder path:", self.range_finder_session_file)
        print("Instructions path:", self.instructions_session_file)
        print("Right images path:", self.right_dir)
        print("Left images path:", self.left_dir)

        os.makedirs(self.right_dir, exist_ok=True)
        os.makedirs(self.left_dir, exist_ok=True)

        with open(self.imu_session_file, 'w') as imu_file:
            pass
        with open(self.range_finder_session_file, 'w') as range_file:
            pass
        with open(self.instructions_session_file, 'w') as instructions_file:
            pass

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
    
    def package_session(self, session_id):
        session = next((s for s in self.sessions if s['session_id'] == session_id), None)
        if not session:
            return {"error": "Session not found"}

        right_images = self.read_all_images_to_np(self.right_dir)
        left_images = self.read_all_images_to_np(self.left_dir)

        session_package_dir = os.path.join(self.DIR_PATH, 'SessionPackages', str(session_id))
        os.makedirs(session_package_dir, exist_ok=True)

        right_images_packaged_file = os.path.join(session_package_dir, f"{session_id}_right_images.npy")
        left_images_packaged_file = os.path.join(session_package_dir, f"{session_id}_left_images.npy")

        imu_packaged_file = os.path.join(session_package_dir, f"{session_id}_imu_data.jsonl")
        range_finder_packaged_file = os.path.join(session_package_dir, f"{session_id}_range_finder_data.jsonl")
        instructions_packaged_file = os.path.join(session_package_dir, f"{session_id}_instructions.txt")

        np.save(right_images_packaged_file, right_images)
        np.save(left_images_packaged_file, left_images)

        shutil.copy2(self.imu_session_file, imu_packaged_file)
        shutil.copy2(self.range_finder_session_file, range_finder_packaged_file)
        shutil.copy2(self.instructions_session_file, instructions_packaged_file)

        return {
            'session_id': session_id,
            'right_images': right_images_packaged_file,
            'left_images': left_images_packaged_file,
            'imu_data': imu_packaged_file,
            'range_finder_data': range_finder_packaged_file,
            'instructions_data': instructions_packaged_file
        }
    
    def read_all_images_to_np(self, dir_path):
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
                try:
                    # Remove directories
                    shutil.rmtree(os.path.join(self.RIGHT_PATH, "session_" + str(session['session_id'])), ignore_errors=True)
                    shutil.rmtree(os.path.join(self.LEFT_PATH, "session_" + str(session['session_id'])), ignore_errors=True)
                    os.remove(os.path.join(self.IMU_PATH, "session_" + str(session['session_id']) + ".jsonl"))
                    os.remove(os.path.join(self.RANGE_FINDER_PATH, "session_" + str(session['session_id']) + ".jsonl"))
                    os.remove(os.path.join(self.INSTRUCTIONS_PATH, "session_" + str(session['session_id']) + ".jsonl"))
                except FileNotFoundError:
                    print("file does not exist")
        self.sessions = [session for session in self.sessions if session['session_id'] not in sessions_to_delete]
        with open(os.path.join(self.DIR_PATH, 'Sessions', 'session_data.jsonl'), "w") as f:
            for session in self.sessions:
                f.write(json.dumps(session) + "\n")

if __name__ == "__main__":
    sessionsManager = SessionManager(False)
    sessionsManager.delete_session(range(3,34))  # Example usage to delete sessions with IDs 1, 2, and 3
