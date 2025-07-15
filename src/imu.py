import json
import smbus2
import time

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

	SAMPLE_RATE = 0.1  # 100 ms sample rate

	def __init__(self):
		self.bus = smbus2.SMBus(1)
		self.previousReading = None
		self.session_readings = []
		self.speed = {
			"x": 0, 
			"y": 0,
			"z": 0
		}
		self.displacement = {
			"x": 0, 
			"y": 0,
			"z": 0
		}

	def resetSpeed(self):
		self.speed = {
			"x": 0, 
			"y": 0,
			"z": 0
		}
	def resetDisplacement(self):
		self.displacement = {
			"x": 0, 
			"y": 0,
			"z": 0
		}

	def generateStream(self):
		while True:
			timeStamp = time.time()
			orientation = self.getOrientation()
			acceleration = self.getAcc()
			self.updateSpeed(acceleration)
			self.updateDisplacement(timeStamp - (self.previousReading["timeStamp"] if self.previousReading else timeStamp))
			if orientation and acceleration:
				data = {
					"orientation": orientation,
					"acceleration": acceleration,
					"timeStamp": timeStamp
				}
				self.previousReading = data
				# print(f"IMU data: {data}".ljust(120), end="\r")
				yield json.dumps(data) + "\n"
			elif orientation is None:
				yield json.dumps({"error": "Failed to read orientation"}) + "\n"
			elif acceleration is None:
				yield json.dumps({"error": "Failed to read acceleration"}) + "\n"
			time.sleep(self.SAMPLE_RATE)

	def get_data(self):
		frame = {
			"orientation": self.getOrientation(),
			"acceleration": self.getAcc(),
			"gyro": self.getGyro(),
			"timeStamp": time.time()
		}
		self.session_readings.append(frame)
		return frame
		
	def get_frame(self):
		self.get_data()

	def i2cRead(self, registerAddress, numBytes=1):
		return self.bus.read_i2c_block_data(self.I2C_ADDRESS, registerAddress, numBytes)
		
	def getOrientation(self):
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

		orientation = {
			"bearing": bearing,
			"pitch": pitch,
			"roll": roll
		}

		return orientation
	def getGyro(self):
		try:
			# Read 6 bytes: Gyro X (2), Y (2), Z (2)
			gyro_x_bytes = self.i2cRead(self.GYRO_X_REGISTER, 2)
			gyro_y_bytes = self.i2cRead(self.GYRO_Y_REGISTER, 2)	
			gyro_z_bytes = self.i2cRead(self.GYRO_Z_REGISTER, 2)
			gyro_x = self.__to_signed16(gyro_x_bytes[0], gyro_x_bytes[1])
			gyro_y = self.__to_signed16(gyro_y_bytes[0], gyro_y_bytes[1])
			gyro_z = self.__to_signed16(gyro_z_bytes[0], gyro_z_bytes[1])

			gyro = {
				"x": gyro_x / 1000.0,  # Convert to degrees/s
				"y": gyro_y / 1000.0,
				"z": gyro_z / 1000.0
			}

			return gyro
		except Exception as e:
			print("I2C read error (gyroscope):", e)
			return None
		
	def getAcc(self):
		try:
			# Read 6 bytes: Accel X (2), Y (2), Z (2)
			acc_x_bytes = self.i2cRead(self.ACCEL_X_REGISTER, 2)
			acc_y_bytes = self.i2cRead(self.ACCEL_Y_REGISTER, 2)	
			acc_z_bytes = self.i2cRead(self.ACCEL_Z_REGISTER, 2)
			acc_x = self.__to_signed16(acc_x_bytes[0], acc_x_bytes[1])
			acc_y = self.__to_signed16(acc_y_bytes[0], acc_y_bytes[1])
			acc_z = self.__to_signed16(acc_z_bytes[0], acc_z_bytes[1])
			acc = {
				"x": acc_x / 1000.0,
				"y": acc_y / 1000.0,
				"z": acc_z / 1000.0
			}

			return acc
		except Exception as e:
			print("I2C read error (acceleration):", e)
			return None
		
	def updateSpeed(self, acc):
		if acc:
			self.speed["x"] += acc["x"] * self.SAMPLE_RATE
			self.speed["y"] += acc["y"] * self.SAMPLE_RATE	
			self.speed["z"] += acc["z"] * self.SAMPLE_RATE

	def updateDisplacement(self, timeElapsed):
		# print("moved by", self.speed, "in", timeElapsed, "seconds")
		# print("displacement before", self.displacement)
		self.displacement["x"] += self.speed["x"] * timeElapsed
		self.displacement["y"] += self.speed["y"] * timeElapsed
		self.displacement["z"] += self.speed["z"] * timeElapsed
		# print("displacement after", self.displacement)
	
	def __to_signed16(self, high, low):
		value = (high << 8) | low
		return value - 65536 if value >= 32768 else value

