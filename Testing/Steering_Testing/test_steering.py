from PCA9685 import PCA9685
from picamera2 import Picamera2

import math
import numpy as np

import pygame
pygame.init()

class Motor:
    def __init__(self):
        self.pwm = PCA9685(0x40, debug=True)
        self.pwm.setPWMFreq(50)
    def duty_range(self,duty1,duty2,duty3,duty4):
        if duty1>4095:
            duty1=4095
        elif duty1<-4095:
            duty1=-4095        
        
        if duty2>4095:
            duty2=4095
        elif duty2<-4095:
            duty2=-4095
            
        if duty3>4095:
            duty3=4095
        elif duty3<-4095:
            duty3=-4095
            
        if duty4>4095:
            duty4=4095
        elif duty4<-4095:
            duty4=-4095
        return duty1,duty2,duty3,duty4
        
    def left_Upper_Wheel(self,duty):
        if duty>0:
            self.pwm.setMotorPwm(0,0)
            self.pwm.setMotorPwm(1,duty)
        elif duty<0:
            self.pwm.setMotorPwm(1,0)
            self.pwm.setMotorPwm(0,abs(duty))
        else:
            self.pwm.setMotorPwm(0,4095)
            self.pwm.setMotorPwm(1,4095)

    def left_Lower_Wheel(self,duty):
        if duty>0:
            self.pwm.setMotorPwm(3,0)
            self.pwm.setMotorPwm(2,duty)
        elif duty<0:
            self.pwm.setMotorPwm(2,0)
            self.pwm.setMotorPwm(3,abs(duty))
        else:
            self.pwm.setMotorPwm(2,4095)
            self.pwm.setMotorPwm(3,4095)
    
    def right_Upper_Wheel(self,duty):
        if duty>0:
            self.pwm.setMotorPwm(6,0)
            self.pwm.setMotorPwm(7,duty)
        elif duty<0:
            self.pwm.setMotorPwm(7,0)
            self.pwm.setMotorPwm(6,abs(duty))
        else:
            self.pwm.setMotorPwm(6,4095)
            self.pwm.setMotorPwm(7,4095)
    
    def right_Lower_Wheel(self,duty):
        if duty>0:
            self.pwm.setMotorPwm(4,0)
            self.pwm.setMotorPwm(5,duty)
        elif duty<0:
            self.pwm.setMotorPwm(5,0)
            self.pwm.setMotorPwm(4,abs(duty))
        else:
            self.pwm.setMotorPwm(4,4095)
            self.pwm.setMotorPwm(5,4095)
            
 
    def setMotorModel(self,duty1,duty2,duty3,duty4):
        duty1,duty2,duty3,duty4=self.duty_range(duty1,duty2,duty3,duty4)
        self.left_Upper_Wheel(duty1)
        self.left_Lower_Wheel(duty2)
        self.right_Upper_Wheel(duty3)
        self.right_Lower_Wheel(duty4)
'''
def find_motor_pwm_vals(r, theta):                  # rE[0,1] and thetaE[-pi,pi]
    m_x, m_y = 0, 0
    pi = math.pi
    if theta >= 0 and theta <= pi:
        varr = -4000*math.cos(2*theta)
        if theta < pi/2: m_x, m_y = 4000, varr
        else: m_x, m_y = varr, 4000
    elif theta < 0 and theta >= -pi:
        varr = 4000*math.cos(2*theta)
        if theta < -pi/2: m_x, m_y = -4000, varr
        else: m_x, m_y = varr, -4000
    return round(r*m_x), round(r*m_y)
'''

def gaussian_func1(x): return round(-8000*np.exp(-(x+pi/2)**2/2)+4000)

def gaussian_func2(x): return round(8000*np.exp(-(x-pi/2)**2/2)-4000)

def find_motor_pwm_vals(r, theta, piecewise_boundaries):
    pi = math.pi
    m_x, m_y = 0, 0
    if theta >= piecewise_boundaries[0] and theta <= piecewise_boundaries[1]: m_x, m_y = -4000, round(4000*math.cos(4*theta))
    elif theta > piecewise_boundaries[1] and theta < piecewise_boundaries[3]:
        if theta < piecewise_boundaries[2]: m_x, m_y = -4000, gaussian_func1(theta) 
        else: m_x, m_y = gaussian_func1(theta), -4000
    elif theta >= piecewise_boundaries[3] and theta < piecewise_boundaries[4]: m_x, m_y = round(4000*math.cos(4*theta)), -4000
    elif theta >= piecewise_boundaries[4] and theta <= piecewise_boundaries[5]: m_x, m_y = 4000, round(-4000*math.cos(4*theta))
    elif theta > piecewise_boundaries[5]  and theta < piecewise_boundaries[7]:
        if theta < piecewise_boundaries[6]: m_x, m_y = 4000, gaussian_func2(theta)
        else: m_x, m_y = gaussian_func2(theta), 4000
    elif theta >= piecewise_boundaries[7]  and theta <= piecewise_boundaries[8]: m_x, m_y = round(-4000*math.cos(4*theta)), 4000
    return round(r*m_x), round(r*m_y)

def directionalVector_to_pwmValues(x, y, piecewise_boundaries):
    pi = math.pi
    theta = round(math.atan2(y,x),5)
    r = round(math.sqrt(x**2+y**2),3)

    print(f"r = {r}     theta = {theta}")

    motor_x_pwm, motor_y_pwm = find_motor_pwm_vals(r, theta, piecewise_boundaries)
    return (motor_x_pwm, motor_x_pwm, motor_y_pwm, motor_y_pwm)

def controller_drive(controller, piecewise_boundaries):
    while True:
        pygame.event.get()
        motor_pwm_vals = directionalVector_to_pwmValues(controller.get_axis(0), -controller.get_axis(1), piecewise_boundaries)
        PWM.setMotorModel(motor_pwm_vals[0], motor_pwm_vals[1], motor_pwm_vals[2], motor_pwm_vals[3])

if __name__=='__main__':
    PWM = Motor()          
    PWM.setMotorModel(0, 0, 0, 0)
    try:
        pi = math.pi
        piecewise_boundaries = [round(-pi,5), round(-7*pi/8,5), round(-pi/2,5), round(-pi/8,5), 0, round(pi/8,5), round(pi/2,5), round(7*pi/8,5), round(pi,5)]
        #xy_ls = [(1,0), (1/2**0.5,1/2**0.5), (0,1), (-1/2**0.5,1/2**0.5), (-1,0), (-1/2**0.5,-1/2**0.5), (0,-1), (1/2**0.5,-1/2**0.5)]

        #xy_ls = [(1,0), (round(math.cos(pi/8),5),round(math.sin(pi/8),5)), (0,1), (round(math.cos(7*pi/8),5),round(math.sin(7*pi/8),5)), (-1,0), (round(math.cos(-7*pi/8),5),round(math.sin(-7*pi/8),5)), (0,-1), (round(math.cos(-pi/8),5),round(math.sin(-pi/8),5))]
        #for x, y in xy_ls: print(directionalVector_to_pwmValues(x, y, piecewise_boundaries))
        #input()

        controllers = []
        for i in range(pygame.joystick.get_count()):
            controllers.append(pygame.joystick.Joystick(i))
            controllers[-1].init()
            print(f"Detected joystick {controllers[-1].get_name()}")
        
        controller = controllers[0]
        controller_drive(controller, piecewise_boundaries)

    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        PWM.setMotorModel(0, 0, 0, 0)
