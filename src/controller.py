from motor_controller import MotorController
from imu import IMU
import time

from data_fuser import SensorFuser

class Controller:
	
	def __init__(self, sensor_manager):
		self.motors = MotorController()
		self.sensor_manager = sensor_manager
		self.imu = self.sensor_manager.imu
		self.session_manager = self.sensor_manager.session_manager
		self.session_log_file = self.session_manager.instructions_session_file
		self.currentOrientation = self.imu.current_orientation

	def granular(self, instruction):
		self.log_instruction(instruction)
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
		self.currentOrientation = self.imu.current_orientation
		print(f"Current Orientation: {self.currentOrientation}")
		bearing = self.currentOrientation[0]
		startingBearing = bearing
		desiredBearing = (bearing + degrees) % 360
		print(f"Current Bearing: {bearing}, Desired Bearing: {desiredBearing}")
		while True:
			self.currentOrientation = self.imu.current_orientation
			bearing = self.currentOrientation[0]
			print(f"Current Bearing: {bearing}")
			if (bearing - startingBearing) % 360 >= (desiredBearing - startingBearing) % 360:
				break
			self.motors.lf_activate(1)
			self.motors.rf_activate(-1)
			self.motors.lr_activate(1)
			self.motors.rr_activate(-1)
			time.sleep(0.01)
		self.motors.all_off()

		self.currentOrientation = self.imu.current_orientation
		print(f"Final Bearing: {self.currentOrientation[0]}")

	def turnCounterClockwise(self, degrees):
		self.currentOrientation = self.imu.current_orientation
		bearing = self.currentOrientation[0]
		startingBearing = bearing
		desiredBearing = (bearing - degrees) % 360
		if desiredBearing < 0:
			desiredBearing += 360
		print(f"Current Bearing: {bearing}, Desired Bearing: {desiredBearing}")
		while True:
			self.currentOrientation = self.imu.current_orientation
			bearing = self.currentOrientation[0]
			print(f"Current Bearing: {bearing}")
			# if abs(bearing - desiredBearing) < 1:
			# 	break
			if (startingBearing - bearing) % 360 >= (startingBearing - desiredBearing) % 360:
				break
			self.motors.lf_activate(-1)
			self.motors.rf_activate(1)
			self.motors.lr_activate(-1)
			self.motors.rr_activate(1)
			time.sleep(0.01)
		self.motors.all_off()

		self.currentOrientation = self.imu.current_orientation
		print(f"Final Bearing: {self.currentOrientation[0]}")

	def faceDirection(self, direction):
		self.currentOrientation = self.imu.current_orientation
		bearing = self.currentOrientation[0]
		desiredBearing = direction
		print(f"Current Bearing: {bearing}, Desired Bearing: {desiredBearing}")
		while True:
			self.currentOrientation = self.imu.current_orientation
			bearing = self.currentOrientation[0]
			print(f"Current Bearing: {bearing}")
			if abs(bearing - desiredBearing) < 1:
				break
			if bearing < desiredBearing:
				self.motors.lf_activate(1)
				self.motors.rf_activate(-1)
				self.motors.lr_activate(1)
				self.motors.rr_activate(-1)
			else:
				self.motors.lf_activate(-1)
				self.motors.rf_activate(1)
				self.motors.lr_activate(-1)
				self.motors.rr_activate(1)
			time.sleep(0.1)
		self.motors.all_off()

		self.currentOrientation = self.imu.current_orientation
		print(f"Final Bearing: {self.currentOrientation[0]}")

	def log_instruction(self, instruction):
		instruction['timestamp'] = time.time()
		with open(self.session_log_file, 'a') as file:
			file.write(f"{instruction}\n")

	def imuGenerateStream(self):
		return self.imu.generateStream()
	

if __name__ == "__main__":
	sensor_fuser = SensorFuser(session_label="Test Session")
	controller = Controller(sensor_manager=sensor_fuser)  # Replace with actual sensor manager instance
	controller.moveBackward(speed=-0.5, duration=2)

		
		
	
