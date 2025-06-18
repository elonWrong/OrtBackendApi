from picamera2 import Picamera2, Preview
import time

imageiterator = 0
str1 = "cam1Image"
str3 = "cam2Image"
str2 = ".jpg"



running = True
while (running):
	print("Press a key to take picture, press 1 to exit")
	selection = input()

	if(selection == "1"):
		running = False
		break

	picam2 = Picamera2(0)
	camera_config = picam2.create_preview_configuration()
	picam2.configure(camera_config)
	picam2.start()
	stringOut = str1 + str(imageiterator) + str2


	picam21 = Picamera2(1)
	camera_config1 = picam21.create_preview_configuration()
	picam21.configure(camera_config1)
	picam21.start()
	stringOut1 = str3 + str(imageiterator) + str2

	picam2.capture_file(stringOut)
	picam21.capture_file(stringOut1)
	
	picam2.close()
	picam21.close()
	
	imageiterator = imageiterator + 1

