import json
import smbus2
import time
import threading
import numpy as np

from scipy.spatial.transform import Rotation as R

class IMU:
	I2C_ADDRESS = 0x60

	# CMPS12 Registers
	BEARING_REGISTER = 2 
	PITCH_REGISTER = 4
	ROLL_REGISTER = 5
	ACCEL_X_REGISTER = 0x0C
	ACCEL_Y_REGISTER = 0x0E
	ACCEL_Z_REGISTER = 0x10
	GYRO_X_REGISTER = 0x12
	GYRO_Y_REGISTER = 0x14
	GYRO_Z_REGISTER = 0x16

	SAMPLE_RATE = 0.05  # 50 ms sample rate
	GRAVITY =  np.array([0, 0, 0.981])  # g, used for gravity correction
	

	def __init__(self, use_trapezoidal=True):
		self.bias = np.array([0.90905092, 0.42618937, -1.10863928])
		# self.bias = np.zeros(3)
		self.velocity = np.zeros(3)
		self.displacement = np.zeros(3)
		self.prev_velocity = np.zeros(3)
		self.current_orientation = np.zeros(3)
		self.current_acceleration = np.zeros(3)
		self.current_acceleration_adjusted = np.zeros(3)
		self.current_gyro = np.zeros(3)
		self.prev_time = None
		self.use_trapezoidal = use_trapezoidal
		self.bus = smbus2.SMBus(1)


	def calc_bias(self, num_samples=100):
		print("Calculating bias for acceleration...")
		accel_sum = np.zeros(3)
		self.bias = np.zeros(3)
		while np.array_equal(self.current_acceleration_adjusted, np.zeros(3)):
			print("Waiting for first valid acceleration reading...")
			time.sleep(self.SAMPLE_RATE)
		for index in range(num_samples):
			accel_sum += self.current_acceleration_adjusted
			time.sleep(self.SAMPLE_RATE)
			print(f"Collected {index + 1} samples for bias calculation.", end='\r')

		bias = accel_sum / num_samples
		print("Calculated bias:", bias)
		return bias


	def start_track_thread(self):
		self.thread = threading.Thread(target=self.track_location)
		self.thread.daemon = True
		self.thread.start()

	def stop_track_thread(self):
		if self.thread.is_alive():
			self.thread.join(timeout=1)
			if self.thread.is_alive():
				print("Thread did not stop gracefully, forcing exit.")
				self.thread._stop()

	def track_location(self):
		while True:
			self.get_measurements()
			self.update(self.current_acceleration, self.current_orientation)
			time.sleep(self.SAMPLE_RATE)

	def get_frame(self):
		return {
			"orientation": self.current_orientation.tolist(),
			"acceleration": self.current_acceleration_adjusted.tolist(),
			"gyro": self.current_gyro.tolist(),	
			"speed": self.velocity.tolist(),
			"displacement": self.displacement.tolist(),
			"timeStamp": time.time()
		}


	def i2cRead(self, registerAddress, numBytes=1):
		return self.bus.read_i2c_block_data(self.I2C_ADDRESS, registerAddress, numBytes)

	def get_measurements(self):
		self.get_orientation()
		self.get_acc()
		self.get_gyro()


	def get_orientation(self):
		try:
            # Read 4 bytes: bearing (2), pitch (1), roll (1)
			receivedBytes = self.i2cRead(self.BEARING_REGISTER, 4)
		except Exception as e:
			print("I2C read error:", e)
			return None

        # Calculate bearing 
		bearing = ((receivedBytes[0] << 8) + receivedBytes[1]) / 10.		
		pitch = receivedBytes[2]
		if pitch > 127:
			pitch -= 25		
		roll = receivedBytes[3]
		if roll > 127:
			roll -= 256

		orientation = np.array([bearing, pitch, roll])
		self.current_orientation = orientation
		return orientation
	def get_gyro(self):
		try:
			# Read 6 bytes: Gyro X (2), Y (2), Z (2)
			gyro_x_bytes = self.i2cRead(self.GYRO_X_REGISTER, 2)
			gyro_y_bytes = self.i2cRead(self.GYRO_Y_REGISTER, 2)	
			gyro_z_bytes = self.i2cRead(self.GYRO_Z_REGISTER, 2)
			gyro_x = self.__to_signed16(gyro_x_bytes[0], gyro_x_bytes[1])
			gyro_y = self.__to_signed16(gyro_y_bytes[0], gyro_y_bytes[1])
			gyro_z = self.__to_signed16(gyro_z_bytes[0], gyro_z_bytes[1])

			gyro = np.array([gyro_x, gyro_y, gyro_z]) / 1000.0  # Convert to rad/s
			self.current_gyro = gyro
			return gyro
		except Exception as e:
			print("I2C read error (gyroscope):", e)
			return None
	def get_acc(self):
		try:
			# Read 6 bytes: Accel X (2), Y (2), Z (2)
			acc_x_bytes = self.i2cRead(self.ACCEL_X_REGISTER, 2)
			acc_y_bytes = self.i2cRead(self.ACCEL_Y_REGISTER, 2)	
			acc_z_bytes = self.i2cRead(self.ACCEL_Z_REGISTER, 2)
			acc_x = self.__to_signed16(acc_x_bytes[0], acc_x_bytes[1])
			acc_y = self.__to_signed16(acc_y_bytes[0], acc_y_bytes[1])
			acc_z = self.__to_signed16(acc_z_bytes[0], acc_z_bytes[1])
			acc = np.array([acc_x, acc_y, acc_z]) / 1000.0  # Convert to g's
			self.current_acceleration = acc
			return acc
		except Exception as e:
			print("I2C read error (acceleration):", e)
			return None

	def update(self, accel_body, euler_angles_deg):
		curr_time = time.time()
		if self.prev_time is None:
			self.prev_time = curr_time
			return self.displacement

		dt = curr_time - self.prev_time
		self.prev_time = curr_time	
    	
		rot = R.from_euler('zyx', euler_angles_deg, degrees=True)	
		
		gravity_body = rot.inv().apply(self.GRAVITY)	

		accel_corrected = np.array(accel_body) - gravity_body - self.bias
		self.current_acceleration_adjusted = accel_corrected
		
		velocity = self.velocity + accel_corrected * dt	
		
		if self.use_trapezoidal:
			avg_velocity = 0.5 * (self.velocity + velocity)
			self.displacement += avg_velocity * dt
		else:
			self.displacement += velocity * dt

		self.prev_velocity = self.velocity
		self.velocity = velocity

	def __to_signed16(self, high, low):
		value = (high << 8) | low
		return value - 65536 if value >= 32768 else value
	

if __name__ == "__main__":
	imu = IMU()
	imu.start_track_thread()
	imu.calc_bias()
	# imu.calc_bias(num_samples=1000)
#
	try:
		while True:
			print("Current IMU Reading:", imu.get_frame()['orientation'], end='\r')
			time.sleep(1)
	except KeyboardInterrupt:
		print("IMU tracking stopped.")

