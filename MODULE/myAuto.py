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
        self.programName = '계산기'
        self.winHandleList = []
        self.winHandleDict = {}
        self.initAuto()         #   프로그램 실행확인 및 좌표 가져오기

    def run(self):
        while self.isAuto == True:
            pass

    def initAuto(self):     #   프로그램 실행확인 및 좌표 가져오기
        self.isAuto ^= True
        print(pyautogui.size())
        for win in pyautogui.getWindowsWithTitle("계산기"):
            print(win)
            win.activate()
            ff = np.fromfile('./TARGET_IMAGE/COMMON/삼색1.png', np.uint8)
            img = cv2.imdecode(ff, cv2.IMREAD_UNCHANGED)  # img = array

            targetImg = pyautogui.locateCenterOnScreen(img, region=(win.left, win.top, win.width, win.height))  # 이미지가 있는 위치를 가져옵니다.
            pyautogui.moveTo(targetImg)

        # for win in self.myWin32API.getWindowList():
        #     if (win[0] == self.programName):
        #         self.winHandleList.append(win[1])
        #         self.autoLog.emit('프로그램 : %s, 프로그램 핸들 : %d' % (self.programName, win[1]))
        #         self.autoLog.emit('프로그램 좌표 : ' + str(self.myWin32API.getWindowRect(win[1])))
        #         print(self.winHandleList)



    def click(self):
        pass

    def searchImage(self):
        pass