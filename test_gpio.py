import serial
import time
'''
ser = serial.Serial()
ser.port = 'COM5'
ser.baudrate = 9600
time.sleep(1)
ser.dtr = True
ser.open()
time.sleep(1)
ser.write(b'2,1,1,1,1,0,0\n')

# res = bytes('com_str', 'utf-8')
# s_com.write(string)
# s_com.close()
print('done')


import serial
import time

try:
    # Configure the serial port (adjust port name and baud rate as needed)
    ser = serial.Serial('COM6', 9600)  # Example for Linux
                  # ttyUSBx format on Linux
    ser.bytesize = 8   # Number of data bits = 8
    ser.parity  ='N'   # No parity
    ser.stopbits = 1   # Number of Stop bits = 1
    # ser = serial.Serial('COM3', 9600)  # Example for Windows
    time.sleep(1) # Wait for 2 seconds
    # ser.timeout = 1
    # Ensure the serial port is open
    if ser.is_open:
        print(f"Serial port {ser.name} is open")
        # data = ['2','1','1','1','1','0','0']
        # my_string = ','.join(data) + '\n'
        # res = bytes(com_str, 'utf-8')
        # self.serialcomm.write(res)
        # mydata = bytes(my_string,'utf-8')
        # ser.write(mydata)
        # print(f"Sent: {mydata}")
        # Data to be sent (must be bytes)
        data_to_send = b'5,1,0,1,0,0,0,0\n'
        # print(type(data_to_send))
        # print(len(data_to_send))
        # Write data to the serial port
        ser.write(data_to_send)
        # # ser.write(('2,1,1,1,1,0,0\n').("ascii"))
        # print(f"Sent: {data_to_send}")

    else:
        print("Serial port could not be opened")

except serial.SerialException as e:
    print(f"Error: {e}")

finally:
    # Close the serial port
    if ser.is_open:
        ser.close()
        print("Serial port closed")

import time
import keyboard
import pyfirmata

# set up arduino board
board = pyfirmata.Arduino('COM3')

# start while loop to keep blinking indefinitely
while True:

    if keyboard.is_pressed('esc'): # stop making the arduino blink if the escape key is pressed
        break

    board.digital[13].write(1) # turn pin 13 ON
    time.sleep(0.5)            # wait 1/2 second
    board.digital[13].write(0) # turn pin 13 OFF
    time.sleep(0.5)            # wait 1/2 second
'''
import serial
import time

try:
    # Configure the serial port (adjust port name and baud rate as needed)
    ser = serial.Serial('COM5', 9600)  # Example for Linux
    # ttyUSBx format on Linux
    # ser.bytesize = 8   # Number of data bits = 8
    # ser.parity  ='N'   # No parity
    # ser.stopbits = 1   # Number of Stop bits = 1
    # ser.rtscts = True
    # ser = serial.Serial('COM3', 9600)  # Example for Windows
    time.sleep(1)  # Wait for 2 seconds
    ReceivedString = ser.readline()
    print(f"Received: {ReceivedString}")
    # ser.timeout = 1
    # Ensure the serial port is open
    if ser.is_open:
        print(f"Serial port {ser.name} is open")
        data = ['1', '0', '0', '0', '0', '1', '1']
        my_string = ','.join(data) + '\n'
        mydata = bytes(my_string, 'utf-8')
        ser.write(mydata)
        print(f"Sent: {mydata}")
        ReceivedString = ser.readline()
        print(f"Received: {ReceivedString}")

        time.sleep(0.02)
        data = ['2', '0', '0', '0', '0', '1', '1']
        my_string = ','.join(data) + '\n'
        mydata = bytes(my_string, 'utf-8')
        ser.write(mydata)
        print(f"Sent: {mydata}")
        ReceivedString = ser.readline()
        print(f"Received: {ReceivedString}")

        time.sleep(0.02)
        data = ['3', '0', '0', '0', '0', '1', '1']
        my_string = ','.join(data) + '\n'
        mydata = bytes(my_string, 'utf-8')
        ser.write(mydata)
        print(f"Sent: {mydata}")
        ReceivedString = ser.readline()
        print(f"Received: {ReceivedString}")

        time.sleep(0.02)
        data = ['4', '0', '0', '0', '0', '1', '1']
        my_string = ','.join(data) + '\n'
        mydata = bytes(my_string, 'utf-8')
        ser.write(mydata)
        print(f"Sent: {mydata}")
        ReceivedString = ser.readline()
        print(f"Received: {ReceivedString}")

        time.sleep(0.02)
        data = ['5', '0', '0', '0', '0', '1', '1']
        my_string = ','.join(data) + '\n'
        mydata = bytes(my_string, 'utf-8')
        ser.write(mydata)
        print(f"Sent: {mydata}")
        ReceivedString = ser.readline()
        print(f"Received: {ReceivedString}")

        time.sleep(0.02)
        data = ['6', '0', '0', '0', '0', '1', '1']
        my_string = ','.join(data) + '\n'
        mydata = bytes(my_string, 'utf-8')
        ser.write(mydata)
        print(f"Sent: {mydata}")
        ReceivedString = ser.readline()
        print(f"Received: {ReceivedString}")

        time.sleep(0.02)
        data = ['7', '0', '0', '0', '0', '1', '1']
        my_string = ','.join(data) + '\n'
        mydata = bytes(my_string, 'utf-8')
        ser.write(mydata)
        print(f"Sent: {mydata}")
        ReceivedString = ser.readline()
        print(f"Received: {ReceivedString}")
        #----------------------------------------------
        time.sleep(0.02)
        # data = ['7', '0', '0', '0', '0', '1', '1']
        # my_string = ','.join(data) + '\n'
        # mydata = bytes(my_string, 'utf-8')
        # ser.write(mydata)
        # print(f"Sent: {mydata}")
        # ReceivedString = ser.readline()
        # print(f"Received: {ReceivedString}")


        # Data to be sent (must be bytes)
        # data_to_send = b'3,1,0,1,0,0,0,0\n'
        # # # print(type(data_to_send))
        # # # print(len(data_to_send))
        # # # Write data to the serial port
        # ser.write(data_to_send)
        # # ser.write(('2,1,1,1,1,0,0\n').("ascii"))
        # print(f"Sent: {data_to_send}")
        # time.sleep(10)


    else:
        print("Serial port could not be opened")

except serial.SerialException as e:
    print(f"Error: {e}")

finally:
    # Close the serial port
    if ser.is_open:
        ser.close()
        print("Serial port closed")
