from gpiozero import PhaseEnableMotor
import time
from motorController import MotorController

# Motor Test suite

if __name__ == "__main__":
    motorControl = MotorController()
    
    print("test start")
    motorControl.lf_activate(1) ## forward 20%
    time.sleep(4)
    motorControl.all_off()
    motorControl.rf_activate(1) ## Backward 70%
    time.sleep(4)
    motorControl.all_off()
    motorControl.lr_activate(1) ## forward 30%
    time.sleep(4)
    motorControl.all_off()
    motorControl.rr_activate(1) ## forward 100%
    time.sleep(4)
    motorControl.all_off()
    print("test end")
