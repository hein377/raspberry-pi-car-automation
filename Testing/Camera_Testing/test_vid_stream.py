from picamera2 import Picamera2
import cv2

cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture(f'v4l2src device=/dev/video0 io-mode=2 ! image/jpeg, width=(int)640, height=(int)480 !  nvjpegdec ! video/x-raw, format=I420 ! autovideosink', cv2.CAP_GSTREAMER)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

output = cv2.VideoWriter('home/hein/autodrive/tutorial/Code/Server/videos',
        cv2.VideoWriter_fourcc(*'XVID'),
        20,
        (width, height))

while True:
    _, frame = cap.read()
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    print(type(imgRGB))
    input()
    output.write(frame)
