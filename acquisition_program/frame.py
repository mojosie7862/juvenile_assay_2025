import time
import cv2
import block
import queue

class FrameManager():

    def __init__(self, experiment, frame_block_dicts):
        self.experiment = experiment
        self.frame_img = None

        # Create dictionary of information needed for each block in the experiment
        self.blocks = {}
        for block_index, frame_block_dict in frame_block_dicts.items():
            # print('block_index',block_index)
            # print(frame_block_dict)
            # have this be the designation of background acquisition / tracked blocks for gamma version (live-tracking but no continuous tracking)
            self.blocks[block_index] = block.BlockManager(self, frame_block_dict)

        print(self.blocks)

        self.current_block = None
        self.current_block_manager = None

        self.processed_frame_counter = 0
        self.recorded_frame_counter = 0
        self.processed_frame_ls = [0]

        self.frame_t_put = None
        self.frame_t_get = None
        self.frame_t_diff = None
        self.frame_t_res = None

        self.frame_tput_ls = []
        self.frame_tget_ls = []
        self.frame_tdiff_ls = []

        self.hold_record = True
        self.total_recorded_frames = 0


    def image_processor(self):
        global bg_init_done

        while self.experiment.continue_recording:

            #in track blocks, the first image will be before opening og gpio channel, 2nd will be once
            if self.experiment.img_q.full():
                # Get an image (and time it was snapped) from Spinnaker SDK to process
                (self.frame_t_put, img) = self.experiment.img_q.get()
                self.frame_t_get = time.time()
                self.frame_t_diff = self.frame_t_get - self.frame_t_put         # time between acquisition of image and retrival from image queue
                self.experiment.img_q.task_done()
                self.frame_tget_ls.append(self.frame_t_get)
                self.frame_img = img.reshape(512, 528)                          # add dimension to the image array

                # Display processed image
                cv2.imshow('frame', self.frame_img)
                cv2.waitKey(1)
                self.processed_frame_counter += 1
                self.processed_frame_ls.append(self.processed_frame_counter)
                # print('processed_frame_counter', self.processed_frame_counter)

                # Start recording images
                if self.current_block > 0:
                    self.experiment.video_out.write(self.frame_img)
                    self.recorded_frame_counter += 1
                    # print('recorded_frame_counter', self.recorded_frame_counter)

                    self.frame_tput_ls.append(self.frame_t_put)

                    # if self.current_block_manager.block_frame_counter % self.experiment.track_frame_skip == 0:
                    #     self.current_block_manager.track_record.track_frame(self.frame_img)

                self.current_block_manager.block_frame_counter+=1
                # print('block_frame_counter', self.current_block_manager.block_frame_counter)
                # print('total_recorded_frames', self.total_recorded_frames) # stuck at 200 - not expected, look at this


            # if not self.hold_record:
            #     self.experiment.continue_recording = False

            # send a conditional (although not actually conditional in beta with no live-tracking) block into stimulus administration
            if self.current_block in self.experiment.track_blocks:
                if self.current_block_manager.block_frame_counter == self.current_block_manager.start_frame:
                    if not self.current_block_manager.gpio_record.films_on:
                        self.current_block_manager.gpio_record.turn_on_films()
                        print('films on at frame', self.recorded_frame_counter)
                if self.current_block_manager.block_frame_counter == self.current_block_manager.stop_frame:
                    if self.current_block_manager.gpio_record.films_on:
                        self.current_block_manager.gpio_record.turn_off_films()
                        print('films off at frame', self.recorded_frame_counter)


                    # if self.current_block_manager.block_frame_counter == self.current_block_manager.total_block_frames+1: #test this +1... otherwise might need separate thread, or something blocking onset of new block while films are closing
                    #     self.current_block_manager.gpio_record.turn_off_films()
                    #     print('films off at frame', self.recorded_frame_counter)
                        # print(self.current_block_manager.index, self.current_block_manager.block_event_status)
                        self.current_block_manager.gpio_record.close_serial()
                        self.current_block_manager.block_event_status = 'finished'

            if self.recorded_frame_counter > 37000:
                self.experiment.continue_recording = False
                print("ending experiment at frame", self.recorded_frame_counter)

                return

        return


    def block_sequencer(self):

        for block_index, self.current_block_manager in self.blocks.items():

            self.current_block = self.current_block_manager.index
            print('----- block index', self.current_block, '-----')
            self.current_block_manager.block_frame_counter = 0

            if block_index > 0:
                self.total_recorded_frames += self.current_block_manager.total_block_frames

            while True:

                # Move on to next block if all frames for this one are collected and gpio has executed
                if self.current_block_manager.block_frame_counter == self.current_block_manager.total_block_frames:
                    if self.current_block in self.experiment.track_blocks:
                        if self.current_block_manager.gpio_record.gpio_wait: continue
                    break

                if self.recorded_frame_counter > 37000:
                    return

                # Display stage color
                cv2.imshow('stage', self.current_block_manager.color)
                cv2.waitKey(1)
                cv2.moveWindow('stage', 1920, 0)

        self.hold_record = False
        print('total frames',self.total_recorded_frames)
        return



# cropped_img_dict = split_image(img)
# cropped_img_ls = list(zip(cropped_img_dict.keys(), cropped_img_dict.values()))
# self.experiment.cropped_img_q.put(cropped_img_ls)

# with concurrent.futures.ProcessPoolExecutor() as executor:
#     zf_positions = executor.map(tracking_util.position_track, cropped_img_ls)
#     for position in zf_positions:
#         print(position)

