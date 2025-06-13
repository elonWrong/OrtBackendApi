from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from controller import Controller

import cv2
import time
from picamera2 import Picamera2, Preview

app = FastAPI()
controller = Controller()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

class StandardInstruction(BaseModel):
    instruction: str
    value: int

class GranularInstruction(BaseModel):
    front_left: int
    front_right: int
    rear_left: int
    rear_right: int
    duration: float

# Open the webcam (use 0 for the default camera, or provide a video file path)
gst_pipeline = (
	"libcamerasrc ! video/x-raw,width=1280,height=720,framerate=30/1 "
	"! videoconvert ! appsink"
)
video_source = 0  # Change to a file path for a saved video
cap_default = 0


#picam1 = Picamera2(1)
#picam1.resolution = (320,240)
#camera_config = picam1.create_preview_configuration()
#picam1.configure(camera_config)
#picam1.start_preview(Preview.DRM)
#picam1.start()
#
#picam2 = Picamera2(0)
#picam2.resolution = (320,240)
#camera_config = picam2.create_preview_configuration()
#picam2.configure(camera_config)
#picam2.start_preview(Preview.DRM)
#picam2.start()
#
#cams = [picam2, picam1]

@app.get("/")
def read_root():
    return {"message": "testing cors"}

def generate_frames(cap=cap_default):
    while True:
        frameRaw = cams[cap].capture_array()
        frameRaw = frameRaw[:, :, [2,1,0]]
        success, buffer = cv2.imencode('.png', frameRaw)
        if not success:
          print("shit")
          break
        #_, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

## add video feeds for multiple cameras
@app.get("/video_feed/{camera_id}")
def video_feed(camera_id: int):
    return StreamingResponse(generate_frames(camera_id), media_type="multipart/x-mixed-replace; boundary=frame")

## add endpoints for the controls
# Motor specific controls

@app.post("/standard")
async def standard_movement(instruction: StandardInstruction):
    print(f"Received instruction: {instruction.instruction}, value: {instruction.value}")
    if instruction.instruction == "forward":
        print("Moving forward by", instruction.value, "units")
        controller.moveForward(instruction.value/100)
    elif instruction.instruction == "backward":
        print("Moving backward by", instruction.value, "units")
        controller.moveBackward(-instruction.value/100)
    elif instruction.instruction == "left":
        print("Turning left by", instruction.value, "degrees")
        controller.turnCounterClockwise(instruction.value)
    elif instruction.instruction == "right":
        print("Turning right by", instruction.value, "degrees")
        controller.turnClockwise(instruction.value)
    elif instruction.instruction == "face":
        print("Turning to face direction:", instruction.value)
        controller.faceDirection(instruction.value)
    else:
        print("Unknown instruction")       
    return {"message": "Standard movement activated."}


@app.post("/granular")
async def granular_movement(instruction: GranularInstruction):
    print(f"Received granular instruction: {instruction}")
    print("Front Left:", instruction.front_left)
    print("Front Right:", instruction.front_right)
    print("Rear Left:", instruction.rear_left)
    print("Rear Right:", instruction.rear_right)
    print("Duration:", instruction.duration)
    controller.granular(instruction)
    return {"message": "Granular movement activated."}
