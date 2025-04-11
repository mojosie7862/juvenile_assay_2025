import cv2
import track
import gpio


class BlockManager():

    def __init__(self, frame_manager, frame_block_dict):
        '''
        A block is a portion of the experiment that features multiple variables in this system:
        - Index: this block's position in the list of blocks to occur in the experiment.
        - Duration: length of time designated for this block to occur.
        - Type:
        -- Acclimate (no recording, tracking, or stimulus)
        -- Baseline (recording and tracking but no stimulus)
        -- Condition (recording, tracking, and stimulus)
        - Color: the color of the display illuminated at the base of the zebrafish well.

        :param frame_manager: experiment frame manager initiated by frame.FrameManager
        :param frame_block_dict:
        '''

        self.frame_manager = frame_manager
        self.index = frame_block_dict['block_index']
        self.block_type = frame_block_dict['block_type']
        self.t_seconds = frame_block_dict['t_seconds']
        self.color = frame_block_dict['block_color']
        self.start_frame = frame_block_dict['frame_start']
        self.stop_frame = frame_block_dict['frame_stop']
        self.block_frame_counter = 0

        if self.block_type == 'condition':
            self.track_record = track.TrackingManager(self)
            self.gpio_record = gpio.GPIOManager(self)

        elif self.block_type == 'baseline':
            self.track_record = track.TrackingManager(self)

        elif self.block_type == 'acclimate':
            self.track_record = track.TrackingManager(self)


    def split_row(col_index, row_index, img):
        x0 = int(528 / 7) * col_index
        x1 = int(528 / 7) * (col_index + 1)
        y0 = int(512 / 2) * row_index
        y1 = int(512 / 2) * (row_index + 1)

        zf_id_img = img[y0:y1, x0:x1]

        return zf_id_img

    def split_image(img):

        id_img_dict = {}
        r0_zf_ids = list(range(1, 8))
        r1_zf_ids = list(range(8, 15))

        for col_index, zf_id in enumerate(r0_zf_ids):
            id_img_dict[zf_id] = split_row(col_index, 0, img)

        for col_index, zf_id in enumerate(r1_zf_ids):
            id_img_dict[zf_id] = split_row(col_index, 1, img)

        return id_img_dict

