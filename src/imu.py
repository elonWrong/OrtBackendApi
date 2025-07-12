import json
import smbus2
import time

class IMU:
	I2C_ADDRESS = 0x60

	# CMPS12 Registers
	BEARING_REGISTER = 2 
	PITCH_REGISTER = 4
	ROLL_REGISTER = 5
	ACCEL_X_REGISTER = 6
	ACCEL_Y_REGISTER = 7
	ACCEL_Z_REGISTER = 8
	
	SAMPLE_RATE = 0.01  # 10 ms sample rate

	def __init__(self):
		self.bus = smbus2.SMBus(1)
		self.previousReading = None
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

	async def generateStream(self):
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
					"speed": self.speed,
					"displacement": self.displacement,
					"timeStamp": timeStamp,
					"previousReading": {
						"timeElapsed": self.previousReading["timeStamp"] if self.previousReading else None,
						"previousOrientation": self.previousReading["orientation"] if self.previousReading else None,
						"previousAcceleration": self.previousReading["acceleration"] if self.previousReading else None,
						"previousSpeed": self.previousReading["speed"] if self.previousReading else None,
						"previousDisplacement": self.previousReading["displacement"] if self.previousReading else None
					}
				}
				self.previousReading = timeStamp
				print("IMU Data:", data, end="\r")
			#	yield json.dumps(data) + "\n"
			#elif orientation is None:
			#	yield json.dumps({"error": "Failed to read orientation"}) + "\n"
			#elif acceleration is None:
			#	yield json.dumps({"error": "Failed to read acceleration"}) + "\n"
			time.sleep(self.SAMPLE_RATE)

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
		
	def getAcc(self):
		try:
			# Read 6 bytes: Accel X (2), Y (2), Z (2)
			acc_bytes = self.i2cRead(self.ACCEL_X_REGISTER, 6)
			# Combine high and low bytes into signed 16-bit integers
			def to_signed16(high, low):
				value = (high << 8) | low
				return value - 65536 if value >= 32768 else value
			acc_x = to_signed16(acc_bytes[0], acc_bytes[1])
			acc_y = to_signed16(acc_bytes[2], acc_bytes[3])
			acc_z = to_signed16(acc_bytes[4], acc_bytes[5])

			acc = {
				"x": acc_x,  # Convert to g
				"y": acc_y,
				"z": acc_z
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
		print("moved by", self.speed, "in", timeElapsed, "seconds")
		print("displacement before", self.displacement)
		self.displacement["x"] += self.speed["x"] * timeElapsed
		self.displacement["y"] += self.speed["y"] * timeElapsed
		self.displacement["z"] += self.speed["z"] * timeElapsed
		print("displacement after", self.displacement)

