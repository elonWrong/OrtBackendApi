import cv2
import numpy as np

# Load images
img2 = cv2.imread('utilityPrograms\\CameraCalibration\\CalImLeft10.jpg')  # Base image
img1 = cv2.imread('utilityPrograms\\CameraCalibration\\CalImRight10.jpg')  # Image to overlay

h, w = img1.shape[:2]

calib = np.load('stereo_params.npz')
K1, dist1 = calib['K1'], calib['dist1']
K2, dist2 = calib['K2'], calib['dist2']
R1, R2 = calib['R1'], calib['R2']
P1, P2 = calib['P1'], calib['P2']
Q = calib['Q']

# Compute rectification maps
map1L, map2L = cv2.initUndistortRectifyMap(K1, dist1, R1, P1, (w, h), cv2.CV_16SC2)
map1R, map2R = cv2.initUndistortRectifyMap(K2, dist2, R2, P2, (w, h), cv2.CV_16SC2)

# Apply remap (rectify images)
rectifiedL = cv2.remap(img2, map1L, map2L, cv2.INTER_LINEAR)
rectifiedR = cv2.remap(img1, map1R, map2R, cv2.INTER_LINEAR)


#cv2.imshow('Rectified Left', rectifiedL)
#cv2.imshow('Rectified Right', rectifiedR)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

if img1 is None or img2 is None:
    raise FileNotFoundError("Make sure both 'image1.jpg' and 'image2.jpg' exist in the same folder")

# Resize img2 to match img1 size if needed
rectifiedL = cv2.resize(rectifiedL, (rectifiedR.shape[1], rectifiedR.shape[0]))



# Trackbar callback function (does nothing but required by createTrackbar)
def nothing(x):
    pass

# Create window and trackbars
cv2.namedWindow('Overlay')
cv2.createTrackbar('X Offset', 'Overlay', 0, rectifiedL.shape[1], nothing)
cv2.createTrackbar('Y Offset', 'Overlay', 0, rectifiedL.shape[0], nothing)

while True:
    x_offset = cv2.getTrackbarPos('X Offset', 'Overlay')
    y_offset = cv2.getTrackbarPos('Y Offset', 'Overlay')

    # Create blank canvas
    overlay = rectifiedR.copy()

    # Define region of interest on base image
    x_end = min(rectifiedR.shape[1], rectifiedL.shape[1] + x_offset)
    y_end = min(rectifiedR.shape[0], rectifiedL.shape[0] + y_offset)
    x_start = min(rectifiedR.shape[1], max(0, x_offset))
    y_start = min(rectifiedR.shape[0], max(0, y_offset))

    # Define overlay area on img2
    x1 = max(0, -x_offset)
    y1 = max(0, -y_offset)
    x2 = x1 + (x_end - x_start)
    y2 = y1 + (y_end - y_start)

    if x_end > x_start and y_end > y_start:
        roi = overlay[y_start:y_end, x_start:x_end]
        img2_crop = rectifiedL[y1:y2, x1:x2]

        blended = cv2.addWeighted(roi, 0.5, img2_crop, 0.5, 0)
        overlay[y_start:y_end, x_start:x_end] = blended

    cv2.imshow('Overlay', overlay)

    key = cv2.waitKey(1)
    if key == 27:  # ESC to exit
        break

cv2.destroyAllWindows()
