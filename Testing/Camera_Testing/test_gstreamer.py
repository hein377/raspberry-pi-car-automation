from time import sleep
from threading import Thread

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib
Gst.init()

main_loop = GLib.MainLoop()
main_loop_thread = Thread(target=main_loop.run)
main_loop_thread.start()

pipeline = Gst.parse_launch('v4l2src device=/dev/video0 io-mode=2 ! decodebin ! videoconvert ! autovideosink')
#pipeline = Gst.parse_launch('v4l2src device=/dev/video0 io-mode=2 ! video/x-h264, width=640, height=480 ! h264parse ! queue ! rtph264pay config-interval=1 pt=96 ! gdppay ! autovideosink') 

pipeline.set_state(Gst.State.PLAYING)

try:
    while True: sleep(0.1)
except KeyboardInterrupt:
    pass

pipeline.set_state(Gst.State.NULL)
main_loop.quit()
main_loop_thread.join()
