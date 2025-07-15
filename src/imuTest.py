import smbus2

bus = smbus2.SMBus(1)
I2C_ADDRESS = 0x60
CALIBRATION_REGISTER = 0x1E

status = bus.read_byte_data(I2C_ADDRESS, CALIBRATION_REGISTER)
print(f"CMPS12 calibration status: {status:#04x}")