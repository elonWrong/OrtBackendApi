import smbus2
import time

class IMU:
	I2C_ADDRESS = 0x60

	# CMPS12 Registers
	BEARING_REGISTER = 2 
	PITCH_REGISTER = 4
	ROLL_REGISTER = 5
	
	def __init__(self):
		self.bus = smbus2.SMBus(1)
		self.speed = {
			"x": 0,
			"y": 0,
			"z": 0
		}
		
		
	def i2cRead(self, registerAddress, numBytes=1):
    # Read bytes from a register
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
		# Pitch (signed)
		pitch = receivedBytes[2]
		if pitch > 127:
			pitch -= 25		
		# Roll (signed)
		roll = receivedBytes[3]
		if roll > 127:
			roll -= 256

		orientation = {
			"bearing": bearing,
			"pitch": pitch,
			"roll": roll
		}

		return orientation
		
	def resetSpeed(self):
		self.speed = {
			"x": 0,
			"y": 0,
			"z": 0
		}
		
		
	def getAcc():
		pass
		
	def getSpeed():
		pass
