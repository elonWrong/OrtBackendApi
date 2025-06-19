import time
import cv2
from picamera2 import Picamera2, Preview

class Camera:
    def __init__(self, camera_id=0):
        try:
            self.camera_id = camera_id
            self.picam2 = Picamera2(camera_id)
            self.picam2.resolution = (320, 240)
            camera_config = self.picam2.create_still_configuration(
                main={
                    "size": (1280, 720),       # Match this across both cameras
                    "format": "RGB888"         # Good for OpenCV
                },
            buffer_count=1
            )
            self.picam2.configure(camera_config)
            self.picam2.set_controls({"AfMode": 1})     # Manual focus mode
            self.picam2.set_controls({"AfTrigger": 0})  # Trigger focus once
            self.picam2.start_preview(Preview.DRM)
            time.sleep(2)  # Allow autofocus to complete
            self.picam2.set_controls({"AfMode": 0})  # Switch back to auto focus mode
            self.picam2.set_controls({
                "AeEnable": False,
                "ExposureTime": 10000,     # in microseconds
                "AnalogueGain": 1.5        # Adjust as needed
            })
            self.picam2.start()
        except ImportError:
            raise ImportError("picamera2 is not installed")

    def get_frame(self):
        return self.picam2.capture_array()  # Capture a frame as a numpy array
    
    def generate_frames(self):
        while True:
            frame = self.get_frame()[:, :, [2, 1, 0]]
            success, buffer = cv2.imencode('.png', frame)
            if not success:
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    def stop(self):
        self.picam2.stop()  # Stop the camera when done