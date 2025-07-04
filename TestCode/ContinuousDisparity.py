import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider


try:
    from camera import Camera
    left_camera = Camera(0)
    right_camera = Camera(1)
    live = True
except ImportError:
    live = False

frame_count = 0
frame_duration = 5  # seconds

calib = np.load('stereo_params.npz')
K1, dist1 = calib['K1'], calib['dist1']
K2, dist2 = calib['K2'], calib['dist2']
R1, R2 = calib['R1'], calib['R2']
P1, P2 = calib['P1'], calib['P2']
Q = calib['Q']
ROI1, ROI2 = calib['ROI1'], calib['ROI2']

x = max(ROI1[0], ROI2[0])
y = max(ROI1[1], ROI2[1])
w = min(ROI1[0] + ROI1[2], ROI2[0] + ROI2[2]) - x
h = min(ROI1[1] + ROI1[3], ROI2[1] + ROI2[3]) - y

w, h = 1280, 720  # Assuming a fixed resolution for the cameras

map1L, map2L = cv.initUndistortRectifyMap(K1, dist1, R1, P1, (w, h), cv.CV_16SC2)
map1R, map2R = cv.initUndistortRectifyMap(K2, dist2, R2, P2, (w, h), cv.CV_16SC2)



num_disparities = 16 * 2  # Must be divisible by 16
block_size = 7  # Must be odd
unique_ratio = 10
speckle_window_size = 100
speckle_range = 16

stereo = cv.StereoSGBM_create(
    numDisparities=num_disparities,
    blockSize=block_size,
    minDisparity=0,
    P1=8 * 3 * block_size ** 2,
    P2=32 * 3 * block_size ** 2,
    disp12MaxDiff=1,
    uniquenessRatio=unique_ratio,
    speckleWindowSize=speckle_window_size,
    speckleRange=speckle_range,
)

fig, ax = plt.subplots(1, 3, figsize=(15, 5))

plt.subplots_adjust(left=0.1, bottom=0.25)
ax[0].set_title('Left Camera')
ax[1].set_title('Right Camera')
ax[2].set_title('Disparity Map')

ax[0].axis('off')
ax[1].axis('off')
ax[2].axis('off')

dur_slider_ax = plt.axes([0.1, 0.01, 0.8, 0.03], facecolor='lightgoldenrodyellow')
dur_slider = Slider(dur_slider_ax, 'Frame Duration', 0.01, 10.0, valinit=frame_duration, valstep=0.01)

num_disparities_ax = plt.axes([0.1, 0.05, 0.8, 0.03], facecolor='lightgoldenrodyellow')
num_disparities_slider = Slider(num_disparities_ax, 'Num Disparities', 16, 128, valinit=num_disparities, valstep=16)

block_size_ax = plt.axes([0.1, 0.09, 0.8, 0.03], facecolor='lightgoldenrodyellow')
block_size_slider = Slider(block_size_ax, 'Block Size', 3, 21, valinit=block_size, valstep=2)

left_frame, right_frame = None, None

key_pressed = {'pressed': False}

def on_key(event):
    # When a key is pressed, set the flag True
    print(f"Key pressed: {event.key}")
    key_pressed['pressed'] = True

def recalculate_disparity_map():
    global left_frame, right_frame, stereo, num_disparities, block_size
    if left_frame is not None and right_frame is not None:
        disparity_map = get_disparity_map(left_frame, right_frame)
        update_plot(left_frame, right_frame, disparity_map)

def update_frame_duration(val):
    global frame_duration
    frame_duration = val

def update_num_disparities(val):
    global num_disparities, stereo
    num_disparities = int(val)
    stereo.setNumDisparities(num_disparities)
    recalculate_disparity_map()

def update_block_size(val):
    global block_size, stereo
    block_size = int(val)
    if block_size % 2 == 0:  # Ensure block size is odd
        block_size += 1
    stereo.setBlockSize(block_size)
    recalculate_disparity_map()
    
dur_slider.on_changed(update_frame_duration)
num_disparities_slider.on_changed(update_num_disparities)
block_size_slider.on_changed(update_block_size)

def rectify_images(left_frame, right_frame):
    rectifiedL = cv.remap(left_frame, map1L, map2L, cv.INTER_CUBIC)
    rectifiedR = cv.remap(right_frame, map1R, map2R, cv.INTER_CUBIC)
    rectifiedL = rectifiedL[y:y+h, x:x+w]  # Crop to ROI
    rectifiedR = rectifiedR[y:y+h, x:x+w]  # Crop
    # Resize rectified images to match the original size
    return rectifiedL, rectifiedR

def get_frames():
    global frame_count
    global left_frame, right_frame
    frame_count += 1
    if not live:
        raise RuntimeError("Cameras are not available in this environment.")
    left_frame = left_camera.get_frame()
    right_frame = right_camera.get_frame()

    rectifiedL, rectifiedR = rectify_images(left_frame, right_frame)

    if left_frame is None or right_frame is None:
        raise ValueError("Failed to capture frames from cameras.")
    cv.imwrite(f"TestCode\\DepthImages\\left{frame_count}.jpg", left_frame)
    cv.imwrite(f"TestCode\\DepthImages\\right{frame_count}.jpg", right_frame)

    return rectifiedL, rectifiedR

def get_frame_placeholder(index = 0):
    global left_frame, right_frame
    #path = "TestCode\\testImages\\"
    path = "utilityPrograms\\CameraCalibration\\CalIm"
    left = cv.imread(f"{path}Left{index}.jpg")
    right = cv.imread(f"{path}Right{index}.jpg")
    if left is None or right is None:
        raise FileNotFoundError(f"Images for index {index} not found.")
    left, right = rectify_images(left, right)
    return left, right

def update_plot(left_frame, right_frame, disparity_map):

    left_epipolar = draw_epipolar_lines(left_frame.copy())
    right_epipolar = draw_epipolar_lines(right_frame.copy())
    ax[0].imshow(left_epipolar)
    ax[1].imshow(right_epipolar)
    ax[2].imshow(disparity_map, cmap='cool')
    plt.draw()

def get_disparity_map(left_frame, right_frame):
    # Convert images to grayscale
    left_gray = cv.cvtColor(left_frame, cv.COLOR_BGR2GRAY)
    right_gray = cv.cvtColor(right_frame, cv.COLOR_BGR2GRAY)
    left_gray = cv.equalizeHist(left_gray)  # Optional: Enhance contrast
    right_gray = cv.equalizeHist(right_gray)  # Optional: Enhance contrast
    # Compute disparity map
    disparity_map = stereo.compute(left_gray, right_gray).astype(np.float32) / num_disparities 
    #disparity_map = cv.normalize(disparity_map, disparity_map, alpha=0, beta=255, norm_type=cv.NORM_MINMAX)
    disparity_map = interpolate_disparity_map(disparity_map)
    return disparity_map


def interpolate_disparity_map(disparity_map):
    # Interpolate the disparity map to fill in missing values
    mask = disparity_map <= 0
    mask = mask.astype(np.uint8)  # Convert mask to uint8 for inpainting
    inpainted = cv.inpaint(disparity_map, mask, inpaintRadius=3, flags=cv.INPAINT_NS)
    return inpainted

def draw_epipolar_lines(img, num_lines=20, color=(0, 255, 0)):
    h, w = img.shape[:2]
    step = h // num_lines
    for i in range(0, h, step):
        cv.line(img, (0, i), (w, i), color, 1)
    return img

def main():
    global left_frame, right_frame
    index = 0
    while True:
        try:
            if not live:
                left_frame, right_frame = get_frame_placeholder(index)
            else:
                # Get frames from the cameras
                left_frame, right_frame = get_frames()
        except Exception as e:
            print(f"Error getting frames: {e}")
            break
        
        # Get the disparity map
        disparity_map = get_disparity_map(left_frame, right_frame)
        # Display the images and disparity map

        left_epipolar = draw_epipolar_lines(left_frame.copy())
        right_epipolar = draw_epipolar_lines(right_frame.copy())

        ax[0].imshow(left_epipolar)
        ax[1].imshow(right_epipolar)
        ax[2].imshow(disparity_map, cmap='cool')

        
        plt.draw()
        key_pressed['pressed'] = False
        
        # Wait here until a key is pressed
        while not key_pressed['pressed']:
            plt.pause(0.1) 
        #plt.pause(frame_duration)
        # Display the plot
        plt.tight_layout()
        

        index += 1
fig.canvas.mpl_connect('key_press_event', on_key)
plt.show(block=False)
if __name__ == "__main__":
    main()
    if live:
        left_camera.stop()
        right_camera.stop()  # Stop the cameras when done
