import time

import pyautogui, cv2

import win32api, binascii
import win32gui
import numpy as np
import cv2, os, glob
import pyautogui
import time
import pywinauto
import pygetwindow as gw

from PyQt5.QtCore import *

from playsound import playsound

from MODULE.myOpenCV import *           #   user Serial

class gameInfoStruct():
    Status = 0      #   현재 상태
    BattleCount = 0  # 전투 횟수
    WarningCount = 0  # 암행어사 횟수
    DeathCount = 0  # 죽은 횟수
    EatCount = 0  # 포만감 섭취 횟수
    TimeOutCount = 0    #   Time Out 시 다음 상태로 변경
    Battle = 0


class myAuto(QThread):
    autoLog = pyqtSignal(str)         # 오토 로그
    autoSendReport = pyqtSignal(str)  # 이미지 발견시 시리얼통신으로 보내기위한 시그널

    def __init__(self):
        QThread.__init__(self)
        self.isAuto = False
        self.searchProgramName = "Gersang"  # 프로그램 이름
        self.searchProgramHandle = []  # 프로그램 핸들
        self.searchImg = myOpenCV()  # 이미지 처리 하기위한 객채 생성
        self.isInitOk = 0
        self.Battle = 0
        self.initAuto()

        self.timer = QTimer()
        self.timer.start(1000)  #   1초마다
        self.timer.timeout.connect(self.timer1Sec)

    def stop(self):
        self.isAuto = False

    def timer1Sec(self):
        if self.isAuto:
            for i in range(0, len(self.clientInfo)):
                self.gameInfo[i].TimeOutCount = self.gameInfo[i].TimeOutCount + 1   #   1초마다 타임 아웃 카운트 증가

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
        if self.isInitOk == 0:
            self.isInitOk = 1
            self.clientInfo = {0:{}, 1:{}, 2:{}}   #   클라이언트 고유 정보
            self.gameInfo = []          #   게임내 정보
            self.getWindowList()        #   오토 시작전 윈도우 핸들 가져오기

            for idx, handle in enumerate(self.searchProgramHandle):  #   클라이언트별 정보 초기화
                self.clientInfo[idx]['Handle'] = handle    # 클라이언트 handle
                self.clientInfo[idx]['ProgramPosition'] = self.searchImg.getProgramPos(handle)  #   클라이언트 위치좌표 확인
                self.gameInfo.append(gameInfoStruct())
                self.isAuto = True  #   클라이언트 한개이상 실행하는 경우
                #print(self.searchImg.getProgramPos(handle))

    def set_foreground(self, handle):       #   프로그램 최상단으로
        """put the window in the foreground"""
        pyautogui.press("alt")
        win32gui.SetForegroundWindow(handle)

    def searchBattleMap(self):      # 전투 맵 이미지
        path = r'.\IMAGE\BATTLE\BLACK_DRAGON_MAP\*.bmp' # 전투 맵 이미지 반복 확인
        return glob.glob(path)  ## 폴더 안에 있는 모든 파일 출력

    def autoStart(self):
        for i in range(0,len(self.searchProgramHandle)):

            self.set_foreground(self.clientInfo[i]['Handle'])   #   이미지 서치할 클라이언트 최상단
            time.sleep(0.5)

            pos = self.clientInfo[i]['ProgramPosition']

            if self.gameInfo[i].Status == 0:      # Home화면에서 행동
                captureImg = self.searchImg.screenCapture(pos)  # 현재 화면 캡쳐
                self.homeAct(self.gameInfo[i], pos, captureImg)

            if self.gameInfo[i].Status == 1:      #   전투 대기 상태
                captureImg = self.searchImg.screenCapture(pos)  # 현재 화면 캡쳐
                self.BattleWaitAct(self.gameInfo[i], pos, captureImg)

            time.sleep(2)

    def homeAct(self, info, pos, captureImg):  #   Home화면에서 행동
        deathPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\death.bmp')  # 사망 경고창 좌표
        chickenPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\chicken.bmp')  # 삼계탕 좌표
        snackPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\snack.bmp')  # 삼색채 좌표
        creditPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\credit.bmp')  # 신용등급 좌표 -- 홈화면 확인 이미지
        checkPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\check.bmp')  # 확인버튼 좌표
        battleEnterPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\BATTLE\battleEnter.bmp')  # 전투 진입 확인 이미지 좌표

        if deathPos:    #   사망 경고창 발견시
            self.returnCommand(info, self.Mousecode(1, checkPos, 0), 0, "불사신부 사용")    #   불사신부 사용한다는 기준, 확인 버튼 으로 이동 후 클릭
            info.DeathCount = info.DeathCount + 1            #   사망카운트 증가
            if chickenPos:  # 삼계탕 이미지 발견시
                self.returnCommand(info, self.Mousecode(2, chickenPos, 0), 0, "삼계탕 사용")  # 삼계탕 사용

        if creditPos:  # 정상적인 홈화면
            if info.BattleCount > 4:    #   4번째 전투마다 삼색채 먹기
                if snackPos: #   삼색채 이미지 발견시
                    for repeat in range(0,4):   #   3번반복
                        self.returnCommand(info, self.Mousecode(2, snackPos, 0), 0, "삼색채 사용")  # 삼색채 이미지 이동 후 우클릭

        if battleEnterPos:    #   전투 진입 이미지 발견시
            info.Status = info.Status + 1


    def BattleWaitAct(self, info, pos, captureImg):  #   전투 대기 상태
        mapePos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\WARNING\mape.bmp')  # 암행 어사 발견 이미지 좌표
        warningCheckPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\WARNING\check.bmp')  # 확인 이미지 좌표
        battleEnterPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\BATTLE\battleEnter.bmp')  # 전투 진입 확인 이미지 좌표
        creditPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\credit.bmp')  # 신용등급 좌표 -- 홈화면 확인 이미지

        if mapePos:    #   암행어사 이미지 발견시
            self.returnCommand(info, self.Mousecode(0, mapePos, 0), 0, "암행 어사 발견")  # 암행 어사 발견
            #playsound("Warning.mp3")    #   경고 사운드 재생
            time.sleep(20)              #   마패 찾을시간

        if warningCheckPos:    #   기타 경고 이미지 발견시
            self.returnCommand(info, self.Mousecode(0, warningCheckPos, 0), 0, "경고창 발견")  # 확인창 이미지로 이동만
            #playsound("Check.mp3")    #   체크 사운드 재생

        if battleEnterPos and self.Battle == 0:    #   전투 진입 이미지 발견시
            skill = '1e2e3e4e'  # 전투맵 이미지 발견시 스킬 예약
            for map in self.searchBattleMap():
                battleMapSearchPos = self.searchImg.searchImage(pos, captureImg, map)  # 전투맵 이미지 경로 저장
                if battleMapSearchPos:  # 전투맵 내부 이미지 인식시
                    self.returnCommand(info, self.Mousecode(0, battleMapSearchPos, 0),
                                       skill, "발견된 이미지 {0}, 마우스 이동, {1}, {2}".format(map, battleMapSearchPos[0], battleMapSearchPos[1]))  # 전투 진입 이미지 이동
                    print('반복문 탈출')
                    self.Battle = 1
                    break
        elif self.Battle == 1:
            skill = '1e2e3e4e'  # 전투맵 이미지 발견시 스킬 예약
            self.returnCommand(info, 0, skill, "전투중 스킬시전")  # 전투 진입 이미지 이동

        if creditPos:    #   신용등급 이미지 이미지 발견시
            self.returnCommand(info, 0, 0, "전투 종료")  # 신용등급 이미지 확인
            info.Status = 0  # Home 화면 전환
            info.Battle = 0
            #playsound("Check.mp3")    #   체크 사운드 재생


    def returnCommand(self, info, mouse, key, log):        #   시리얼통신으로 전달할 커맨드
        self.autoLog.emit(log)
        print('커맨드 전송 함수 진입')
        if mouse:
            tx = self.CtrlAddCheckSum("$MOUSE,{0},{1},{2},{3},*".format(mouse[0], int((mouse[1] - pyautogui.position().x)), int((mouse[2] - pyautogui.position().y)), mouse[3]))
            print(tx)
            self.autoSendReport.emit(tx)      #   마우스 제어 프로토콜 전송
            time.sleep(0.5)  # 마우스 이동시간

        if key:
            tx = self.CtrlAddCheckSum("$KEYBOARD,0,0,{0},*".format(key))
            self.autoSendReport.emit(tx)    #   키보드 제어 프로토콜 전송
            time.sleep(2)  # 마우스 이동시간 대기

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

