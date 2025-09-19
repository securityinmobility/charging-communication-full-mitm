import serial
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

if __name__ == "__main__":
    print("Arduino Connection Check")
    print("-" * 25)
    check_arduino_connection()