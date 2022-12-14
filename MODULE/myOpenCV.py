import pytesseract
import win32api, binascii, datetime
import win32gui
import numpy as np
import cv2, os, glob
import pyautogui
import time
import pywinauto
import pygetwindow as gw

from PIL import ImageGrab
from functools import partial
from pytesseract import *

from PyQt5.QtCore import *

ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

class myOpenCV(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.window_name = "Gersang"        #   1024, 768 사이즈

        hwnd = win32gui.FindWindow(None, self.window_name)
        if not hwnd:
            raise Exception('Window not found: ' + self.window_name)

        self.handle = hwnd
        self.ratio = 0.7 #  프로그램 크기 비율

    def getProgramPos(self, handle):      # 프로그램 원본
        left, top, right, bot = win32gui.GetClientRect(handle)
        x, y = win32gui.ClientToScreen(handle, (left, top))
        pos = x, y, right, bot
        return pos

    def getProgramCenterPos(self, handle):      # 프로그램 일정비율로 캡쳐
        left, top, right, bot = win32gui.GetClientRect(handle)
        x, y = win32gui.ClientToScreen(handle, (left, top))
        resizeX = x + (right - int(right*self.ratio))
        resizeY = y + (bot - int(bot*self.ratio))

        rightRatio = right - int(right*self.ratio)
        botRatio = bot - int(bot*self.ratio)
        resizeRight = right - rightRatio*2
        resizeBot = bot - botRatio*2

        pos = resizeX, resizeY, resizeRight, resizeBot
        return pos

    def getleftTopPos(self, handle):      # 왼쪽 상단
        left, top, right, bot = win32gui.GetClientRect(handle)
        x, y = win32gui.ClientToScreen(handle, (left, top))

        resizeRight = int(right/2)
        resizeBot = int(bot/2)
        pos = x, y, resizeRight, resizeBot
        return pos

    def getleftDownPos(self, handle):      # 왼쪽 하단
        left, top, right, bot = win32gui.GetClientRect(handle)
        x, y = win32gui.ClientToScreen(handle, (left, top))

        resizeRight = int(right/2)
        resizeY = y + int(bot/2)
        resizeBot = int(bot/2)
        pos = x, resizeY, resizeRight, resizeBot
        return pos
    
    def getRightTopPos(self, handle):      # 오른쪽 상단
        left, top, right, bot = win32gui.GetClientRect(handle)
        x, y = win32gui.ClientToScreen(handle, (left, top))
        resizeX = x + int(right/2)
        resizeY = y
        resizeRight = int(right/2)
        resizeBot = int(bot/2)
        pos = resizeX, resizeY, resizeRight, resizeBot
        return pos

    def getRightDownPos(self, handle):      # 오른쪽 하단
        left, top, right, bot = win32gui.GetClientRect(handle)
        x, y = win32gui.ClientToScreen(handle, (left, top))
        resizeX = x + int(right/2)
        resizeY = y + int(bot/2)
        resizeRight = int(right/2)
        resizeBot = int(bot/2)
        pos = resizeX, resizeY, resizeRight, resizeBot
        return pos
    
    def screenCapture(self, pos):      
        return cv2.cvtColor(np.asarray(pyautogui.screenshot(region=pos)), cv2.COLOR_RGB2BGR)

    def BgrToRgb(self, src):
        return cv2.cvtColor(src, cv2.COLOR_BGR2RGB)

    def BgrToGray(self, src):
        return cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    def captureImgAndShow(self, pos):
        cv2.imshow("captureImg", cv2.cvtColor(np.asarray(pyautogui.screenshot(region=pos)), cv2.COLOR_RGB2BGR))
        key = cv2.waitKey(1)

    def run(self):
        while True:
            pass
            #self.colorCompare()
            #frame = self.screenCapture(self.getProgramPos(self.handle))
            #frame = self.screenCapture(self.getProgramCenterPos(self.handle))
            #cv2.imshow('frame', frame)
            #text = pytesseract.image_to_string(self.BgrToRgb(frame), config='--psm 6')
            #print(text)
            #key = cv2.waitKey(1)

    def searchColorImage(self, pos, img_src, img_template):
        threshold = 0.8
        image = cv2.cvtColor(img_src, cv2.COLOR_BGR2RGB)    #   RGB로 변환
        template = cv2.imread(img_template, cv2.IMREAD_COLOR)
        template_rgb = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)    #   RGB로 변환

        ##Split Both into each R, G, B Channel
        imageMainR, imageMainG, imageMainB = cv2.split(image)
        imageNeedleR, imageNeedleG, imageNeedleB = cv2.split(template_rgb)

        ##Matching each channel
        resultB = cv2.matchTemplate(imageMainR, imageNeedleR, cv2.TM_SQDIFF)
        resultG = cv2.matchTemplate(imageMainG, imageNeedleG, cv2.TM_SQDIFF)
        resultR = cv2.matchTemplate(imageMainB, imageNeedleB, cv2.TM_SQDIFF)

        print(resultB, resultG, resultR)

        ##Add together to get the total score
        result = resultB + resultG + resultR
        loc = np.where(result >= 3 * threshold)
        for x in zip(*loc[::-1]):
            return x


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


    def edge_laplacian(self):
        path = glob.glob(r'.\IMAGE\BATTLE\DRAGON\*.bmp')  # 전투 맵 이미지 반복 확인

        for x in path:
            img = cv2.imread(x)

            # 라플라시안 필터 적용 ---①
            edge = cv2.Laplacian(img, -1)

            # 결과 출력
            merged = np.hstack((img, edge))
            cv2.imshow('Laplacian', merged)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def edge_canny(self):
        path = glob.glob(r'.\IMAGE\BATTLE\DRAGON\*.bmp')  # 전투 맵 이미지 반복 확인

        for x in path:
            img = cv2.imread(x)
            # 케니 엣지 적용
            edges = cv2.Canny(img, 100, 200)

            # 결과 출력
            cv2.imshow('Original', img)
            cv2.imshow('Canny', edges)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def saveImg(self, Img):
        Time = datetime.datetime.now().strftime('%H:%M:%S')
        cv2.imwrite('{0}.jpg'.format(Time), Img)


    def testCvtImg(self):
        path = glob.glob(r'.\IMAGE\BATTLE\DRAGON\*.bmp')  # 전투 맵 이미지 반복 확인

        for x in path:
            img = cv2.imread(x)

            # Conversion to CMYK (just the K channel):

            # Convert to float and divide by 255:
            dst = cv2.inRange(img, (0, 0, 0), (150, 150, 150))


            # 결과 출력
            cv2.imshow('Original', img)
            cv2.imshow('Canny', dst)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

