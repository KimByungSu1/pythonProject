import win32api, binascii
import win32gui
import numpy as np
import cv2, os, glob
import pyautogui
import time
import pywinauto
import pygetwindow as gw

from playsound import playsound
from PIL import ImageGrab
from functools import partial

from PyQt5.QtCore import *

ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

class myOpenCV(QThread):
    def __init__(self):
        QThread.__init__(self)
        pass

    def getProgramPos(self, handle):      # 프로그램 좌표 확인
        left, top, right, bot = win32gui.GetClientRect(handle)
        x, y = win32gui.ClientToScreen(handle, (left, top))
        return x, y, right, bot

    def screenCapture(self, pos):
        return cv2.cvtColor(np.asarray(pyautogui.screenshot(region=pos)), cv2.COLOR_RGB2BGR)

    def captureImgAndShow(self, pos):
        cv2.imshow("captureImg", cv2.cvtColor(np.asarray(pyautogui.screenshot(region=pos)), cv2.COLOR_RGB2BGR))
        key = cv2.waitKey()


    def set_foreground(self, handle):
        """put the window in the foreground"""
        pyautogui.press("alt")
        win32gui.SetForegroundWindow(handle)

    def run(self):
        while True:
            pass

    def searchImage(self, pos, img_src, img_template):
        image = img_src
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)    #   흑백으로 변환
        template = cv2.imread(img_template, 0)
        w, h = template.shape[::-1]
        result = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)

        # 임계치로 찾는법
        threshold = 0.9 # 임계치 설정
        box_loc = np.where(result >= threshold) # 임계치 이상의 값들만 사용

        for box in zip(*box_loc[::-1]):     #   이미지 비교 일치한 데이터 빨간 사각형 테두리 전부 그리기
            startX, startY = box
            endX, endY = startX + w, startY + h
            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)    #   발견된 이미지 빨간 사각형 테두리 그리기
            searchImagePos = int((startX + endX)/2) + pos[0], int((startY + endY)/2) + pos[1]   #   발견된 이미지 가운데 좌표 가져오기
            return searchImagePos #   이미지 가운데 좌표 리턴, 발견된 이미지 없으면 None 리턴

    def gaussianBlur(self, img):
        image_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 흑백으로 변환
        return cv2.GaussianBlur(image_gray, (5, 5), 0)
