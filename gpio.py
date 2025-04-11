import threading
import serial

class GPIOManager():

    def __init__(self, block_manager):
        self.block_manager = block_manager
        self.fps_gpio = block_manager.frame_manager.experiment.fps_gpio

        # self.serialcomm = serial.Serial('COM4', 9600)
        self.serialcomm = ''
        self.pos_dict = {}
        self.pos_cat_dict = {}

    def open_smartfilm(self):
        global film_toggle
        global lane_ls
        global com_ls
        print("OPEN SMARTFILM")
        film_toggle = '1'
        for i in range(1, 5):
            com_ls[i] = film_toggle

        for lane in lane_ls:
            com_ls[0] = lane
            com_str = ','.join(com_ls) + '\n'
            res = bytes(com_str, 'utf-8')
            self.serialcomm.write(res)


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


    def voltage_off(self):
        global lane_ls
        global com_ls
        print("VOLTS OFF ")
        v_toggle = '0'
        for i in range(5, 7):
            com_ls[i] = v_toggle

        for lane in lane_ls:
            com_ls[0] = lane
            com_str = ','.join(com_ls) + '\n'
            res = bytes(com_str, 'utf-8')
            self.serialcomm.write(res)


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
        print(self.zf_pos_dict)
        print(self.zf_pos_cat_dict)
        frame_com = []
        for lane in lane_ls:
            com_ls[0] = lane
            for f_num in self.zf_pos_dict.keys():
                if self.zf_pos_cat_dict[f_num] == 'inside':
                    if lane == str(f_num):  # Top Row
                        com_ls[4] = '0'
                        com_ls[3] = '1'
                    if lane == str(f_num - 7):  # Bottom Row
                        com_ls[2] = '1'
                        com_ls[1] = '0'
                if self.zf_pos_cat_dict[f_num] == 'outside':
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
            com_ls = ['0', '0', '0', '0', '0', '0', '0']
        for com in frame_com:
            print(com)
        return frame_com


    # just dup of send social right now, need to update
    def send_shock_gpio_com(self):
        global s_com
        com_ls = ['0', '0', '0', '0', '0', '0', '0']

        for lane in lane_ls:
            com_ls[0] = lane
            for f_num in self.zf_pos_dict.keys():
                if self.zf_pos_cat_dict[f_num] == 'inside':
                    if lane == str(f_num):  # Top Row
                        com_ls[4] = '0'
                        com_ls[3] = '1'
                    if lane == str(f_num - 7):  # Bottom Row
                        com_ls[2] = '1'
                        com_ls[1] = '0'
                if self.zf_pos_cat_dict[f_num] == 'outside':
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