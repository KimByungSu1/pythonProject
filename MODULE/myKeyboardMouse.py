import enum

import keyboard

from pynput import *

from PyQt5.QtCore import *

from PyQt5.QtCore import Qt

class arduinoKeyCode(enum.Enum):    #   아두이노 레오나르도 키코드값
    ctrl_l = 0x80
    shift_l = enum.auto()
    alt_l = enum.auto()
    cmd_l = enum.auto()
    ctrl_r = enum.auto()
    shift_r = enum.auto()
    alt_r = enum.auto()
    cmd_r = enum.auto()

    right = 0xD7
    left = enum.auto()
    down = enum.auto()
    up = enum.auto()

    enter = 0xB0
    esc = enum.auto()
    backspace = enum.auto()
    tab = enum.auto()

    insert = 0xD1
    home = enum.auto()
    page_up = enum.auto()
    delete = enum.auto()
    end = enum.auto()
    page_down = enum.auto()

    caps_lock = 0xC1
    f1 = enum.auto()
    f2 = enum.auto()
    f3 = enum.auto()
    f4 = enum.auto()
    f5 = enum.auto()
    f6 = enum.auto()
    f7 = enum.auto()
    f8 = enum.auto()
    f9 = enum.auto()
    f10 = enum.auto()
    f11 = enum.auto()
    f12 = enum.auto()

class myKeyboardMouse(QThread):
    keyLog = pyqtSignal(str)  # 시리얼 이벤트 시그널

    def __init__(self):
        QThread.__init__(self)
        self.isKey = False          #   쓰레드 동작 여부
        self.prePressKey = None     #   이전 press 확인
        self.preReleaseKey = None   #   이전 release 확인
        self.recordKey = []         #   키입력 순서 기록
        self.leftCtrl = False       #   왼쪽 컨트롤키 눌림 확인용
        

    def run(self):
        self.recordKey.clear()
        while self.isKey == True:
            # Collect events until released
            with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                listener.join()

    def on_press(self, key):
        if self.prePressKey != key: #   이전 키눌림 상태와 비교해서 다르다면
            self.prePressKey = key
            self.preReleaseKey = None

            try:
                if self.leftCtrl:
                    if key.char == None:    #   컨트롤 + '`' ~ '=' 조합키 누를시
                        returnKey = chr(int(str(key)[1:-1]))
                    else:
                        returnKey = chr(ord(key.char) + 96)
                else:
                    returnKey = key.char

                self.keyLog.emit("{0} 눌림".format(returnKey))
                self.recordKey.append(returnKey)

            except AttributeError:
                if key == keyboard.Key.ctrl_l:  # left 컨트롤키 눌림
                    self.leftCtrl = True

                for x in arduinoKeyCode:
                    if key.name in x.name:
                        self.keyLog.emit("{0} 눌림".format(key.name))
                        self.recordKey.append(x.value)
                        break

    def on_release(self, key):
        if self.preReleaseKey != key:   #   이전 release 상태와 비교해서 다르다면
            self.preReleaseKey = key
            self.prePressKey = None

            try:
                if self.leftCtrl:
                    if key.char == None:    #   컨트롤 + '`' ~ '=' 조합키 누를시
                        returnKey = chr(int(str(key)[1:-1]))
                    else:
                        returnKey = chr(ord(key.char) + 96)
                else:
                    returnKey = key.char

                self.keyLog.emit("{0} 떼기".format(returnKey))
                self.recordKey.append(returnKey)

            except AttributeError:
                if key == keyboard.Key.ctrl_l:  # left 컨트롤키 눌림
                    self.leftCtrl = False

                for x in arduinoKeyCode:
                    if key.name in x.name:
                        self.keyLog.emit("{0} 떼기".format(key.name))
                        self.recordKey.append(x.value)
                        break

            if key == keyboard.Key.f11:  # f11키 감지시 record 종료
                print(self.recordKey)
                self.isKey = False
                return False