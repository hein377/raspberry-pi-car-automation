sys.path.inser(0, "....")
from motor import Motor
from picamera2 import Picamera2
import pygame
pygame.init()

import math
import numpy as np
import time
import threading

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

    print(f"r = {r}     theta = {theta}")

    motor_x_pwm, motor_y_pwm = find_motor_pwm_vals(r, theta, piecewise_boundaries)
    print(motor_x_pwm, motor_y_pwm)
    return (motor_x_pwm, motor_x_pwm, motor_y_pwm, motor_y_pwm)

def controller_drive(controller, piecewise_boundaries):
    while True:
        pygame.event.get()
        motor_pwm_vals = directionalVector_to_pwmValues(controller.get_axis(0), -controller.get_axis(1), controller.get_axis(2), piecewise_boundaries)
        PWM.setMotorModel(motor_pwm_vals[0], motor_pwm_vals[1], motor_pwm_vals[2], motor_pwm_vals[3])


# Configuration
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
 
def main():
    # Global Variables
    global IMG_COUNT
    IMG_COUNT = 0
    camera_flag = threading.Event()
    camera_flag.set()
    exit_flag = threading.Event()
    img_path = '/home/hein/code_dir/Testing/Multiprocessing_Driving/test_pics'

    PWM = Motor()
    PWM.setMotorModel(0, 0, 0, 0)
    cap = cv2.VideoCapture(0)
    
    pi = math.pi
    piecewise_boundaries = [0, round(pi/4,5), round(pi/2,5), round(3*pi/4,5), round(pi,5)]
    #test_piecewise_boundaries(piecewise_boundaries)
    controller = get_controllers()[0]

    camera_thread = threading.Thread()
    drive_thread = threading.Thread(controller_drive, args=[exit_flag, controller, piecewise_boundaries])

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

if __name__=='__main__':
    main()
