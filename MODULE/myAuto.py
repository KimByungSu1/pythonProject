import time

import pyautogui, cv2
import numpy as np
import pywinauto

from PyQt5.QtCore import *

from PIL import ImageGrab
from functools import partial

from MODULE.myWin32API import *    #   user Win32 API
from MODULE.myFile import *    #   user File System


ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

class myAuto(QThread):
    autoLog = pyqtSignal(str)  # 이벤트 시그널

    def __init__(self):
        QThread.__init__(self)
        self.isAuto = False
        self.myWin32API = myWin32API()
        self.programName = '계산기'
        self.winDict = {}       #   프로그램 관련 변수
        self.imageDict = imgFolderList()    #   찾을 이미지 불러오기
        self.initAuto()         #   프로그램 실행확인 및 좌표 가져오기

    def run(self):
        self.isAuto = True
        self.autoLog.emit("Auto Start")
        while self.isAuto == True:
            self.searchImage()
            pass

    def initAuto(self):     #   프로그램 실행확인 및 좌표 가져오기
        self.getProgramInfo()


    def getProgramInfo(self):
        self.winDict.clear()
        for idx, win in enumerate(pyautogui.getWindowsWithTitle(self.programName)):
            self.winDict[idx] = []
            self.winDict[idx].append(win.title) #   프로그램 이름
            self.winDict[idx].append(win._hWnd) #   프로그램 핸들
            self.winDict[idx].append(win.left)  #   프로그램 left
            self.winDict[idx].append(win.top)   #   프로그램 top
            self.winDict[idx].append(win.width) #   프로그램 width
            self.winDict[idx].append(win.height)    #   프로그램 height


    def searchImage(self):
        # start = time.time()
        for win in self.winDict.values():
            for x in self.imageDict.values():
                for j in x:
                    ff = np.fromfile(j, np.uint8)
                    img = cv2.imdecode(ff, cv2.IMREAD_UNCHANGED)  # img = array
                    targetImg = pyautogui.locateCenterOnScreen(img, region=(win[2], win[3], win[4], win[5]))  # 이미지가 있는 위치를 가져옵니다.

                    if targetImg != None:
                        self.autoLog.emit("Image Found : {0}".format(targetImg))    #   이미지 찾음
                        # pyautogui.moveTo(targetImg) #   이미지 발견시 해당 이미지로 이동

        # print(time.time() - start)

        # for win in pyautogui.getWindowsWithTitle(self.programName):
        #     ff = np.fromfile('./TARGET_IMAGE/COMMON/로그인/거상_로그인_동의.png', np.uint8)
        #     img = cv2.imdecode(ff, cv2.IMREAD_UNCHANGED)  # img = array
        #
        #     targetImg = pyautogui.locateCenterOnScreen(img, region=(win.left, win.top, win.width, win.height))  # 이미지가 있는 위치를 가져옵니다.
        #     pyautogui.moveTo(targetImg)
