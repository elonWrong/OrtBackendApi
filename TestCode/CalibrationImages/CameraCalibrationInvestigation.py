import numpy as np
import cv2 as cv
from PIL import Image
import os

# Directory containing images
folder = 'TestCode/CalibrationImages/chessboard'

# print names of all files in the directory folder
print("Files in directory:", os.listdir(folder))

# Get all image files (filter by extension)
images = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

# Open all images
 
# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

grid = (8,6)  # Number of inner corners per a chessboard row and column
 
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((grid[0]*grid[1],3), np.float32)
objp[:,:2] = np.mgrid[0:grid[0],0:grid[1]].T.reshape(-1,2)
 
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
 
#images = glob.glob('TestCode\CalibrationImages\cam1Image0*.jpg')
print("Found images:", len(images))
 
for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
 
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, grid, None)
 
    # If found, add object points, image points (after refining them)
    if ret == True:
        print(f"Processing {fname} - Found corners")
        objpoints.append(objp)
 
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)
 
        # Draw and display the corners
        cv.drawChessboardCorners(img, grid, corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(3000)

if not objpoints or not imgpoints:
    print("No chessboard corners were found in any image. Calibration cannot proceed.")
    exit(1)

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# Print results
print("Camera matrix:\n", mtx)
print("Distortion coefficients:\n", dist)
cv.destroyAllWindows()

img = cv.imread(images[4])  # Use the first image for undistortion
h,  w = img.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

# undistort
dst = cv.undistort(img, mtx, dist, None, newcameramtx)
 
# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite('calibresult.png', dst)