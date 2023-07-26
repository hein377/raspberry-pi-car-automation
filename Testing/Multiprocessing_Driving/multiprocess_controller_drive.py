import os
import sys
sys.path.insert(1, "/home/hein/code_dir")

from motor import Motor
from picamera2 import Picamera2
import cv2
import pygame
pygame.init()

import math
import numpy as np
import time
import threading
import pickle

# Picamera2
def video_stream(picam, exit_flag, camera_flag, img_path):
    while not exit_flag.is_set():
        camera_flag.wait()
        print("Sending image to file write", end = "\n\n")
        save_img(cv2.cvtColor(picam.capture_array(), cv2.COLOR_YUV2GRAY_420), camera_flag, img_path)
        time.sleep(0.05)

def save_img(img, camera_flag, img_path):
    global IMG_COUNT, IMG_LS 

    camera_flag.clear()
    print(f"Saving image {IMG_COUNT}_img...", end = "\n\n")
    #cv2.imwrite(os.path.join(img_path, f'{IMG_COUNT}_img.jpg'), img)
    IMG_LS.append(img)
    IMG_COUNT += 1
    camera_flag.set()


# Controller drive
def find_motor_pwm_vals(r, theta, piecewise_boundaries):
    pi = math.pi
    m_x, m_y = 0.25, 4                                  # special case for theta = -pi
    if theta >= piecewise_boundaries[0] and theta <= piecewise_boundaries[1]: m_x, m_y = 4, (1/piecewise_boundaries[4])*theta+0.25
    elif theta > piecewise_boundaries[1] and theta < piecewise_boundaries[2]: m_x, m_y = 4, -3/(piecewise_boundaries[1]**2)*(theta-piecewise_boundaries[2])**2+4 
    elif theta >= piecewise_boundaries[2] and theta < piecewise_boundaries[3]: m_x, m_y = -3/(piecewise_boundaries[1]**2)*(theta-piecewise_boundaries[2])**2+4, 4
    elif theta >= piecewise_boundaries[3] and theta <= piecewise_boundaries[4]: m_x, m_y = (-1/piecewise_boundaries[4])*theta+1.25, 4
    return round(1000*r*m_x), round(1000*r*m_y)

def directionalVector_to_pwmValues(x, y, rotate_val, piecewise_boundaries):
    if abs(rotate_val) > 0.5:
        pwm_val = round(rotate_val*-4000)
        return (-pwm_val, -pwm_val, pwm_val, pwm_val)

    pi = math.pi
    theta = abs(round(math.atan2(y,x),5))
    r = round(math.sqrt(x**2+y**2),3)
    if y < 0: r *= -1

    #print(f"r = {r}     theta = {theta}")

    motor_x_pwm, motor_y_pwm = find_motor_pwm_vals(r, theta, piecewise_boundaries)
    #print(motor_x_pwm, motor_y_pwm)
    return (motor_x_pwm, motor_x_pwm, motor_y_pwm, motor_y_pwm)

def controller_drive(exit_flag, controller, piecewise_boundaries, PWM):
    while not exit_flag.is_set():
        print("Getting joystick input...")
        pygame.event.get()
        motor_pwm_vals = directionalVector_to_pwmValues(controller.get_axis(0), -controller.get_axis(1), controller.get_axis(2), piecewise_boundaries)
        print(f"Setting motor pwm values to: {motor_pwm_vals[0]}, {motor_pwm_vals[1]}, {motor_pwm_vals[2]}, {motor_pwm_vals[3]}")
        PWM.setMotorModel(motor_pwm_vals[0], motor_pwm_vals[1], motor_pwm_vals[2], motor_pwm_vals[3])
        time.sleep(0.01)


# Configuration and Main()
def test_piecewise_boundaries(piecewise_boundaries):
    for val in piecewise_boundaries: print(find_motor_pwm_vals(1, val, piecewise_boundaries))
    print(find_motor_pwm_vals(1, round(pi/4,5)+0.00000001, piecewise_boundaries))
    print(find_motor_pwm_vals(1, round(3*pi/4,5)-0.00000001, piecewise_boundaries))

def get_controllers():
    controllers = []
    for i in range(pygame.joystick.get_count()):
        controllers.append(pygame.joystick.Joystick(i))
        controllers[-1].init()
        print(f"Detected joystick {controllers[-1].get_name()}")
    return controllers

def pickle_images(vid_name):
    global IMG_LS

    print("Saving all images...") 
    pickle.dump(IMG_LS, open(f'test_videos/{vid_name}', 'wb'))
    print("Done saving!")


def main():
    # Global Variables
    global IMG_COUNT, IMG_LS
    IMG_COUNT = 0
    IMG_LS = []
    camera_flag = threading.Event()
    camera_flag.set()
    exit_flag = threading.Event()
    img_path = '/home/hein/code_dir/Testing/Multiprocessing_Driving/test_pics'

    # Set up Motor and PiCamera
    PWM = Motor()
    PWM.setMotorModel(0, 0, 0, 0)
    picam = Picamera2()
    picam.configure(picam.create_still_configuration(main={"size":(640,480), "format":"YUV420"}, lores={"size":(640,480), "format":"YUV420"}, display="lores"))
    picam.start()
   
    # Set up Piecewise Boundaries and Controller
    pi = math.pi
    piecewise_boundaries = [0, round(pi/4,5), round(pi/2,5), round(3*pi/4,5), round(pi,5)]
    #test_piecewise_boundaries(piecewise_boundaries)
    controller = get_controllers()[0]

    # Multiprocessing
    camera_thread = threading.Thread(target=video_stream, args=[picam, exit_flag, camera_flag, img_path])
    drive_thread = threading.Thread(target=controller_drive, args=[exit_flag, controller, piecewise_boundaries, PWM])

    camera_thread.start()
    drive_thread.start()

    try:
        while 1:
            time.sleep(0.1)
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        print("Stopping car...")
        PWM.setMotorModel(0, 0, 0, 0)

        exit_flag.set()
        camera_thread.join()
        drive_thread.join()

        pickle_images("joystick_control_video.pkl")

if __name__=='__main__':
    main()
