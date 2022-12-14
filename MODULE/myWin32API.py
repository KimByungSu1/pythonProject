import win32con
import win32gui

from PyQt5.QtCore import *

class myWin32API(QThread):

    win32ApiLog = pyqtSignal(str)  # 이벤트 시그널

    def __init__(self):
        QThread.__init__(self)

    def run(self):
        pass

    def getWindowList(self):
        def callback(hwnd, hwnd_list: list):
            title = win32gui.GetWindowText(hwnd)
            if win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd) and title:
                hwnd_list.append((title, hwnd))
            return True
        output = []
        win32gui.EnumWindows(callback, output)
        return output                               #   윈도우타이틀, 윈도우 핸들 튜플 형식으로 반환  ex (Gersang, 62231)

    def getWindowRect(self, winHandle):             #   윈도우 핸들 사각 좌표 가져오기
        left, top, right, bot = win32gui.GetClientRect(winHandle)
        x, y = win32gui.ClientToScreen(winHandle, (left, top))
        return x, y, right, bot
