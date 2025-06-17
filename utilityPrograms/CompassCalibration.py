from smbus2 import SMBus
import time

CMPS12_ADDR = 0x60  # Default I2C address for CMPS12

def start_calibration(bus):
	print("starting")
	bus.write_byte_data(CMPS12_ADDR, 0x00, 0xF0)
    
def end_calibration(bus):
    print("Ending")
    bus.write_byte_data(CMPS12_ADDR, 0x00, 0xF1)


def calibration_sequence():
    with SMBus(1) as bus:
        start_calibration(bus)

        instructions = [
            ("Rotate +45° around X-axis", 5),
            ("Rotate -45° around X-axis", 5),
            ("Rotate +45° around Y-axis", 5),
            ("Rotate -45° around Y-axis", 5),
            ("Rotate +45° around Z-axis", 5),
            ("Rotate -45° around Z-axis", 5),
            ("Move in slow figure-8 pattern", 10),
        ]

        for step, duration in instructions:
            time.sleep(duration)
            print(step)

        end_calibration(bus)

