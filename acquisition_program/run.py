from numpy.lib.utils import source
from scipy.special import y0_zeros
from skimage.measure import label, regionprops
from skimage.morphology import remove_small_objects
import numpy as np
import win32gui
import sys
import time
import threading
import multiprocessing
import datetime
import cv2
import queue
import serial
import tkinter
import os
import pandas as pd
import torch
import PySpin  # import torch before pyspin or dependencies break
import shutil
import concurrent.futures
import experiment
import frame
import block
import track
import gpio

end_toggle = 1

def main():
    exp_name = 'demo'

    exp_time = str(datetime.datetime.now().strftime('%Y%m%d_%H%M'))
    experiment_id = exp_time + "_" + exp_name

    experiment_dir = os.getcwd() + '/' + experiment_id + '_data/'
    param_transcript_fn = experiment_id + '_params' + '.txt'
    os.makedirs(os.path.dirname(experiment_dir), exist_ok=True)

    # Set stage color arrays
    white_ar = np.zeros((1080, 1920, 3), np.uint8)
    white_ar[:, :, :] = 255

    black_ar = np.zeros((1080, 1920, 3), np.uint8)
    black_ar[:, :, :] = 0

    red_grey_ar = np.zeros((1080, 1920, 3), np.uint8)
    red_grey_ar[:260, :, :] = 125  # gray
    red_grey_ar[260:775, :, 2] = 150  # red
    red_grey_ar[775:, :, :] = 125

    blue_yellow_ar = np.zeros((1080, 1920, 3), np.uint8)
    blue_yellow_ar[:260, :, 1:] = 255  # yellow
    blue_yellow_ar[260:775, :, 0] = 255  # blue
    blue_yellow_ar[775:, :, 1:] = 255  # yellow

    fps_dict = {'fps_record': 20,       # EXACT FROM SPINVIEW is 20.11
                'fps_bg_acq': 2,
                'fps_track': 5,
                'fps_gpio': 5}

    num_of_blocks = 3

    # Time of each block (s)
    acclimate_t = 3  # white screen, no recording
    bg_acq_t1 = 3  # block 1
    condition_t1 = 3  # block 2

    # Categorize block types (acclimate / baseline / condition) and block colors (black_ar / red_grey_ar / blue_yellow_ar)
    exp_block_types = ['acclimate', 'baseline', 'condition']
    exp_block_color = [white_ar, white_ar, white_ar]

    # Make list of block times and sequence the time-course of the experiment (in seconds)
    t_second_blocks = [acclimate_t, bg_acq_t1, condition_t1]
    n_frame_blocks = [fps_dict['fps_record'] * b for b in t_second_blocks]
    total_recorded_frames = sum(n_frame_blocks)-n_frame_blocks[0]
    start_block_frame = [sum(n_frame_blocks[:i])+1 for i in range(len(n_frame_blocks))]
    stop_block_frame = [sum(n_frame_blocks[:i+1]) for i in range(len(n_frame_blocks))]

    print('total frames to be recorded:', total_recorded_frames)

    exp_blocks = list(range(num_of_blocks))      # list of total blocks, 0 indexed.
    frame_block_info = {}
    for b in exp_blocks:
        frame_block_dict = {}
        frame_block_dict['block_index']=b
        frame_block_dict['block_type']=exp_block_types[b]
        frame_block_dict['block_color']=exp_block_color[b]
        frame_block_dict['t_seconds']=t_second_blocks[b]
        frame_block_dict['frame_start']=start_block_frame[b]
        frame_block_dict['frame_stop']=stop_block_frame[b]
        frame_block_info[b] = frame_block_dict

    # Print the block start times of the experiment
    time_seq_blocks = [sum(t_second_blocks[:i + 1]) for i in range(len(t_second_blocks))]
    time_now = datetime.datetime.now()
    print('Experiment ID:', experiment_id)
    print('Block times:')
    print('Block 0 (acclimation) -', str(time_now + datetime.timedelta(seconds=time_seq_blocks[0]))[11:19])
    print('Block 1 -', str(time_now + datetime.timedelta(seconds=time_seq_blocks[1]))[11:19])
    print('Block 2 -', str(time_now + datetime.timedelta(seconds=time_seq_blocks[2]))[11:19])

    param_transcript_f = open(param_transcript_fn, 'w')
    param_transcript_f.writelines(['start: ', str(exp_time), '\n',
                                   'acclimation: ', str(acclimate_t), ' s\n',
                                   'bg_acq_t1: ', str(bg_acq_t1), ' s\n',
                                   'condition_t1: ', str(condition_t1), ' s\n'])
    param_transcript_f.close()

    ts_start = time.time()

    # Initiate record objects
    experiment_record = experiment.ExperimentManager(experiment_id, fps_dict)
    frame_record = frame.FrameManager(experiment_record, frame_block_info, total_recorded_frames)

    # Start acquiring images through the image handler queue
    open_cam_th = threading.Thread(target=experiment_record.open_camera)
    open_cam_th.daemon = True
    open_cam_th.start()

    img_proc_th = threading.Thread(target=frame_record.image_processor)
    block_seq_th = threading.Thread(target=frame_record.block_sequencer)
    img_proc_th.start()
    block_seq_th.start()
    img_proc_th.join()
    block_seq_th.join()

    ts_stop = time.time()

    param_transcript_f = open(param_transcript_fn, 'a')
    param_transcript_f.writelines(['\ntotal time:', str(ts_stop - ts_start), 's'])
    param_transcript_f.close()

    source_dir = os.getcwd()

    print("Moving data to experiment dir")

    shutil.move(source_dir + '/' + param_transcript_fn, experiment_dir + param_transcript_fn)
    shutil.move(source_dir + '/' + experiment_id+'.avi', experiment_dir + experiment_id+'.avi')

    print("Stopped Recording, exiting program")
    cv2.destroyAllWindows()
    # global end_toggle
    # end_toggle *= -1
    sys.exit(0)


def startup():
    top = tkinter.Tk()

    def action():
        global end_toggle
        end_toggle *= -1
        if end_toggle == -1:
            print('Ending Base Threads')
            os._exit(0)

    global B
    B = tkinter.Button(top, text='End Task', command=action)

    B.pack()
    top.mainloop()


def supermain():
    t1 = threading.Thread(target=main)
    t2 = threading.Thread(target=startup)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

if __name__ == '__main__':
    supermain()
