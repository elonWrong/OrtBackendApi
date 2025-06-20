from picamera2 import Picamera2, Preview
import time

imageiterator = 0
str1 = "cam1Image"
str3 = "cam2Image"
str2 = ".jpg"

EXPOSURE = 30000
ISO = 200

# picam2 = Picamera2(0)
# camera_config = picam2.create_preview_configuration()
# picam2.configure(camera_config)
# picam2.start()


picam2 = Picamera2(0)
picam21 = Picamera2(1)

camera_config = picam2.create_still_configuration(
	sensor={"output_size": (4608, 2592)},
	main={"size": (1280, 720)}
)

camera_control = {
	"ExposureTime": EXPOSURE, 
	"AnalogueGain": ISO / 100, 
	"LensPosition": 2.5,
	"AfMode": 0}

picam2.configure(camera_config)
picam21.configure(camera_config)

picam2.set_controls(camera_control)
picam21.set_controls(camera_control)

picam2.start()
picam21.start()

running = True
while (running):
	print("Press a key to take picture, press 1 to exit")
	selection = input()

	if(selection == "1"):
		running = False
		break

	stringOut = str1 + str(imageiterator) + str2
	
	stringOut1 = str3 + str(imageiterator) + str2

	picam2.capture_file(stringOut)
	picam21.capture_file(stringOut1)
	
	
	imageiterator = imageiterator + 1

picam2.close()
picam21.close()
