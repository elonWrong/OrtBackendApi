import serial
import struct
import time

class RangeFinder:
    SERIAL_PORT = 'Some string representing the serial port'  # e.g., '/dev/ttyUSB0' or 'COM3' idk but hope you do
    BAUD_RATE = 115200

    def __init__(self):
        self.ser = serial.Serial(self.SERIAL_PORT, self.BAUD_RATE, timeout=1)
        self.session_readings = []

    def read_distance(self):
        while True:
            if self.ser.in_waiting >= 9:
                data = self.ser.read(9)  # Most Waveshare models send 9-byte frames
                if data[0] == 0x59 and data[1] == 0x59:  # Frame header (0x59 0x59)
                    distance = data[2] + data[3] * 256
                    strength = data[4] + data[5] * 256
                    temperature = (data[6] + data[7] * 256) / 8 - 256
                    checksum = sum(data[:8]) & 0xFF

                    if checksum == data[8]:
                        data = {
                            'timestamp': time.time(),
                            'distance_cm': distance,
                            'strength': strength,
                            'temperature_c': round(temperature, 2)
                        }
                        self.session_readings.append(data)
                        return data
                    else:
                        print("Checksum mismatch")
            time.sleep(0.01)

    def close(self):
        self.ser.close()