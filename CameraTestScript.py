from picamera2 import Picamera2, Preview

picam2 = Picamera2(0)
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
picam2.start_preview(Preview.DRM)
picam2.start()
picam2.capture_file("testimage1.jpg")
