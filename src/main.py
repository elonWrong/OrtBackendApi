from time import time
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from starlette.responses import StreamingResponse as StarletteStreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from controller import Controller
from camera import Camera
from data_fuser import SensorFuser
from session_manager import SessionManager
from typing import Optional
import cv2
import io
import zipfile


app = FastAPI()
sensor_fuser = SensorFuser()
controller = Controller(sensor_fuser)
cams = sensor_fuser.left_camera, sensor_fuser.right_camera
session_manager = sensor_fuser.session_manager
sensor_fuser.run()

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

#@app.get("/video_feed")
#def video_feed():
#    def generate_frames():
#         while True:
#                success, frame = cap.read()
#                if not success:
#                    break
#                _, buffer = cv2.imencode('.jpg', frame)
#                yield (b'--frame\r\n'
#                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
#    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

## add video feeds for multiple cameras
@app.get("/video_feed/{camera_id}")
def video_feed(camera_id: int):
    cams = sensor_fuser.left_camera, sensor_fuser.right_camera
    if camera_id < len(cams):
        return StreamingResponse(cams[camera_id].generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
    return {"error": "Camera not found"}

###### THIS NEEDS TO BE REFACTORED ######
@app.get("/imu")
def get_imu_data():
    return StreamingResponse(controller.imuGenerateStream(), media_type="application/x-ndjson")

@app.get("/sensor_fusion")
def get_sensor_fusion_data():
    return sensor_fuser.current_fused_data 

@app.get("/sessions/")
def get_session_data(session_id: Optional[int] = None):
    if session_id is not None:
        session = session_manager.package_session(session_id)
        if "error" in session:
            return session
        zip_buffer = create_zip_file(session)
        return StreamingResponse(zip_buffer, media_type="application/zip", headers={
            "Content-Disposition": f"attachment; filename=session_{session_id}.zip"
        })
    return session_manager.sessions

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

def create_zip_file(session: dict):
    session_id = session['session_id']

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(session['right_images'], arcname=f"{session_id}_right_images.npy")
        zip_file.write(session['left_images'], arcname=f"{session_id}_left_images.npy")
        zip_file.write(session['imu_data'], arcname=f"{session_id}_imu_data.jsonl")
        zip_file.write(session['range_finder_data'], arcname=f"{session_id}_range_finder_data.jsonl")
        zip_file.write(session['instructions_data'], arcname=f"{session_id}_instructions.txt")

    zip_buffer.seek(0)
    return zip_buffer

def sensor_fusion_stream():
    while True:
        data = sensor_fuser.get_fused_data()
        if data:
            yield f"{data}\n"
        time.sleep(0.1)

def get_sensor_stream(sensor_name: str):
    while True:
        data = sensor_fuser.current_fused_data.get(sensor_name)
        if not data:
            break
        if sensor_name == 'left_camera' or sensor_name == 'right_camera':
            _, buffer = cv2.imencode('.jpg', data)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            