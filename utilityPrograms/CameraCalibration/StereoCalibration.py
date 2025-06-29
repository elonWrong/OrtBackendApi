import cv2
import numpy as np
import glob

# ==== PARAMETERS ====
CHECKERBOARD = (9, 6)  # (columns, rows) of internal corners
SQUARE_SIZE = 25       # mm or any consistent unit
IMAGE_DIR = './stereo_images/'  # folder containing left*.jpg and right*.jpg
LEFT_PREFIX = 'left'
RIGHT_PREFIX = 'right'

# ==== PREPARE OBJECT POINTS ====
objp = np.zeros((CHECKERBOARD[1]*CHECKERBOARD[0], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE

objpoints = []  # 3D real-world points
imgpoints_left = []  # 2D points in left image
imgpoints_right = []  # 2D points in right image

# ==== LOAD IMAGE PAIRS ====
left_images = sorted(glob.glob(IMAGE_DIR + LEFT_PREFIX + '*.jpg'))
right_images = sorted(glob.glob(IMAGE_DIR + RIGHT_PREFIX + '*.jpg'))

assert len(left_images) == len(right_images), "Mismatched image pairs"

for left_img_path, right_img_path in zip(left_images, right_images):
    img_left = cv2.imread(left_img_path)
    img_right = cv2.imread(right_img_path)
    gray_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
    gray_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)

    ret_left, corners_left = cv2.findChessboardCorners(gray_left, CHECKERBOARD, None)
    ret_right, corners_right = cv2.findChessboardCorners(gray_right, CHECKERBOARD, None)

    if ret_left and ret_right:
        objpoints.append(objp)
        imgpoints_left.append(cv2.cornerSubPix(gray_left, corners_left, (11,11), (-1,-1),
                                               criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)))
        imgpoints_right.append(cv2.cornerSubPix(gray_right, corners_right, (11,11), (-1,-1),
                                                criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)))
    else:
        print(f"Checkerboard not found in pair: {left_img_path}, {right_img_path}")

img_size = gray_left.shape[::-1]

# ==== CALIBRATE EACH CAMERA ====
ret_l, K1, dist1, _, _ = cv2.calibrateCamera(objpoints, imgpoints_left, img_size, None, None)
ret_r, K2, dist2, _, _ = cv2.calibrateCamera(objpoints, imgpoints_right, img_size, None, None)

# ==== STEREO CALIBRATION ====
flags = cv2.CALIB_FIX_INTRINSIC
criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)

ret, _, _, _, _, R, T, E, F = cv2.stereoCalibrate(
    objpoints, imgpoints_left, imgpoints_right,
    K1, dist1, K2, dist2,
    img_size, criteria=criteria, flags=flags
)

# ==== RECTIFICATION ====
R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(K1, dist1, K2, dist2, img_size, R, T)

# ==== SAVE PARAMETERS ====
np.savez('stereo_params.npz',
         K1=K1, dist1=dist1, K2=K2, dist2=dist2,
         R=R, T=T, R1=R1, R2=R2, P1=P1, P2=P2, Q=Q)

print("Stereo calibration complete. Parameters saved to 'stereo_params.npz'")
