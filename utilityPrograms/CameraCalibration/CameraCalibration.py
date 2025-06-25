from camera2 import Camera
import cv2 as cv

imageiterator = 0


grid = (7,7)

cam = Camera(1)



running = True
while (running):
	print("Press a key to take picture, press 1 to exit")
	selection = input()

	if(selection == "1"):
		running = False
		break
	cornersFound = False
	frame = None
	while not cornersFound:
		frame = cam.get_frame()
		gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
		print("what")
		cornersFound, corners = cv.findChessboardCorners(gray, grid, None)	
		if cornersFound:
			visualise = frame.copy()
			cv.drawChessboardCorners(visualise, grid, corners, cornersFound)
			cv.waitKey(3000)
			print("howdy")
		else:
			cv.imshow("visualise", cam.get_frame())
			cv.waitKey(3000)
	
	cv.imwrite("CalIm" + str(imageiterator) + "R.jpg", frame)
	
	imageiterator = imageiterator + 1

