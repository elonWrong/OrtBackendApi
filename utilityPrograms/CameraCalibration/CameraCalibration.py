from camera2 import Camera
import cv2 as cv

imageiterator = 14


grid = (7,7)

cam = Camera(0)
rightCam = Camera(1)



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
		rightFrame = rightCam.get_frame()
		gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
		rightGray = cv.cvtColor(rightFrame, cv.COLOR_BGR2GRAY)
		print("what")
		cornersFound, corners = cv.findChessboardCorners(gray, grid, None)	

		if cornersFound:
			visualise = frame.copy()
			cv.drawChessboardCorners(visualise, grid, corners, cornersFound)
			cv.waitKey(3000)
			print("howdy")		
			cornersFoundRight, cornersRight = cv.findChessboardCorners(rightGray, grid, None)
			if cornersFoundRight:
				visualiseRight = rightFrame.copy()
				cv.drawChessboardCorners(visualiseRight, grid, cornersRight, cornersFoundRight)
				cv.imshow("visualiseRight", visualiseRight)
				cv.waitKey(3000)
		else:
			cv.imshow("visualise", cam.get_frame())
			cv.waitKey(3000)

	cv.imwrite("CalImLeft" + str(imageiterator) + ".jpg", frame)
	cv.imwrite("CalImRight" + str(imageiterator) + ".jpg", rightFrame)
	imageiterator = imageiterator + 1

