from numpy.lib.utils import source
from skimage.measure import label, regionprops
from skimage.morphology import remove_small_objects
import numpy as np
import win32gui
import sys
import time
import threading
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


class ImageEventHandler(PySpin.ImageEventHandler):

    def __init__(self, cam, handle_q):

        # delegates method to parent class
        super().__init__()

        nodemap = cam.GetTLDeviceNodeMap()

        # Retrieve device serial number
        node_device_serial_number = PySpin.CStringPtr(nodemap.GetNode('DeviceSerialNumber'))

        if PySpin.IsReadable(node_device_serial_number):
            self._device_serial_number = node_device_serial_number.GetValue()

        # Initialize image counter to 0
        self._image_count = 0
        self.handle_q = handle_q
        self.time_ls = []
        self.continue_recording = True

        # Release reference to camera
        # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
        # cleaned up when going out of scope.
        # The usage of del is preferred to assigning the variable to None.
        del cam

        # Create ImageProcessor instance for post processing images
        self._processor = PySpin.ImageProcessor()

        # Set default image processor color processing method
        #
        # *** NOTES ***
        # By default, if no specific color processing algorithm is set, the image
        # processor will default to NEAREST_NEIGHBOR method.
        self._processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)

    def OnImageEvent(self, image):
        """
        This method defines an image event. In it, the image that triggered the
        event is converted and saved before incrementing the count. Please see
        Acquisition example for more in-depth comments on the acquisition
        of images.

        :param image: Image from event.
        :type image: ImagePtr
        :rtype: None
        """
        if self.continue_recording:

            if image.IsIncomplete():
                print('Image incomplete with image status %i...' % image.GetImageStatus())

            else:
                # global bg_init_done
                # if bg_init_done:
                # Convert to ND array
                image_converted = self._processor.Convert(image, PySpin.PixelFormat_Mono8)
                array = image_converted.GetData()
                t_put = time.time()
                self.time_ls.append(t_put)
                self.handle_q.put((t_put, array))

                # Increment image counter
                self._image_count += 1
        else:
            return


class ExperimentManager():

    def __init__(self, exp_id, fps_dict):
        '''
        :param exp_id: str
        :param fps_dict: dict with 'fps_record', 'fps_bg_acq', 'fps_track', 'fps_gpio'
        '''

        self.fps_record = fps_dict['fps_record']
        self.social_block = [2]
        self.total_recorded_frames = None

        if 'fps_bg_acq' in fps_dict.keys():
            self.fps_bg_acq = fps_dict['fps_bg_acq']
            self.bg_frame_skip = self.fps_record/self.fps_bg_acq

        if 'fps_track' in fps_dict.keys():
            self.fps_track = fps_dict['fps_track']
            self.track_frame_skip = self.fps_record/self.fps_track

        if 'fps_gpio' in fps_dict.keys():
            self.fps_gpio = fps_dict['fps_gpio']


        self.fourcc = 'MJPG'
        self.frameSize = (528, 512) # VideoWriter frame dimensions are flipped (width, height)
        self.video_filename = str(exp_id) + ".avi"
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps_record, self.frameSize, False)
        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        self.num_cams = self.cam_list.GetSize()
        self.SLEEP_DURATION = 1 / self.fps_record
        self.img_q = queue.Queue(maxsize=1)
        self.ts_start = time.time()

        self.image_event_handler = ImageEventHandler(self.cam_list[0], self.img_q)
        self.continue_recording = self.image_event_handler.continue_recording

    def wait_for_images(self):
        """
        This function waits for the appropriate amount of images.  Notice that
        whereas most examples actively retrieve images, the acquisition of images is
        handled passively in this example.

        :param image_event_handler: Image event handler.
        :type image_event_handler: ImageEventHandler
        :return: True if successful, False otherwise.
        :rtype: bool
        """

        try:
            result = True

            #  Wait for images

            #  *** NOTES ***
            #  In order to passively capture images using image event handlers and
            #  automatic polling, the main thread sleeps in increments of SLEEP_DURATION ms
            #  until _MAX_IMAGES images have been acquired and saved.
            while self.image_event_handler.continue_recording:
                time.sleep(self.SLEEP_DURATION)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result

    def reset_image_events(self, cam):
        """
        This functions resets the example by unregistering the image event handler.

        :param cam: Camera instance.
        :param image_event_handler: Image event handler for cam.
        :type cam: CameraPtr
        :type image_event_handler: ImageEventHandler
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        try:

            result = True

            #  Unregister image event handler
            #
            #  *** NOTES ***
            #  It is important to unregister all image events from all cameras they are registered to.
            #  Unlike SystemEventHandler and InterfaceEventHandler in the EnumerationEvents example,
            #  there is no need to explicitly delete the ImageEventHandler here as it does not store
            #  an instance of the camera (it gets deleted in the constructor already).
            cam.UnregisterEventHandler(self.image_event_handler)
            for i, t in enumerate(self.image_event_handler.time_ls):
                if i > 0:
                    diff = t - self.image_event_handler.time_ls[i - 1]
                    # print(i, diff)

            print('Processed image count:', self.image_event_handler._image_count)
            print('Image events unregistered...')

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result

    def acquire_images(self, cam, nodemap):
        """
        This function passively waits for images by calling wait_for_images(). Notice that
        this function is much shorter than the acquire_images() function of other examples.
        This is because most of the code has been moved to the image event's OnImageEvent()
        method.

        :param cam: Camera instance to grab images from.
        :param nodemap: Device nodemap.
        :param image_event_handler: Image event handler.
        :type cam: CameraPtr
        :type nodemap: INodeMap
        :type image_event_handler: ImageEventHandler
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        # print('*** IMAGE ACQUISITION ***\n')
        try:
            result = True

            # Set acquisition mode to continuous
            node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
            if not PySpin.IsReadable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
                print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
                return False

            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
            if not PySpin.IsReadable(node_acquisition_mode_continuous):
                print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
                return False

            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

            # Begin acquiring images
            cam.BeginAcquisition()

            # Retrieve images using image event handler
            self.wait_for_images()

            cam.EndAcquisition()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result

    def configure_image_events(self, cam):
        """
        This function configures the example to execute image events by preparing and
        registering an image event.

        :param cam: Camera instance to configure image event.
        :return: tuple(result, image_event_handler)
            WHERE
            result is True if successful, False otherwise
            image_event_handler is the event handler
        :rtype: (bool, ImageEventHandler)
        """
        try:
            result = True
            #  Create image event handler
            #
            #  *** NOTES ***
            #  The class has been constructed to accept a camera pointer in order
            #  to allow the saving of images with the device serial number.
            #  image_event_handler = ImageEventHandler(cam, self.img_q)
            #  Register image event handler
            #
            #  *** NOTES ***
            #  Image events are registered to cameras. If there are multiple
            #  cameras, each camera must have the image events registered to it
            #  separately. Also, multiple image events may be registered to a
            #  single camera.
            #
            #  *** LATER ***
            #  Image event handlers must be unregistered manually. This must be done prior
            #  to releasing the system and while the image events are still in
            #  scope.
            cam.RegisterEventHandler(self.image_event_handler)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result

    def run_single_camera(self, cam):
        """
        This function acts as the body of the example; please see NodeMapInfo example
        for more in-depth comments on setting up cameras.

        :param cam: Camera to acquire images from.
        :type cam: CameraPtr
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        try:
            result = True

            # Initialize camera
            cam.Init()

            # Retrieve GenICam nodemap
            nodemap = cam.GetNodeMap()

            node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
            if not PySpin.IsReadable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
                print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
                return False

            # Configure image events
            err = self.configure_image_events(cam)
            if not err:
                return err

            # Acquire images using the image event handler
            result &= self.acquire_images(cam, nodemap)

            # Reset image event handlers
            result &= self.reset_image_events(cam)

            # Deinitialize camera
            cam.DeInit()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result

    def open_camera(self):
        for cam in self.cam_list:
            self.run_single_camera(cam)


