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

    def run(self):
        while self.isAuto == True:
            pass

    def initAuto(self):     #   오토 시작전 거상 실행중인지 확인하기
        for win in self.myWin32API.getWindowList():
            if (win[0] == self.programName):
                self.winHandleList.append(win[1])
                self.autoLog.emit('%s : %d' % (self.programName, win[1]))

        if len(self.winHandleList):
            self.autoLog.emit('%s %d개 실행중입니다' %(self.programName, len(self.winHandleList)))
        else:
            self.autoLog.emit('%s 실행중이지 않습니다.' %(self.programName))

        # ff = np.fromfile('./TARGET_IMAGE/COMMON/삼색.png', np.uint8)
        # img = cv2.imdecode(ff, cv2.IMREAD_UNCHANGED)  # img = array
        #
        # x, y = pyautogui.locateCenterOnScreen(img, confidence=0.7)  # 이미지가 있는 위치를 가져옵니다.
        # pyautogui.moveTo(x, y)
        pass