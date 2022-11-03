import win32api
import win32gui
import numpy as np
import cv2
import pyautogui
import time

from PIL import ImageGrab
from functools import partial

ESC_KEY = 27
FRAME_RATE = 1
SLEEP_TIME = 1/FRAME_RATE

from PyQt5.QtCore import *

ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

X_POS = 1920

class myOpenCV(QThread):
    searchPos = pyqtSignal(tuple)  # 찾은 이미지 x, y 좌표

    def __init__(self):
        QThread.__init__(self)
        self.window_name = "Gersang"
        self.wait_time = 1 / FRAME_RATE
        self.programX = 0
        self.programY = 0

        self.methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

    def run(self):
        while True:
            start = time.time()

            captureImg = self.screenshot()  # 캡쳐된 이미지
            self.searchImage(captureImg, "None")

            #cv2.imshow("capture", captureImg)  # 캡쳐된 이미지 띄우기

            delta = time.time() - start

            if delta < SLEEP_TIME:
                time.sleep(SLEEP_TIME - delta)

            key = cv2.waitKey(1) & 0xFF
            if key == ESC_KEY:
                break
    def screenshot(self):
        hwnd = win32gui.FindWindow(None, self.window_name)

        if not hwnd:
            raise Exception('Window not found: ' + self.window_name)


        left, top, right, bot = win32gui.GetClientRect(hwnd)
        x, y = win32gui.ClientToScreen(hwnd, (left, top))
        #print(x, y, *win32gui.ClientToScreen(hwnd, (right-x, bot-y)))

        self.programX = x
        self.programY = y

        return cv2.cvtColor(np.asarray(pyautogui.screenshot(region=(x+X_POS, y, *win32gui.ClientToScreen(hwnd, (right - x, bot - y))))), cv2.COLOR_RGB2BGR)
        #return cv2.cvtColor(np.asarray(pyautogui.screenshot(region=(x, y, *win32gui.ClientToScreen(hwnd, (right - x, bot - y))))), cv2.COLOR_RGB2BGR)

    def searchImage(self, img_src, img_template):
        image = img_src
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)    #   흑백으로 변환

        #ff = np.fromfile('./IMAGE/흑룡담/전투입장.bmp', np.uint8)
        #template = cv2.imdecode(ff, cv2.COLOR_BGR2GRAY)  # img = array
        # w, h = template.shape[:-1]
        #result = cv2.matchTemplate(image_gray, template[1], cv2.TM_SQDIFF_NORMED)

        template = cv2.imread('IMAGE/11.bmp', 0)
        w, h = template.shape[::-1]

        result = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)

        threshold = 0.9 # 임계치 설정
        box_loc = np.where(result >= threshold) # 임계치 이상의 값들만 사용

        for box in zip(*box_loc[::-1]):
            startX, startY = box
            endX, endY = startX + w, startY + h
            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
            searchImagePos = (int((startX + endX)/2) + self.programX, int((startY + endY)/2) + self.programY)
            self.searchPos.emit(searchImagePos)
    def gaussianBlur(self, img):
        image_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 흑백으로 변환
        return cv2.GaussianBlur(image_gray, (5, 5), 0)




# image = cv2.imread('image/1.bmp')
# image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# template = cv2.imread('image/2.bmp', 0)
# w, h = template.shape[::-1]
#
# result = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)
# threshold = 0.95 # 임계치 설정
# box_loc = np.where(result >= threshold) # 임계치 이상의 값들만 사용
#
# for box in zip(*box_loc[::-1]):
#     startX, startY = box
#     endX, endY = startX + w, startY + h
#     cv2.rectangle(image, (startX, startY), (endX, endY), (0,0,255), 1)
#
# cv2.imwrite('result.png', image)

