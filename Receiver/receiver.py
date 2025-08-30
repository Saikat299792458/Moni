# This program should be able to decode arbitrary number of similar bit sequence.
# for that thickness of the strips must be very large compared to shutter loss
# Todo: Check for possible memory overflow for queue operation
import cv2
from queue import Queue
from time import sleep
import numpy as np
import warnings

class receiver:
    def __init__(self, callback) -> None:
        self.callback = callback
        self.stream = ""
        self.q = Queue()
        self.flag = False
        self.counter = 0
        self.data = None # Frame containing information
        self.width = 30
        self.shutter_loss = 15 # Pixel loss due to frame transitioning
        self.frame_width = 640
        self.frame_height = 480
    
    def count_decimal_digits(self, number):
        # Convert the floating-point number to a string
        number_str = str(number)

        # Check if there is a decimal point in the string
        if '.' in number_str:
            # Find the index of the decimal point
            decimal_index = number_str.index('.')

            # Count the number of digits after the decimal point
            decimal_digits = len(number_str) - decimal_index - 1

            return decimal_digits
        else:
            # If there is no decimal point, return 0
            return 0
    

    def isStriped(self, gray_image, brightness_threshold = 110) -> bool:
        "Check if a frame is striped"
        # Apply Canny edge detection
        edges = cv2.Canny(gray_image, threshold1=100, threshold2=400) # Calibrate here
        #cv2.imshow("Frame", edges)
        # For instance, you can calculate the average pixel intensity of bright and dark areas
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            average_bright = gray_image[edges > 0].mean()
            #average_dark = gray_image[edges == 0].mean()
            #print(average_bright)

        ## Condition to declare: May be changed
        #print(average_bright)
        if np.isnan(average_bright):
                return False
        if average_bright < brightness_threshold:
        #if self.count_decimal_digits(average_bright) > 10: # I don't know why the fuck, okay?
            return True
        return False
    

    def transfer(self, h, type) -> None:
        "Converts height to number of bits"
        # Reduce the effective shutter loss value
        no = round(h / self.width)
        if not no:
            no = 1
        self.stream += type*no
        

    def convert(self) -> None:
        "Retrieves Binary data from B&W image"
        # Apply binary threshold to segment black strips
        _, binary_image = cv2.threshold(self.data, 50, 250, cv2.THRESH_BINARY_INV) # Calibrate here
        # Find contours in the binary image
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        init = None
        for contour in reversed(contours):
            x, y, w, h = cv2.boundingRect(contour)
            if init:
                white_width = y - init
                if self.data.shape[0] // init != self.data.shape[0] // y:
                    white_width += self.shutter_loss # at the end of 1 frame
                self.transfer(white_width, "1")
            init = y + h
            if y:
                if self.data.shape[0] // y != self.data.shape[0] // init:
                    h += self.shutter_loss
            self.transfer(h, "0")
        #print("")
    
    
    def parallel(self) -> None:
        "Executes processing operations in parallel"
        ROI_left = self.frame_width // 2 - 25
        ROI_right = self.frame_width // 2 + 25
        while True:
            try:
                frame = self.q.get(block=False)
            except:
                if self.flag:
                    print(self.counter)
                    return
                else:
                    sleep(0.05) # Adjust
                    continue
            frame = cv2.resize(frame, (self.frame_width, self.frame_height)) # Resize
            frame = frame[:, ROI_left : ROI_right] # ROI Cropping
            # Convert the image to grayscale
            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if self.isStriped(gray_image):
                cv2.imwrite(f"Frames/{self.counter}.jpg", gray_image)
                self.counter += 1
                if self.data is None:
                    self.data = gray_image
                else:
                    self.data = cv2.vconcat([self.data, gray_image])
            else:
                if self.data is not None:
                    #print(self.q.qsize())
                    self.convert()
                    #print(self.q.qsize())
                    self.data = None
                    self.callback(self.stream)
                    self.stream = ""
       
