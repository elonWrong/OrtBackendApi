import cv2
import numpy as np

# Load images
img2 = cv2.imread('TestCode\\CalibrationImages\\left.jpg')  # Base image
img1 = cv2.imread('TestCode\\CalibrationImages\\right.jpg')  # Image to overlay

if img1 is None or img2 is None:
    raise FileNotFoundError("Make sure both 'image1.jpg' and 'image2.jpg' exist in the same folder")

# Resize img2 to match img1 size if needed
img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))



# Trackbar callback function (does nothing but required by createTrackbar)
def nothing(x):
    pass

# Create window and trackbars
cv2.namedWindow('Overlay')
cv2.createTrackbar('X Offset', 'Overlay', 0, img1.shape[1], nothing)
cv2.createTrackbar('Y Offset', 'Overlay', 0, img1.shape[0], nothing)

while True:
    x_offset = cv2.getTrackbarPos('X Offset', 'Overlay')
    y_offset = cv2.getTrackbarPos('Y Offset', 'Overlay')

    # Create blank canvas
    overlay = img1.copy()

    # Define region of interest on base image
    x_end = min(img1.shape[1], img2.shape[1] + x_offset)
    y_end = min(img1.shape[0], img2.shape[0] + y_offset)
    x_start = min(img1.shape[1], max(0, x_offset))
    y_start = min(img1.shape[0], max(0, y_offset))

    # Define overlay area on img2
    x1 = max(0, -x_offset)
    y1 = max(0, -y_offset)
    x2 = x1 + (x_end - x_start)
    y2 = y1 + (y_end - y_start)

    if x_end > x_start and y_end > y_start:
        roi = overlay[y_start:y_end, x_start:x_end]
        img2_crop = img2[y1:y2, x1:x2]

        blended = cv2.addWeighted(roi, 0.5, img2_crop, 0.5, 0)
        overlay[y_start:y_end, x_start:x_end] = blended

    cv2.imshow('Overlay', overlay)

    key = cv2.waitKey(1)
    if key == 27:  # ESC to exit
        break

cv2.destroyAllWindows()
