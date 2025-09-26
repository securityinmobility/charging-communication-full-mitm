import serial
import time

from messages import Message

class MitMBoard:
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(0.1)
        self.ser.reset_input_buffer()

    def send_message(self, message: Message):
        try:
            self.ser.write(message.to_bytes())
        except serial.SerialException as e:
            print(f"Cannot communicate with Arduino: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def read_response(self, length=3):
        try:
            time.sleep(0.1)
            return self.ser.read(length)
        except serial.SerialException as e:
            print(f"Cannot communicate with Arduino: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def close(self):
        self.ser.close()