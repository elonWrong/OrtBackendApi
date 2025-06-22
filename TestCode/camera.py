import time
import cv2
from picamera2 import Picamera2, Preview

## CAMERA CLASS HAS 2 SEPERATE FILES, UPDATE BOTH AS NEEDED

SENSOR_RESOLUTION = (4608, 2592)  # Full resolution of the sensor
MAIN_RESOLUTION = (1280, 720)      # Resolution for the main output

EXPOSURE = 30000
ISO = 200
LENS_POSITION = 2.5
AF_MODE = 0  

class Camera:
    def __init__(self, camera_id=0):
        try:
            self.camera_id = camera_id
            self.picam2 = Picamera2(camera_id)
            camera_config = self.picam2.create_still_configuration(
                sensor={"output_size": SENSOR_RESOLUTION},
                main={"size": MAIN_RESOLUTION},
                buffer_count = 1
            )
            self.picam2.configure(camera_config)
            # self.picam2.start_preview(Preview.DRM)
            self.picam2.set_controls({
                "ExposureTime": EXPOSURE,
                "AnalogueGain": ISO / 100,
                "LensPosition": LENS_POSITION,
                "AfMode": AF_MODE
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