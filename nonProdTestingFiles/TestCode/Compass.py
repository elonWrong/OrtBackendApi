import smbus2
import time

# CMPS12 compass I2C address
I2C_ADDRESS = 0x60

# CMPS12 Registers
BEARING_REGISTER = 2 
PITCH_REGISTER = 4
ROLL_REGISTER = 5


# I2C bus (Raspberry Pi usually uses bus 1)
bus = smbus2.SMBus(1)

def i2cRead(registerAddress, numBytes=1):
    # Read bytes from a register
    return bus.read_i2c_block_data(I2C_ADDRESS, registerAddress, numBytes)

try:
    while True:
        try:
            # Read 4 bytes: bearing (2), pitch (1), roll (1)
            receivedBytes = i2cRead(BEARING_REGISTER, 4)

        except Exception as e:
            print("I2C read error:", e)
            continue

        # Calculate bearing
        bearing = ((receivedBytes[0] << 8) + receivedBytes[1]) / 10.0

        # Pitch (signed)
        pitch = receivedBytes[2]
        if pitch > 127:
            pitch -= 256

        # Roll (signed)
        roll = receivedBytes[3]
        if roll > 127:
            roll -= 256

        print(f"Bearing: {bearing:.1f}°, Pitch: {pitch}, Roll: {roll}", end="\r")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Program stopped by user.")
