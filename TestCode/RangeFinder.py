import serial
import struct
import time

# Adjust based on your device
SERIAL_PORT = 'Some string representing the serial port'  # e.g., '/dev/ttyUSB0' or 'COM3' idk but hope you do
BAUD_RATE = 115200
    
# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

def read_distance():
    while True:
        if ser.in_waiting >= 9:
            data = ser.read(9)  # Most Waveshare models send 9-byte frames
            if data[0] == 0x59 and data[1] == 0x59:  # Frame header (0x59 0x59)
                distance = data[2] + data[3] * 256
                strength = data[4] + data[5] * 256
                temperature = (data[6] + data[7] * 256) / 8 - 256
                checksum = sum(data[:8]) & 0xFF

                if checksum == data[8]:
                    return {
                        'distance_cm': distance,
                        'strength': strength,
                        'temperature_c': round(temperature, 2)
                    }
                else:
                    print("Checksum mismatch")
        time.sleep(0.01)

try:
    while True:
        result = read_distance()
        if result:
            print(f"Distance: {result['distance_cm']} cm | "
                  f"Strength: {result['strength']} | "
                  f"Temp: {result['temperature_c']}°C")
except KeyboardInterrupt:
    print("Stopping...")
    ser.close()