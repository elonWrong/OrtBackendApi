import serial
import time

class RangeFinder:
    SERIAL_PORT = '/dev/ttyAMA0'
    BAUD_RATE = 921600
    TOF_HEADER = (87, 0, 255)  # 0x57, 0x00, 0xFF
    TOF_LENGTH = 16

    def __init__(self):
        self.ser = serial.Serial(self.SERIAL_PORT, self.BAUD_RATE, timeout=1)
        self.session_readings = []

    def verify_checksum(self, data):
        checksum = sum(data[:self.TOF_LENGTH-1]) % 256
        return checksum == data[self.TOF_LENGTH-1]

    def read_distance(self):
        while True:
            if self.ser.in_waiting >= self.TOF_LENGTH * 2:
                raw = self.ser.read(self.TOF_LENGTH * 2)
                # Convert bytes to ints (Python 3)
                data = [b for b in raw]
                # Scan for header
                for j in range(len(data) - self.TOF_LENGTH + 1):
                    if (data[j], data[j+1], data[j+2]) == self.TOF_HEADER:
                        frame = data[j:j+self.TOF_LENGTH]
                        if self.verify_checksum(frame):
                            if (frame[12] | (frame[13]<<8)) == 0:
                                return {"error": "Out of range"}
                            tof_id = frame[3]
                            system_time = frame[4] | (frame[5]<<8) | (frame[6]<<16) | (frame[7]<<24)
                            distance = frame[8] | (frame[9]<<8) | (frame[10]<<16)
                            status = frame[11]
                            signal = frame[12] | (frame[13]<<8)
                            result = {
                                "timestamp": time.time(),
                                "distance_mm": distance
                            }
                            self.session_readings.append(result)
                            return result
                        else:
                            print("Checksum mismatch")
            time.sleep(0.01)

    def close(self):
        self.ser.close()

if __name__ == "__main__":
    rf = RangeFinder()
    while True:
        print(rf.read_distance())