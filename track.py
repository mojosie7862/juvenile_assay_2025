from numpy.lib.utils import source
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
import gpio


def background_detection(bgtot_init, bg_init_q, block_index):
    """
    Taking the median of the block's total background array, blurring it, saving it, and adding to queue
    for access

    Might need to add arguments directly because it's a separate process
    Might need to switch back to launching in a thread because of time to spin up thread takes longer (if processing
    individual well images rather than the whole rig)
    """
    print('-------------INIT BG DETECT-----------')
    median_bg, median_bg_indicies = torch.nanmedian(bgtot_init, dim=0)
    np_median_bg = median_bg.numpy()
    cv2.imwrite('background' + block_index + '.jpg', np_median_bg)
    bg_blur = cv2.GaussianBlur(np_median_bg, (5, 5), 0)
    bg_init_q.put_nowait(bg_blur)
    bg_init_q.close()

    return

class TrackingManager():
    
    
    def __init__(self, block_manager):
        '''
        :param block_manager:
        :param bgtot_init: array of images acquired from block for background detection
        :param bg_init_q: queue to hold bgtot_init
        '''
        self.block_manager = block_manager
        self.frame_manager = block_manager.frame_manager
        self.experiment = block_manager.frame_manager.experiment

        self.fps_bg_acq = self.block_manager.frame_manager.experiment.fps_bg_acq
        self.fps_track = self.block_manager.frame_manager.experiment.fps_track

        # BACKGROUND AQUISITION AND INITIALIZATION
        self.bg_init_counter = 0
        self.bg_frame_counter = 0  # COUNTER FOR BLOCK BG FRAMES (median of which is the background used for the following block)
        self.bg_init_q = multiprocessing.Queue(maxsize=1)  # QUEUE FOR BG DETECTION EVENT
        self.bg_blur = None
        self.bgtot_len = int(self.block_manager.t_seconds * self.fps_bg_acq)
        self.bgtot_init = torch.zeros((self.bgtot_len, 512, 528))  # LENGTH OF ARRAY FOR BLOCK BG DETECTION
        self.bgtot_init[:] = torch.nan

        self.tracked_frame_counter = 0
        self.fish_pos_dict = {}
        self.fish_pos_cat_dict = {}
        self.track_frame_com = ''

    def background_frame_process(self, img):
        '''
        Adding frame to total background array
        :param img:
        :return:
        '''
        # while self.bg_frame_counter > len(self.bgtot_init): continue
        if img is not None:
            self.bg_frame_counter += 1
            tensor_img = np.copy(img)
            bg_img_init_tensor = torch.from_numpy(tensor_img[:, :])
            # print(self.bg_frame_counter, len(self.bgtot_init))
            self.bgtot_init[self.bg_frame_counter - 1][:, :] = bg_img_init_tensor
        else:
            return


    def start_background_detection(self):
        '''
        Opening process to take median of total background array quickly
        :return: to make sure this only happens once per block
        '''

        if self.bg_init_counter == 0:
            self.bg_init_counter += 1
            bg_detect_proc = multiprocessing.Process(target=background_detection,
                                                     args=(self.bgtot_init,  self.bg_init_q, '_block_' + str(self.block_manager.index+1)))
            bg_detect_proc.start()
            bg_t0 = time.time()
            while True:
                if not self.bg_init_q.empty():
                    self.frame_manager.blocks[self.block_manager.index+1].track_record.bg_blur = self.bg_init_q.get_nowait()
                    break
            bg_detect_proc.join()
            bg_t1 = time.time()
            bg_time_diff = bg_t1 - bg_t0
            print('bg_time_diff', bg_time_diff)
            return
        else:
            return


    def background_acquisition(self, frame_img):
        '''
        Managing frames as received from recording. Either being added into total background array or starting
        background detection when total background array is complete.
        :param frame_img
        '''

        if self.bg_frame_counter < self.bgtot_len-1:
            if self.frame_manager.recorded_frame_counter % (self.experiment.fps_record / self.fps_bg_acq) == 0:
                print('background frame process', self.bg_frame_counter, self.bgtot_len, self.block_manager.t_seconds)
                self.background_frame_process(frame_img)
        else:
            self.background_frame_process(frame_img)
            print('background frame process', self.bg_frame_counter, self.bgtot_len, self.block_manager.t_seconds)

            self.start_background_detection()

    # reaccount for cropped images
    def load_pos_cat(self, fish_num, pos_cat_dict, y):
        '''
        get position category 'inside' or 'outside' of a centroid in a well from y-coordinate
        :param fish_num: well number of the centroid
        :param pos_cat_dict: position category dictionary
        :param y: y-coordinate
        '''
        if fish_num <= 7:  # Top Row
            if y <= 88:  # outside half
                pos_cat_dict[fish_num] = 'outside'
            if y > 88:  # inside half
                pos_cat_dict[fish_num] = 'inside'
        if fish_num > 7:  # Bottom Row
            if y <= 344:  # inside half
                pos_cat_dict[fish_num] = 'inside'
            if y > 344:  # outside half
                pos_cat_dict[fish_num] = 'outside'
        return
            
    # reaccount for cropped images
    def position_track(self, img, send_gpio='just_track'):

        img_blur = cv2.GaussianBlur(img, (5, 5), 0)                                          # blur current image
        img_bg_subtracted = np.uint8(abs(np.float32(self.bg_blur) - np.float32(img_blur)))
        img_thresholded = cv2.threshold(img_bg_subtracted, 5, 255, cv2.THRESH_BINARY)[1]    # 6 is how dark it needs to be
        img_labeled= label(img_thresholded)                                                              # label the connected components in the thresholded mask
        img_cleaned = remove_small_objects(img_labeled, 150)                                    # remove small objects from thresholded image
                                                                                                        # balance with threshold to account for difference between droplettes and fish
        img_relabeled = label(img_cleaned)                                                              # re-label since small objects removes so get 1 to nFish

        props = regionprops(img_relabeled)
        total_obj = np.amax(img_relabeled)
        # print(total_obj)

        for ind in range(0, total_obj):

            ycent, xcent = props[ind].centroid  # find the centroid of objects
            area = props[ind].area

            if 40 < ycent < 216:  # ignore stimuli fish
                continue
            if area < 150:
                continue

            row = int(ycent / (216))
            col = int(xcent / (528 / 7))
            zf_id = (row * 7) + (col + 1)

            # cent_data = [block_ind, rec_img_count, t_put, t_get, t_diff, zf_id, xcent, ycent, area]
            # experiment_data.append(cent_data)

            if send_gpio == 'just_track':
                return img_thresholded

            # LOADING ZF POSITION DICT and POSITION CATEGORY DICT (overwriting smaller area objects with the largest one)
            if zf_id not in self.fish_pos_dict.keys():
                self.fish_pos_dict[zf_id] = [area, (ycent, xcent)]  # load to position dictionary
                self.load_pos_cat(zf_id, self.fish_pos_cat_dict, ycent)  # load to category dictionary
            else:
                if area > self.fish_pos_dict[zf_id][0]:  # if area of this object is bigger than the existing, replace centroid position data
                    self.fish_pos_dict[zf_id] = [area, (ycent, xcent)]  # reload to position dictionary
                else:
                    continue

            # AVOID LOADING POSITION CATEGORY DICT IN REGIONS NEAR FILM (increased artifact ratio)
            if not 146 < ycent < 286 or ycent < 30 or ycent > 400:
                self.load_pos_cat(zf_id, self.fish_pos_cat_dict, ycent)
            else:  # when past film boundary, load category dictionary with last position beyond film boundary
                self.load_pos_cat(zf_id, self.fish_pos_cat_dict, self.fish_pos_dict[zf_id][1][0])

            # USING POSITION CATEGORY DICT, SEND GPIO COM_STR
            if send_gpio == 'social':
                # self.track_frame_com = self.block_manager.gpio_record.send_social_gpio_com()
                self.track_frame_com = self.block_manager.gpio_record.voltage_on()
            if send_gpio == 'shocks':
                self.track_frame_com = self.block_manager.gpio_record.send_shock_gpio_com()

            track_frame_data = [self.block_manager.current_block,
                                self.frame_manager.recorded_frame_counter,
                                self.track_frame_com,
                                self.fish_pos_dict]

            # gpio_data.append(frame_data)
            print('track_frame_data', track_frame_data)

        return img_thresholded


    def track_frame(self, img):

        if self.bg_blur is not None:
            thresh_frame = self.position_track(img)
            self.tracked_frame_counter += 1
            print('tracked_frame_counter', self.tracked_frame_counter)

            # eventually remove thresholded image display to improve performance
            # cv2.imshow('tracked frame', thresh_frame)
            # cv2.waitKey(1)
            #
            # cv2.imwrite(tracked_img_dir[0] + 'tracked_frame_%d.jpg' % frame_count, thresh_frame)