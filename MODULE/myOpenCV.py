import win32api
import win32gui
import numpy as np
import cv2, os, glob
import pyautogui
import time

from playsound import playsound
from PIL import ImageGrab
from functools import partial

ESC_KEY = 27
FRAME_RATE = 1
SLEEP_TIME = 1/FRAME_RATE

from PyQt5.QtCore import *

ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

X_POS = 1920

class myOpenCV(QThread):
    searchPos = pyqtSignal(list)  # 찾은 이미지 x, y 좌표
    returnKey = pyqtSignal(list)  # 키보드 리턴
    searchImgLog = pyqtSignal(str)  # 찾은 이미지 파일

    def __init__(self):
        QThread.__init__(self)
        self.searchProgramName = "Gersang"      #   프로그램 이름
        self.searchProgramHandle = []           #   프로그램 핸들
        self.searchProgramPos = {}              #   프로그램 좌표

        self.templateBattle = {}                # 전투 템플릿 이미지
        self.templatehome = {}                  # 홈 템플릿 이미지
        
        self.wait_time = 1 / FRAME_RATE         #   서치 시간
        
        self.state = 0   #   현재 단계 확인

        self.battleSuccess = {}
        self.totalBattle = {}

        self.methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
        self.getWindowList()
        self.searchTemplateFolder()

        self.delay = 0.3

        for i in self.searchProgramHandle:  #   프로그램별 전투카운트 계산
            self.battleSuccess[i] = 0  #   정상적으로 전투 완료 한 횟수
            self.totalBattle[i] = 0  # 총 전투 완료 횟수



    def userInit(self, XPos, accuracy):
        self.X_POS = XPos
        self.imgAccuracy = accuracy

    def getWindowList(self):
        def callback(hwnd, hwnd_list: list):
            title = win32gui.GetWindowText(hwnd)
            if win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd) and title:
                hwnd_list.append((title, hwnd))
                if title == self.searchProgramName:
                    self.searchProgramHandle.append(hwnd)
            return True

        output = []
        win32gui.EnumWindows(callback, output)
        return output

    def getSearchProgramPos(self):      # 프로그램 좌표 확인
        for i in self.searchProgramHandle:
            left, top, right, bot = win32gui.GetClientRect(i)
            x, y = win32gui.ClientToScreen(i, (left, top))
            self.searchProgramPos[i] = x + self.X_POS, y, right, bot

    def searchTemplateFolder(self):      # 이미지 템플릿 폴더 경로
        if self.state == 0: # 대기화면
            path = r'.\IMAGE\HOME\*.bmp'
        elif self.state == 1: # 경고 화면
            path = r'.\IMAGE\WARNING\*.bmp'
        elif self.state == 2: # 전투 입장 확인
            path = r'.\IMAGE\BATTLE\BLACK_DRAGON_MAP\*.bmp'
        
        file_list = glob.glob(path)  ## 폴더 안에 있는 모든 파일 출력
        return file_list

    def screenshot(self, pos):
        return cv2.cvtColor(np.asarray(pyautogui.screenshot(region=pos)), cv2.COLOR_RGB2BGR)

    def run(self):
        while True:
            start = time.time()
            self.getSearchProgramPos()      # 이미지 검색 전 윈도우 프로그램 좌표 확인

            for i in self.searchProgramHandle:
                captureImg = self.screenshot(self.searchProgramPos[i])          # 현재 화면 캡쳐
                self.currentState(i, self.searchProgramPos[i], captureImg)         #   상태에 따른 이미지 찾기

                #for templatePath in self.searchTemplateFolder():
                #    self.searchImage(self.searchProgramPos[i], captureImg, templatePath)  #   이미지 찾기

                delta = time.time() - start

                if delta < SLEEP_TIME:
                    time.sleep(SLEEP_TIME - delta)

                key = cv2.waitKey(1) & 0xFF
                if key == ESC_KEY:
                    break

    def searchImage(self, pos, img_src, img_template):
        image = img_src
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)    #   흑백으로 변환

        template = cv2.imread(img_template, 0)
        w, h = template.shape[::-1]
        result = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)

        # 임계치로 찾는법
        threshold = self.imgAccuracy # 임계치 설정
        box_loc = np.where(result >= threshold) # 임계치 이상의 값들만 사용

        for box in zip(*box_loc[::-1]):     #   이미지 비교 일치한 데이터 빨간 사각형 테두리 전부 그리기
            startX, startY = box
            endX, endY = startX + w, startY + h
            #cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)    #   발견된 이미지 빨간 사각형 테두리 그리기
            searchImagePos = int((startX + endX)/2) + pos[0] - self.X_POS, int((startY + endY)/2) + pos[1]   #   발견된 이미지 가운데 좌표 가져오기
            return searchImagePos #   이미지 가운데 좌표 리턴, 발견된 이미지 없으면 None 리턴

    def hidSendReport(self, m, k, log):
        self.searchImgLog.emit(log)

        if m != 0:
            self.searchPos.emit(m)      #   마우스 제어
            time.sleep(self.delay)      #   딜레이

        if k != 0:
            for key in list(k):
                self.returnKey.emit(Keycode(0, key))
                time.sleep(self.delay)  # 딜레이

    def currentState(self, hwnd, pos, captureImg):     #   현재 오토 단계 확인
        if self.state == 0: # 대기화면
            resultPos = self.searchImage(pos, captureImg, r'.\IMAGE\HOME\death.bmp')    #   사망 확인창 발견시
            if resultPos != None: #   사망 경고창 확인 좌표 발견시
                self.hidSendReport(0, 0, "찾은 이미지 : {0}, 수행단계 : {1}, 케릭터 사망".format(str(r'.\IMAGE\HOME\death.bmp'), self.state))

                resultPos = self.searchImage(pos, captureImg, r'.\IMAGE\HOME\check.bmp')  #   확인창 버튼으로 이동
                if resultPos != None:
                    self.hidSendReport(Mousecode(1, resultPos, 0), 0, "찾은 이미지 : {0}, 수행단계 : {1}, 불사신부 사용".format(str(r'.\IMAGE\HOME\check.bmp'), self.state))

                    resultPos = self.searchImage(pos, captureImg, r'.\IMAGE\HOME\chicken.bmp')  # 반계탕, 삼계탕 사용
                    if resultPos != None:  # 반계탕, 삼계탕 사용
                        self.hidSendReport(Mousecode(2, resultPos, 0), 0, "찾은 이미지 : {0}, 수행단계 : {1}, 반계탕 사용".format(str(r'.\IMAGE\HOME\chicken.bmp'), self.state))

            if self.battleSuccess[hwnd] > 4:      #   정상적으로 전투 종료 횟수가 x회 이상이면
                resultPos = self.searchImage(pos, captureImg, r'.\IMAGE\HOME\snack.bmp')  # 삼색채 먹기
                if resultPos != None:  # 반계탕, 삼계탕 사용
                    self.hidSendReport(Mousecode(2, resultPos, 0), 0, "찾은 이미지 : {0}, 수행단계 : {1}, 삼색채먹기".format(str(r'.\IMAGE\HOME\chicken.bmp'), self.state))
                    self.hidSendReport(Mousecode(2, resultPos, 0), 0, "찾은 이미지 : {0}, 수행단계 : {1}, 삼색채먹기".format(str(r'.\IMAGE\HOME\chicken.bmp'), self.state))
                    self.hidSendReport(Mousecode(2, resultPos, 0), 0, "찾은 이미지 : {0}, 수행단계 : {1}, 삼색채먹기".format(str(r'.\IMAGE\HOME\chicken.bmp'), self.state))
                    self.hidSendReport(Mousecode(2, resultPos, 0), 0, "찾은 이미지 : {0}, 수행단계 : {1}, 삼색채먹기".format(str(r'.\IMAGE\HOME\chicken.bmp'), self.state))
                    self.hidSendReport(Mousecode(2, resultPos, 0), 0, "찾은 이미지 : {0}, 수행단계 : {1}, 삼색채먹기".format(str(r'.\IMAGE\HOME\chicken.bmp'), self.state))
                    self.hidSendReport(Mousecode(2, resultPos, 0), 0, "찾은 이미지 : {0}, 수행단계 : {1}, 삼색채먹기".format(str(r'.\IMAGE\HOME\chicken.bmp'), self.state))



                self.battleSuccess[hwnd] = 0

            self.state = self.state + 1

        elif self.state == 1: # 몬스터 클릭 후 경고 화면 또는 암행어사 발견시
            resultPos = self.searchImage(pos, captureImg, r'.\IMAGE\WARNING\check.bmp')  # 경고창 발견시
            if resultPos != None:  # 경고창 발견시
                self.hidSendReport(0, 0, "찾은 이미지 : {0}, 수행단계 : {1}, 경고창 발견".format(str(r'.\IMAGE\WARNING\check.bmp'), self.state))

                resultPos = self.searchImage(pos, captureImg, r'.\IMAGE\WARNING\check.bmp')  # 경고창 확인 버튼 이미지 발견시
                if resultPos != None:
                    self.hidSendReport(Mousecode(1, resultPos, 0), 0, "찾은 이미지 : {0}, 수행단계 : {1}, 경고창 확인 버튼 클릭".format(str(r'.\IMAGE\WARNING\check.bmp'), self.state))

            resultPos = self.searchImage(pos, captureImg, r'.\IMAGE\WARNING\mape.bmp')         # 암행어사 발견시
            if resultPos != None:  # 암행어사 이미지 발견시
                self.hidSendReport(0, 0, "찾은 이미지 : {0}, 수행단계 : {1}, 암행어사창 발견".format(str(r'.\IMAGE\WARNING\mape.bmp'), self.state))
                playsound("Warning.mp3")
                
            resultPos = self.searchImage(pos, captureImg, r'.\IMAGE\BATTLE\battleOption.bmp')         # 정상적으로 전투 진입시
            if resultPos != None:  # 전투 진입 후 옵션창 발견시
                self.hidSendReport(Mousecode(0, resultPos, 0), 0, "찾은 이미지 : {0}, 수행단계 : {1}, 전투 화면 옵션창 발견".format(str(r'.\IMAGE\BATTLE\battleOption.bmp'), self.state))
                self.state = self.state + 1
                
        elif self.state == 2: # 전투 중
            for imgPath in self.searchTemplateFolder():
                resultPos = self.searchImage(pos, captureImg, imgPath)  # 전투 종료 대기, 종료 판단은 메인화면 신용등급 이미지로 확인
                if resultPos != None:  #전투중 스킬 사용하고자 하는 이미지 인식되었다면
                    sendKeyboard = "1ee2ee3ee4ee"
                    self.hidSendReport(Mousecode(0, resultPos, 0), sendKeyboard, "찾은 이미지 : {0}, 수행단계 : {1}, 해당 좌표로 이동".format(str(imgPath), self.state))
                    break
            self.state = self.state + 1

        elif self.state == 3: # 전투 종료 대기
            resultPos = self.searchImage(pos, captureImg, r'.\IMAGE\HOME\credit.bmp')  # 전투 종료 대기, 종료 판단은 메인화면 신용등급 이미지로 확인
            if resultPos != None:  # 전투 종료 후 신용등급 이미지 발견시
                self.hidSendReport(Mousecode(0, resultPos, 0), 0, "찾은 이미지 : {0}, 수행단계 : {1}, 해당 좌표로 이동".format(str(r'.\IMAGE\HOME\credit.bmp'), self.state))
                self.state = self.state + 1

        elif self.state == 4:  # 전투 종료
            self.battleSuccess[hwnd] = self.battleSuccess[hwnd] + 1
            self.totalBattle[hwnd] = self.totalBattle[hwnd] + 1
            self.hidSendReport(0, 0, "총 전투 횟수 : {0}, 정상 전투 횟수 : {1}, handle : {2}".format(self.totalBattle[hwnd], self.battleSuccess[hwnd], hwnd))
            self.state = 0  #   다시 원점으로

    def gaussianBlur(self, img):
        image_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 흑백으로 변환
        return cv2.GaussianBlur(image_gray, (5, 5), 0)

def Mousecode(clcik, pos, wheel):
    hidSend = []
    hidSend.append(clcik)       #   0 동작X, 1 왼쪽 마우스 버튼, 2 오른쪽 마우스 버튼
    hidSend.append(pos[0])
    hidSend.append(pos[1])
    hidSend.append(wheel)   #   휠동작

    return hidSend
    


def Keycode(special, key):
    hidSend = []
    keyMap = {'a':4, 'A':4, 'b':5, 'B':5, 'c':6, 'C':6, 'd':7, 'D':7, 'e':8, 'E':8, 'f':9, 'F':9,
              'g':10, 'G':10, 'h':11, 'H':11, 'i':12, 'I':12, 'j':13, 'J':13, 'k':14, 'K':14, 'l':15, 'L':15,
              'm':0x10, 'M':0x10, 'n':0x11, 'N':0x11, 'o':0x12, 'O':0x12, 'p':0x13, 'P':0x13, 'q':0x14, 'Q':0x14,
              'r':0x15, 'R':0x15, 's':0x16, 'S':0x16, 't':0x17, 'T':0x17, 'u':0x18, 'U':0x18, 'v':0x19, 'V':0x19,
              'w':0x1A, 'W':0x1A, 'x':0x1B, 'X':0x1B, 'y':0x1C, 'Y':0x1C, 'z':0x1D, 'Z':0x1D, '1':0x1E, '!':0x1E,
              '2':0x1F, '@':0x1F, '3':0x20, '#':0x20, '4':0x21, '$':0x21, '5':0x22, '%':0x22, '6':0x23, '^':0x23,
              '7':0x24, '&':0x24, '8':0x25, '*':0x25, '9':0x26, '(':0x26, '0':0x27, ')':0x27}

    hidSend.append(special & 0xFF)          #  ctrl, cui, alt 등등 modifier  키눌림 확인
    hidSend.append(0)                       # reserved
    hidSend.append(keyMap[key])  # 입력할키
    hidSend.append(0)  # 입력할키

    return hidSend




    # ENTER = 0x28
    # """Enter (Return)"""
    # RETURN = ENTER
    # """Alias for ``ENTER``"""
    # ESCAPE = 0x29
    # """Escape"""
    # BACKSPACE = 0x2A
    # """Delete backward (Backspace)"""
    # TAB = 0x2B
    # """Tab and Backtab"""
    # SPACEBAR = 0x2C
    # """Spacebar"""
    # SPACE = SPACEBAR
    # """Alias for SPACEBAR"""
    # MINUS = 0x2D
    # """``-` and ``_``"""
    # EQUALS = 0x2E
    # """``=` and ``+``"""
    # LEFT_BRACKET = 0x2F
    # """``[`` and ``{``"""
    # RIGHT_BRACKET = 0x30
    # """``]`` and ``}``"""
    # BACKSLASH = 0x31
    # r"""``\`` and ``|``"""
    # POUND = 0x32
    # """``#`` and ``~`` (Non-US keyboard)"""
    # SEMICOLON = 0x33
    # """``;`` and ``:``"""
    # QUOTE = 0x34
    # """``'`` and ``"``"""
    # GRAVE_ACCENT = 0x35
    # r""":literal:`\`` and ``~``"""
    # COMMA = 0x36
    # """``,`` and ``<``"""
    # PERIOD = 0x37
    # """``.`` and ``>``"""
    # FORWARD_SLASH = 0x38
    # """``/`` and ``?``"""
    #
    # CAPS_LOCK = 0x39
    # """Caps Lock"""
    #
    # F1 = 0x3A
    # """Function key F1"""
    # F2 = 0x3B
    # """Function key F2"""
    # F3 = 0x3C
    # """Function key F3"""
    # F4 = 0x3D
    # """Function key F4"""
    # F5 = 0x3E
    # """Function key F5"""
    # F6 = 0x3F
    # """Function key F6"""
    # F7 = 0x40
    # """Function key F7"""
    # F8 = 0x41
    # """Function key F8"""
    # F9 = 0x42
    # """Function key F9"""
    # F10 = 0x43
    # """Function key F10"""
    # F11 = 0x44
    # """Function key F11"""
    # F12 = 0x45
    # """Function key F12"""
    #
    # PRINT_SCREEN = 0x46
    # """Print Screen (SysRq)"""
    # SCROLL_LOCK = 0x47
    # """Scroll Lock"""
    # PAUSE = 0x48
    # """Pause (Break)"""
    #
    # INSERT = 0x49
    # """Insert"""
    # HOME = 0x4A
    # """Home (often moves to beginning of line)"""
    # PAGE_UP = 0x4B
    # """Go back one page"""
    # DELETE = 0x4C
    # """Delete forward"""
    # END = 0x4D
    # """End (often moves to end of line)"""
    # PAGE_DOWN = 0x4E
    # """Go forward one page"""
    #
    # RIGHT_ARROW = 0x4F
    # """Move the cursor right"""
    # LEFT_ARROW = 0x50
    # """Move the cursor left"""
    # DOWN_ARROW = 0x51
    # """Move the cursor down"""
    # UP_ARROW = 0x52
    # """Move the cursor up"""
    #
    # KEYPAD_NUMLOCK = 0x53
    # """Num Lock (Clear on Mac)"""
    # KEYPAD_FORWARD_SLASH = 0x54
    # """Keypad ``/``"""
    # KEYPAD_ASTERISK = 0x55
    # """Keypad ``*``"""
    # KEYPAD_MINUS = 0x56
    # """Keyapd ``-``"""
    # KEYPAD_PLUS = 0x57
    # """Keypad ``+``"""
    # KEYPAD_ENTER = 0x58
    # """Keypad Enter"""
    # KEYPAD_ONE = 0x59
    # """Keypad ``1`` and End"""
    # KEYPAD_TWO = 0x5A
    # """Keypad ``2`` and Down Arrow"""
    # KEYPAD_THREE = 0x5B
    # """Keypad ``3`` and PgDn"""
    # KEYPAD_FOUR = 0x5C
    # """Keypad ``4`` and Left Arrow"""
    # KEYPAD_FIVE = 0x5D
    # """Keypad ``5``"""
    # KEYPAD_SIX = 0x5E
    # """Keypad ``6`` and Right Arrow"""
    # KEYPAD_SEVEN = 0x5F
    # """Keypad ``7`` and Home"""
    # KEYPAD_EIGHT = 0x60
    # """Keypad ``8`` and Up Arrow"""
    # KEYPAD_NINE = 0x61
    # """Keypad ``9`` and PgUp"""
    # KEYPAD_ZERO = 0x62
    # """Keypad ``0`` and Ins"""
    # KEYPAD_PERIOD = 0x63
    # """Keypad ``.`` and Del"""
    # KEYPAD_BACKSLASH = 0x64
    # """Keypad ``\\`` and ``|`` (Non-US)"""
    #
    # APPLICATION = 0x65
    # """Application: also known as the Menu key (Windows)"""
    # POWER = 0x66
    # """Power (Mac)"""
    # KEYPAD_EQUALS = 0x67
    # """Keypad ``=`` (Mac)"""
    # F13 = 0x68
    # """Function key F13 (Mac)"""
    # F14 = 0x69
    # """Function key F14 (Mac)"""
    # F15 = 0x6A
    # """Function key F15 (Mac)"""
    # F16 = 0x6B
    # """Function key F16 (Mac)"""
    # F17 = 0x6C
    # """Function key F17 (Mac)"""
    # F18 = 0x6D
    # """Function key F18 (Mac)"""
    # F19 = 0x6E
    # """Function key F19 (Mac)"""
    #
    # F20 = 0x6F
    # """Function key F20"""
    # F21 = 0x70
    # """Function key F21"""
    # F22 = 0x71
    # """Function key F22"""
    # F23 = 0x72
    # """Function key F23"""
    # F24 = 0x73
    # """Function key F24"""
    #
    # LEFT_CONTROL = 0xE0
    # """Control modifier left of the spacebar"""
    # CONTROL = LEFT_CONTROL
    # """Alias for LEFT_CONTROL"""
    # LEFT_SHIFT = 0xE1
    # """Shift modifier left of the spacebar"""
    # SHIFT = LEFT_SHIFT
    # """Alias for LEFT_SHIFT"""
    # LEFT_ALT = 0xE2
    # """Alt modifier left of the spacebar"""
    # ALT = LEFT_ALT
    # """Alias for LEFT_ALT; Alt is also known as Option (Mac)"""
    # OPTION = ALT
    # """Labeled as Option on some Mac keyboards"""
    # LEFT_GUI = 0xE3
    # """GUI modifier left of the spacebar"""
    # GUI = LEFT_GUI
    # """Alias for LEFT_GUI; GUI is also known as the Windows key, Command (Mac), or Meta"""
    # WINDOWS = GUI
    # """Labeled with a Windows logo on Windows keyboards"""
    # COMMAND = GUI
    # """Labeled as Command on Mac keyboards, with a clover glyph"""
    # RIGHT_CONTROL = 0xE4
    # """Control modifier right of the spacebar"""
    # RIGHT_SHIFT = 0xE5
    # """Shift modifier right of the spacebar"""
    # RIGHT_ALT = 0xE6
    # """Alt modifier right of the spacebar"""
    # RIGHT_GUI = 0xE7
    # """GUI modifier right of the spacebar"""


