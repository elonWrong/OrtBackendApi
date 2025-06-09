from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cv2

app = FastAPI()

origins = [
    "http://localhost:3000",  # React app running on localhost:3000
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
video_source = 0  # Change to a file path for a saved video
cap_default = cv2.VideoCapture(video_source)

@app.get("/")
def read_root():
    return {"message": "Hello"}

def generate_frames(cap=cap_default):
    while True:
        success, frame = cap.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

## add video feeds for multiple cameras
@app.get("/video_feed/{camera_id}")
def video_feed(camera_id: int):
    cap = cv2.VideoCapture(camera_id)
    return StreamingResponse(generate_frames(cap), media_type="multipart/x-mixed-replace; boundary=frame")

## add endpoints for the controls
# Motor specific controls

@app.post("/standard")
async def standard_movement(instruction: StandardInstruction):
    print(f"Received instruction: {instruction.instruction}, value: {instruction.value}")
    if instruction.instruction == "forward":
        print("Moving forward by", instruction.value, "units")
    elif instruction.instruction == "backward":
        print("Moving backward by", instruction.value, "units")
    elif instruction.instruction == "left":
        print("Turning left by", instruction.value, "degrees")
    elif instruction.instruction == "right":
        print("Turning right by", instruction.value, "degrees")
    elif instruction.instruction == "face":
        print("Turning to face direction:", instruction.value)
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
    return {"message": "Granular movement activated."}