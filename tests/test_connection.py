import serial
import time
import os


# Quick test script to verify Arduino connection from the docker container

def check_arduino_connection(port="/dev/ttyUSB0", baudrate=9600):
    """Simple check if Arduino is connected and accessible"""
    
    # Check 1: Does the device file exist?
    if not os.path.exists(port):
        print(f"✗ Device {port} not found")
        return False

    # Check 2: Can the serial connection be established?
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        ser.close()
        print(f"✓ Arduino connection successful on {port}")
        return True
    except serial.SerialException as e:
        print(f"✗ Cannot open {port}: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def check_arduino_response(port="/dev/ttyUSB0", baudrate=9600):
    """Check if Arduino responds to a simple command
    Send invalid command and expect an error response
    """

    COMMAND = bytes([0xC1, 0x00, 0xFF])
    EXPECTED_RESPONSE = bytes([0xB1, 0x00, 0xFF])
    RESPONSE_LENGTH = len(EXPECTED_RESPONSE)

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(0.2)
        ser.reset_input_buffer()
        ser.write(COMMAND)
        response = ser.read(RESPONSE_LENGTH+6)

        print(f"Sent command: {COMMAND.hex()}")
        if response == EXPECTED_RESPONSE:
            print("✓ Arduino responded correctly")
        else:
            print(f"✗ Unexpected response from Arduino: {response}")
            ser.write(COMMAND)
            response = ser.read(RESPONSE_LENGTH+3)
            print("Response after command re-sent:", response)
    except serial.SerialException as e:
        print(f"✗ Cannot communicate with Arduino: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    print("Arduino Check")
    print("-" * 25)
    check_arduino_connection()
    check_arduino_response()
