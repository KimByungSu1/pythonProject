import time

import pyautogui, cv2
import numpy as np
import pywinauto

from PyQt5.QtCore import *

from PIL import ImageGrab
from functools import partial

from MODULE.myOpenCV import *           #   user Serial

ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

class myAuto(QThread):
    autoLog = pyqtSignal(str)         # 오토 로그
    autoSendReport = pyqtSignal(str)  # 이미지 발견시 시리얼통신으로 보내기위한 시그널

    def __init__(self):
        QThread.__init__(self)
        self.isAuto = False
        self.searchProgramName = "Gersang"  # 프로그램 이름
        self.searchProgramHandle = []  # 프로그램 핸들
        self.imgPathList = {'HOME': {}}  # 이미지 서치 Path 리스트
        self.searchImg = myOpenCV()  # 이미지 처리 하기위한 객채 생성
        self.initAuto()

    def stop(self):
        self.isAuto = False

    def run(self):
        while self.isAuto is True:
            self.autoStart()

    
    def getWindowList(self):            #   gersang 핸들 가져오기
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
    
    def initAuto(self):
        self.clientInfo = {0:{}}   #   클라이언트 개별 상태정보 확인
        self.getWindowList()        #   오토 시작전 윈도우 핸들 가져오기

        for idx, handle in enumerate(self.searchProgramHandle):  #   클라이언트별 정보 초기화
            self.clientInfo[idx]['Handle'] = handle    # 클라이언트 handle
            self.clientInfo[idx]['Status'] = 'HOME'        # 현재 상태
            self.clientInfo[idx]['ProgramPosition'] = self.searchImg.getProgramPos(handle)  #   클라이언트 위치좌표 확인
            self.clientInfo[idx]['BattleCount'] = 0  # 전투 횟수
            self.clientInfo[idx]['WarningCount'] = 0  # 암행어사 횟수
            self.clientInfo[idx]['DeathCount'] = 0  # 죽은 횟수
            self.clientInfo[idx]['EatCount'] = 0  # 포만감 섭취 횟수
            self.isAuto = True  #   클라이언트 한개이상 실행하는 경우

    def set_foreground(self, handle):       #   프로그램 최상단으로
        """put the window in the foreground"""
        pyautogui.press("alt")
        win32gui.SetForegroundWindow(handle)

    def searchImgFolder(self, status):      # 현재 상태에 따른 이미지 서치 폴더 경로
        # path = r'.\IMAGE\HOME\*.bmp'
        # file_list = glob.glob(path)  ## 폴더 안에 있는 모든 파일 출력
        #
        # if self.state[hwnd] == 0: # 대기화면
        #     path = r'.\IMAGE\HOME\*.bmp'
        # elif self.state[hwnd] == 1: # 경고 화면
        #     path = r'.\IMAGE\WARNING\*.bmp'
        # elif self.state[hwnd] == 2: # 전투 입장 확인
        #     path = r'.\IMAGE\BATTLE\BLACK_DRAGON_MAP\*.bmp'
        #
        # file_list = glob.glob(path)  ## 폴더 안에 있는 모든 파일 출력
        # for x in file_list:
        #     self.imgPathList
        pass

    def autoStart(self):
        for i in range(0,len(self.clientInfo)):
            self.set_foreground(self.clientInfo[i]['Handle'])   #   이미지 서치할 프로그램 최상단 고정
            time.sleep(0.5)     #   화면전환 0.5초 딜레이
            pos = self.clientInfo[i]['ProgramPosition']     # 현재 클라이언트 위치 좌표
            captureImg = self.searchImg.screenCapture(pos)  # 현재 화면 캡쳐
            #self.searchImg.captureImgAndShow(pos)
            #if self.clientInfo[i]['Status'] == 'HOME':      # Home화면에서 행동
           #     self.homeAct(self.clientInfo[i], pos, captureImg)


    
    def homeAct(self, idx, pos, captureImg):  #   Home화면에서 행동
        deathPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\death.bmp')  # 사망 경고창 좌표
        chickenPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\chicken.bmp')  # 삼계탕 좌표
        snackPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\snack.bmp')  # 삼색채 좌표
        creditPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\credit.bmp')  # 신용등급 좌표 -- 홈화면 확인 이미지
        checkPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\check.bmp')  # 확인버튼 좌표

        if deathPos is not None:    #   사망 경고창 발견시
            self.returnCommand(self.Mousecode(1, checkPos, 0), 0, "불사신부 사용")    #   불사신부 사용한다는 기준, 확인 버튼 으로 이동 후 클릭
            self.clientInfo[idx]['DeathCount'] = self.clientInfo[idx]['DeathCount'] + 1            #   사망카운트 증가
            time.sleep(0.2)
            if chickenPos is not None:  # 삼계탕 이미지 발견시
                self.returnCommand(self.Mousecode(2, chickenPos, 0), 0, "삼계탕 사용")  # 삼계탕 사용

        if creditPos is not None:  # 정상적인 홈화면
            self.returnCommand(0, 0, "홈 화면 전환")  #
            if self.clientInfo[idx]['BattleCount'] > 4:    #   4번째 전투마다 삼색채 먹기
                if snackPos is not None: #   삼색채 이미지 발견시
                    for repeat in range(0,4):   #   3번반복
                        self.returnCommand(self.Mousecode(2, snackPos, 0), 0, "삼색채 사용")  # 삼색채 이미지 이동 후 우클릭
                        time.sleep(0.2) # 반복 딜레이

        self.clientInfo[idx]['Status'] = 'BATTLE_WAIT'  #   전투 대기단계로 변경

    def returnCommand(self, mouse, keyboard, log):        #   시리얼통신으로 전달할 커맨드
        if mouse != 0:
            tx = self.CtrlAddCheckSum("$MOUSE,{0},{1},{2},{3},*".format(mouse[0], mouse[1], mouse[2], mouse[3]))
            self.autoSendReport.emit(tx)      #   마우스 제어 프로토콜 전송
            time.sleep(0.1)  # 마우스 이동시간 대기
            
        if keyboard != 0:
            tx = self.CtrlAddCheckSum("$KEYBOARD,0,0,{0},*".format(keyboard))
            self.autoSendReport.emit(tx)    #   키보드 제어 프로토콜 전송

        self.autoLog.emit(log)

    def Mousecode(self, clcik, pos, wheel):
        hidSend = []
        hidSend.append(clcik)       #   0 동작X, 1 왼쪽 마우스 버튼, 2 오른쪽 마우스 버튼
        hidSend.append(pos[0])
        hidSend.append(pos[1])
        hidSend.append(wheel)   #   휠동작

        return hidSend

    def CtrlAddCheckSum(self, txStr):
        CheckSum = 0
        CheckSumResult = 0
        for x in txStr:
            if x == '$':
                continue
            elif x == '*':
                if CheckSum <= 15:  # 체크섬 결과가 15(dec)보다 낮으면 hex로 0xf로 표시되 따라서 0x0f로 표시 하기위해 '0'추가
                    CheckSumResult = '0' + (str(hex(CheckSum))[2:].upper()) + "\r\n"
                else:
                    CheckSumResult = (str(hex(CheckSum))[2:].upper()) + "\r\n"
                return txStr + CheckSumResult  # 종료문자 발견시 xor연산 결과 + '\r' + '\n' 추가
            else:
                CheckSum ^= ord(x)  # 문자를 int(아스키) 변환및 종료문자 발견까지 xor

        return False  # '*'종료문자 발견 못할시 False

