import threading
import serial
import time

class GPIOManager():

    def __init__(self, block_manager):
        self.block_manager = block_manager
        self.fps_gpio = block_manager.frame_manager.experiment.fps_gpio

        self.lane_ls = ['1','2','3','4','5','6','7']
        try:
            self.serialcomm = serial.Serial('COM5', 9600)
            self.serialcomm.timeout = 1
            received_string = self.serialcomm.readline()
            print(f"Received: {received_string}")
        except serial.SerialException as e:
            print(f"Error: {e}")

    def open_smartfilm(self):
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
                data = ['1', '0', '0', '0', '0', '0', '0']
                my_string = ','.join(data) + '\n'
                mydata = bytes(my_string, 'utf-8')
                ser.write(mydata)
                print(f"Sent: {mydata}")
                ReceivedString = ser.readline()
                print(f"Received: {ReceivedString}")

                time.sleep(0.01)
                data = ['2', '0', '0', '0', '0', '0', '0']
                my_string = ','.join(data) + '\n'
                mydata = bytes(my_string, 'utf-8')
                ser.write(mydata)
                print(f"Sent: {mydata}")
                ReceivedString = ser.readline()
                print(f"Received: {ReceivedString}")

                time.sleep(0.01)
                data = ['3', '0', '0', '0', '0', '0', '0']
                my_string = ','.join(data) + '\n'
                mydata = bytes(my_string, 'utf-8')
                ser.write(mydata)
                print(f"Sent: {mydata}")
                ReceivedString = ser.readline()
                print(f"Received: {ReceivedString}")

                time.sleep(0.01)
                data = ['4', '0', '0', '0', '0', '0', '0']
                my_string = ','.join(data) + '\n'
                mydata = bytes(my_string, 'utf-8')
                ser.write(mydata)
                print(f"Sent: {mydata}")
                ReceivedString = ser.readline()
                print(f"Received: {ReceivedString}")

                time.sleep(0.01)
                data = ['5', '0', '0', '0', '0', '0', '0']
                my_string = ','.join(data) + '\n'
                mydata = bytes(my_string, 'utf-8')
                ser.write(mydata)
                print(f"Sent: {mydata}")
                ReceivedString = ser.readline()
                print(f"Received: {ReceivedString}")

                time.sleep(0.01)
                data = ['6', '0', '0', '0', '0', '0', '0']
                my_string = ','.join(data) + '\n'
                mydata = bytes(my_string, 'utf-8')
                ser.write(mydata)
                print(f"Sent: {mydata}")
                ReceivedString = ser.readline()
                print(f"Received: {ReceivedString}")

                time.sleep(0.01)
                data = ['7', '0', '0', '0', '0', '0', '0']
                my_string = ','.join(data) + '\n'
                mydata = bytes(my_string, 'utf-8')
                ser.write(mydata)
                print(f"Sent: {mydata}")
                ReceivedString = ser.readline()
                print(f"Received: {ReceivedString}")

                time.sleep(0.01)

            else:
                print("Serial port could not be opened")

        except serial.SerialException as e:
            print(f"Error: {e}")

        finally:
            # Close the serial port
            if ser.is_open:
                ser.close()
                print("Serial port closed")

    def close_smartfilm(self):
        global film_toggle
        global lane_ls
        global com_ls
        print("CLOSE SMARTFILM")
        film_toggle = '0'
        for i in range(1, 5):
            com_ls[i] = film_toggle

        for lane in lane_ls:
            com_ls[0] = lane
            com_str = ','.join(com_ls) + '\n'
            res = bytes(com_str, 'utf-8')
            self.serialcomm.write(res)


    def voltage_on(self):
        global lane_ls
        global com_ls
        print("VOLTS ON ")
        v_toggle = '1'
        for i in range(5, 7):
            com_ls[i] = v_toggle

        for lane in lane_ls:
            com_ls[0] = lane
            com_str = ','.join(com_ls) + '\n'
            res = bytes(com_str, 'utf-8')
            self.serialcomm.write(res)
            print(f"Sent: {res}")
            ReceivedString = self.serialcomm.readline()
            print(f"Received: {ReceivedString}")


    def start_gpio_thread(self, paradigm, track_block):
        if paradigm == 'social':
            target = self.send_social_gpio_com()
        if paradigm == 'shock':
            target = self.send_shock_gpio_com()
        gpio_thread = threading.Thread(target=target,args=(self.zf_pos_dict, self.zf_pos_cat_dict, '_block_'+str(track_block)))
        gpio_thread.start()
        gpio_thread.join()

        return


    def send_social_gpio_com(self):
        global s_com
        global lane_ls
        com_ls = ['0', '0', '0', '0', '0', '0', '0']
        frame_com = []
        for lane in self.lane_ls:
            com_ls[0] = lane
            for f_num in self.block_manager.track_record.fish_pos_dict.keys():
                if self.block_manager.track_record.fish_pos_cat_dict[f_num] == 'inside':
                    if lane == str(f_num):  # Top Row
                        com_ls[4] = '0'
                        com_ls[3] = '1'
                    if lane == str(f_num - 7):  # Bottom Row
                        com_ls[2] = '1'
                        com_ls[1] = '0'
                if self.block_manager.track_record.fish_pos_cat_dict[f_num] == 'outside':
                    if lane == str(f_num):  # Top Row
                        com_ls[4] = '1'
                        com_ls[3] = '0'
                    if lane == str(f_num - 7):  # Bottom Row
                        com_ls[2] = '0'
                        com_ls[1] = '1'

            com_str = ','.join(com_ls) + '\n'
            res = bytes(com_str, 'utf-8')
            s_com.write(res)
            frame_com.append(com_str)
            com_ls = ['0', '1', '1', '1', '1', '1', '1']
        for com in frame_com:
            print(com)
        return frame_com


    # just dup of send social right now, need to update
    def send_shock_gpio_com(self):
        global s_com
        com_ls = ['0', '0', '0', '0', '0', '0', '0']

        for lane in lane_ls:
            com_ls[0] = lane
            for f_num in self.block_manager.track_record.fish_pos_dict.keys():
                if self.block_manager.track_record.fish_pos_cat_dict[f_num] == 'inside':
                    if lane == str(f_num):  # Top Row
                        com_ls[4] = '0'
                        com_ls[3] = '1'
                    if lane == str(f_num - 7):  # Bottom Row
                        com_ls[2] = '1'
                        com_ls[1] = '0'
                if self.block_manager.track_record.fish_pos_cat_dict[f_num] == 'outside':
                    if lane == str(f_num):  # Top Row
                        com_ls[4] = '1'
                        com_ls[3] = '0'
                    if lane == str(f_num - 7):  # Bottom Row
                        com_ls[2] = '0'
                        com_ls[1] = '1'

            com_str = ','.join(com_ls) + '\n'
            res = bytes(com_str, 'utf-8')
            s_com.write(res)
            return com_str