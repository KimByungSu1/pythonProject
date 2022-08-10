import pyautogui, cv2
import numpy as np

from PyQt5.QtCore import *

from MODULE.myWin32API import *    #   user Win32 API

class myAuto(QThread):
    autoLog = pyqtSignal(str)  # 이벤트 시그널

    def __init__(self):
        QThread.__init__(self)
        self.isAuto = False
        self.myWin32API = myWin32API()
        self.programName = 'Gersang'
        self.winHandleList = []
        self.winHandleDict = {}
        self.initAuto()         #   프로그램 실행확인 및 좌표 가져오기

    def run(self):
        while self.isAuto == True:
            pass

    def initAuto(self):     #   프로그램 실행확인 및 좌표 가져오기
        pass


    def click(self):
        pass

    def searchImage(self):
        for win in pyautogui.getWindowsWithTitle(self.programName):
            ff = np.fromfile('./TARGET_IMAGE/COMMON/로그인/거상_로그인_동의.png', np.uint8)
            img = cv2.imdecode(ff, cv2.IMREAD_UNCHANGED)  # img = array

            targetImg = pyautogui.locateCenterOnScreen(img, region=(win.left, win.top, win.width, win.height))  # 이미지가 있는 위치를 가져옵니다.
            pyautogui.moveTo(targetImg)
