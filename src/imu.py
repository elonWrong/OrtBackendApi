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

	def __init__(self):
		self.bus = smbus2.SMBus(1)
		self.resetSpeed()

	def resetSpeed(self):
		self.speed = {
			"x": 0, 
			"y": 0,
			"z": 0
		}

	def generateStream(self):
		while True:
			orientation = self.getOrientation()
			acceleration = self.getAcc()
			if orientation and acceleration:
				data = {
					"orientation": orientation,
					"acceleration": acceleration
				}
				yield json.dumps(data) + "\n"
			elif orientation is None:
				yield json.dumps({"error": "Failed to read orientation"}) + "\n"
			elif acceleration is None:
				yield json.dumps({"error": "Failed to read acceleration"}) + "\n"
			time.sleep(0.1)

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

			return {
				"x": acc_x,
				"y": acc_y,
				"z": acc_z
			}
		except Exception as e:
			print("I2C read error (acceleration):", e)
			return None

