from motorController import MotorController
from imu import IMU
import time

class Controller:
	
	def __init__(self):
		self.motors = MotorController()
		self.imu = IMU()
		self.currentOrientation = self.imu.getOrientation()
		
	def granular(self, instruction):
		self.motors.lf_activate(instruction.front_left/100)
		self.motors.rf_activate(instruction.front_right/100)    
		self.motors.lr_activate(instruction.rear_left/100)
		self.motors.rr_activate(instruction.rear_right/100)
		time.sleep(instruction.duration)
		self.motors.all_off()

	def moveForward(self, speed=0.5, duration=1):
		print(f"Moving forward at speed {speed} for {duration} seconds")
		self.motors.lf_activate(speed)
		self.motors.rf_activate(speed)
		self.motors.lr_activate(speed)
		self.motors.rr_activate(speed)
		time.sleep(duration)
		self.motors.all_off()

	def moveBackward(self, speed=-0.5, duration=1):
		self.motors.lf_activate(speed)
		self.motors.rf_activate(speed)
		self.motors.lr_activate(speed)
		self.motors.rr_activate(speed)
		time.sleep(duration)
		self.motors.all_off()
		
		
	def turnClockwise(self, degrees):
		self.currentOrientation = self.imu.getOrientation()
		print(f"Current Orientation: {self.currentOrientation}")
		bearing = self.currentOrientation["bearing"]
		desiredBearing = (bearing + degrees) % 360
		print(f"Current Bearing: {bearing}, Desired Bearing: {desiredBearing}")
		while True:
			self.currentOrientation = self.imu.getOrientation()
			bearing = self.currentOrientation["bearing"]
			print(f"Current Bearing: {bearing}")
			if abs(bearing - desiredBearing) < 1:
				break
			self.motors.lf_activate(0.5)
			self.motors.rf_activate(-0.5)
			self.motors.lr_activate(0.5)
			self.motors.rr_activate(-0.5)
			time.sleep(0.1)
		self.motors.all_off()
		
		self.currentOrientation = self.imu.getOrientation()
		print(f"Final Bearing: {self.currentOrientation['bearing']}")

	def turnCounterClockwise(self, degrees):
		self.currentOrientation = self.imu.getOrientation()
		bearing = self.currentOrientation["bearing"]
		desiredBearing = (bearing - degrees)
		if desiredBearing < 0:
			desiredBearing += 360
		print(f"Current Bearing: {bearing}, Desired Bearing: {desiredBearing}")
		while True:
			self.currentOrientation = self.imu.getOrientation()
			bearing = self.currentOrientation["bearing"]
			print(f"Current Bearing: {bearing}")
			if abs(bearing - desiredBearing) < 1:
				break
			self.motors.lf_activate(-0.5)
			self.motors.rf_activate(0.5)
			self.motors.lr_activate(-0.5)
			self.motors.rr_activate(0.5)
			time.sleep(0.1)
		self.motors.all_off()
		
		self.currentOrientation = self.imu.getOrientation()
		print(f"Final Bearing: {self.currentOrientation['bearing']}")
	
	def faceDirection(self, direction):
		self.currentOrientation = self.imu.getOrientation()
		bearing = self.currentOrientation["bearing"]
		desiredBearing = direction
		print(f"Current Bearing: {bearing}, Desired Bearing: {desiredBearing}")
		while True:
			self.currentOrientation = self.imu.getOrientation()
			bearing = self.currentOrientation["bearing"]
			print(f"Current Bearing: {bearing}")
			if abs(bearing - desiredBearing) < 1:
				break
			if bearing < desiredBearing:
				self.motors.lf_activate(0.5)
				self.motors.rf_activate(-0.5)
				self.motors.lr_activate(0.5)
				self.motors.rr_activate(-0.5)
			else:
				self.motors.lf_activate(-0.5)
				self.motors.rf_activate(0.5)
				self.motors.lr_activate(-0.5)
				self.motors.rr_activate(0.5)
			time.sleep(0.1)
		self.motors.all_off()
		
		self.currentOrientation = self.imu.getOrientation()
		print(f"Final Bearing: {self.currentOrientation['bearing']}")
		
		
	
