import time
import threading
import pickle

#from sshkeyboard import listen_keyboard
import keyboard

from PCA9685 import PCA9685
from picamera2 import Picamera2

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

def get_input(): movement_ls.append(input())

def continuous_camera_capture(picam): camera_ls.append(picam.capture_image())

def camera_drive(picam):
    while True:
        input_thread = threading.Thread(target=get_input)
        input_thread.start()

        while len(movement_ls) == 0: continuous_camera_capture(picam)

        input_thread.join()
        movement = movement_ls.pop(0)
        if movement == 'w':
            print('UP')
            PWM.setMotorModel(1000, 1000, 1000, 1000)
        elif movement == 's': 
            print('DOWN')
            PWM.setMotorModel(-1000, -1000, -1000, -1000)
        elif movement == 'a': 
            print('LEFT')
            PWM.setMotorModel(250, 250, 2000, 2000)
        elif movement == 'd': 
            print('RIGHT')
            PWM.setMotorModel(2000, 2000, 250, 250)

#def infinity_drive(key):
def infinity_drive():
    #print(f"{key} pressed")
    #if key == "up":
    while True:
        if keyboard.is_pressed('up'):
            print('UP')
            PWM.setMotorModel(1000, 1000, 1000, 1000)
        #elif key == "down":
        elif keyboard.is_pressed('down'):
            print('DOWN')
            PWM.setMotorModel(-1000, -1000, -1000, -1000)
        #elif key == "left":
        elif keyboard.is_pressed('left'):
            print('LEFT')
            PWM.setMotorModel(250, 250, 2000, 2000)
        #elif key == "right":
        elif keyboard.is_pressed('right'):
            print('RIGHT')
            PWM.setMotorModel(2000, 2000, 250, 250)
        #else:
            #PWM.setMotorModel(0, 0, 0, 0)

if __name__=='__main__':
    PWM = Motor()          
    PWM.setMotorModel(0, 0, 0, 0)
    try:
        #listen_keyboard(infinity_drive)
        movement_ls, camera_ls = [], []
        picam = Picamera2()
        camera_config = picam.create_still_configuration(main={"size": (640,480)}, lores={"size": (640, 480)}, display="lores")
        picam.configure(camera_config)
        picam.start()
        time.sleep(2)

        #infinity_drive()
        camera_drive(picam)
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        PWM.setMotorModel(0, 0, 0, 0)
        #pickle.dump(camera_ls, open('pillow_images_ls.pkl', 'wb'))
