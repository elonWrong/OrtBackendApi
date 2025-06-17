from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from controller import Controller
from camera import Camera


app = FastAPI()
controller = Controller()
leftCam = Camera(0)
rightCam = Camera(1)
cams = [leftCam, rightCam]

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


@app.get("/")
def read_root():
    return {"message": "testing cors"}


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(leftCam.generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

## add video feeds for multiple cameras
@app.get("/video_feed/{camera_id}")
def video_feed(camera_id: int):
    if camera_id < len(cams):
        return StreamingResponse(cams[camera_id].generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
    return {"error": "Camera not found"}

@app.get("/imu")
def get_imu_data():
    return StreamingResponse(controller.generateStream(), media_type="application/json")

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
