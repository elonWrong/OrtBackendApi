from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import cv2

app = FastAPI()

# Open the webcam (use 0 for the default camera, or provide a video file path)
video_source = 0  # Change to a file path for a saved video
cap_default = cv2.VideoCapture(video_source)


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

def generate_frames(cap=cap_default):
    while True:
        success, frame = cap.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
stream_reaponse = StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/video_feed")
def video_feed():
    return stream_reaponse

## add video feeds for multiple cameras
@app.get("/video_feed/{camera_id}")
def video_feed(camera_id: int):
    cap = cv2.VideoCapture(camera_id)
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")