import threading
import serial
import time

class GPIOManager():

    def __init__(self, block_manager):
        self.block_manager = block_manager
        self.fps_gpio = block_manager.frame_manager.experiment.fps_gpio

        self.lane_ls = ['1','2','3','4','5','6','7']
        self.ser = None
        self.gpio_switch = False
        if not self.gpio_switch:
            self.open_serial()
        self.gpio_wait = True
        self.films_on = False


    def open_serial(self):
        try:
            self.ser = serial.Serial('COM5', 9600)  # Example for Linux
            time.sleep(1)
            ReceivedString = self.ser.readline()
        except serial.SerialException as e:
            print(f"Error: {e}")
        self.gpio_switch = True
        return


    def close_serial(self):
        if self.ser.is_open:
            self.ser.close()
        self.gpio_wait = False
        return


    def turn_off_films(self):
        if self.ser.is_open:
            print("closing films")
            lane_nums = ['1', '2', '3', '4', '5', '6', '7']
            data = [0, '0', '0', '0', '0', '0', '0']

            for lane_num in lane_nums:
                data[0] = lane_num

                my_string = ','.join(data) + '\n'
                mydata = bytes(my_string, 'utf-8')
                self.ser.write(mydata)
                ReceivedString = self.ser.readline()
                time.sleep(0.02)

            self.films_on = False

        else:
            print("Serial port is not open")


    def turn_on_films(self):

        if self.ser.is_open:
            print("opening films")
            lane_nums = ['1','2','3','4','5','6','7']
            data = [0, '1', '1', '1', '1', '0', '0']

            for lane_num in lane_nums:
                data[0] = lane_num

                my_string = ','.join(data) + '\n'
                mydata = bytes(my_string, 'utf-8')
                self.ser.write(mydata)
                ReceivedString = self.ser.readline()
                time.sleep(0.02)

            self.films_on = True

        else: print("Serial port is not open")


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