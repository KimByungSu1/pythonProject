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
        self.winDict = {}

        self.initAuto()         #   프로그램 실행확인 및 좌표 가져오기

    def run(self):
        while self.isAuto == True:
            pass

    def initAuto(self):     #   프로그램 실행확인 및 좌표 가져오기
        self.getProgramInfo()
        print(imgFolderList())
        self.searchImage()

    def getProgramInfo(self):
        self.winDict.clear()
        for idx, win in enumerate(pyautogui.getWindowsWithTitle(self.programName)):
            self.winDict[idx] = []
            self.winDict[idx].append(win.title)
            self.winDict[idx].append(win._hWnd)
            self.winDict[idx].append(win.left)
            self.winDict[idx].append(win.top)
            self.winDict[idx].append(win.width)
            self.winDict[idx].append(win.height)

    def click(self):
        pass

    def searchImage(self):
        for win in self.winDict.values():
            ff = np.fromfile('./TARGET_IMAGE/COMMON/삼색1.png', np.uint8)
            img = cv2.imdecode(ff, cv2.IMREAD_UNCHANGED)  # img = array
            targetImg = pyautogui.locateCenterOnScreen(img, region=(win[2], win[3], win[4], win[5]))  # 이미지가 있는 위치를 가져옵니다.
            pyautogui.moveTo(targetImg)

        # for win in pyautogui.getWindowsWithTitle(self.programName):
        #     ff = np.fromfile('./TARGET_IMAGE/COMMON/로그인/거상_로그인_동의.png', np.uint8)
        #     img = cv2.imdecode(ff, cv2.IMREAD_UNCHANGED)  # img = array
        #
        #     targetImg = pyautogui.locateCenterOnScreen(img, region=(win.left, win.top, win.width, win.height))  # 이미지가 있는 위치를 가져옵니다.
        #     pyautogui.moveTo(targetImg)
