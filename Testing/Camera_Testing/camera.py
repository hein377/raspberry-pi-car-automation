from picamera2 import Picamera2
import numpy as np
import time
import PIL
import cv2
import pickle

camera = Picamera2()
camera_config = camera.create_still_configuration(main={"size": (640,480), "format": "YUV420"}, lores={"size": (640, 480), "format": "YUV420"}, display="lores")
camera.configure(camera_config)
camera.start()

start = time.perf_counter()
yuv_img = cv2.cvtColor(camera.capture_array(), cv2.COLOR_YUV2GRAY_420)
end = time.perf_counter()
print(end-start)

cv2.imshow('greyscale_img', yuv_img)
cv2.waitKey()

pickle.dump(yuv_img, open('curve2_img.pkl', 'wb'))
