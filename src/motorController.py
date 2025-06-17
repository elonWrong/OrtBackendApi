from gpiozero import Motor # Library tested and works with our motors
import time

class MotorController:
    def __init__(self):
		## numbers are pin numbers as corresponding to the pinmap ()
        self.motorLF = Motor(22,23) # Front Left Motor
        self.motorRF = Motor(17,27) # Front Right Motor

        self.motorLR = Motor(5,6) # Rear Left motor
        self.motorRR = Motor(9,11) # Rear right motor
    
    def lf_activate(self, inNo: float):
        print("LF")
        self.__motor_number_decode(inNo, self.motorLF)
        
    def rf_activate(self, inNo: float):
        print("RF")
        self.__motor_number_decode(inNo, self.motorRF)
    
    def lr_activate(self, inNo: float):
        print("LR")
        self.__motor_number_decode(inNo, self.motorLR)
    
    def rr_activate(self, inNo: float):
        print("RR")
        self.__motor_number_decode(inNo, self.motorRR)
        
    def all_off(self):
        print("allOff")
        self.motorLF.stop()
        self.motorRF.stop()
        self.motorLR.stop()
        self.motorRR.stop()
    
    def __motor_number_decode(self, inNo: float, motor):
        if inNo == 0:
            motor.forward(0)
        if inNo > 0:
            motor.forward(inNo)
        if inNo < 0:
            motor.backward(abs(inNo))
