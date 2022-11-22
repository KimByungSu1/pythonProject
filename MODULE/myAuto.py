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
    BattleTotalCount = 0  # 총 전투 횟수
    BattleCount = 0  # 전투 횟수
    WarningCount = 0  # 경고창 발생 횟수
    MapeCount = 0  # 암행어사 횟수
    DeathCount = 0  # 죽은 횟수
    EatCount = 0  # 포만감 섭취 횟수
    TimeOutCount = 0    #   Time Out 시 다음 상태로 변경
    ChickenCount = 0  # 삼계탕 섭취 횟수
    Battle = 0


class myAuto(QThread):
    autoLog = pyqtSignal(int, str)    # 오토 로그
    gameInfoLog = pyqtSignal(int, list)  # 1초마다 게임정보
    autoSendReport = pyqtSignal(str)  # 이미지 발견시 시리얼통신으로 보내기위한 시그널

    def __init__(self):
        QThread.__init__(self)
        self.isAuto = False
        self.searchProgramName = "Gersang"  # 프로그램 이름
        self.searchProgramHandle = []  # 프로그램 핸들
        self.HandleCount = 0  # 프로그램 갯수
        self.searchImg = myOpenCV()  # 이미지 처리 하기위한 객채 생성
        #self.searchImg.start()
        self.battlePath = ''        #   사냥터 이미지 인식 폴더
        self.battleMapSearchPos = 0
        self.isInitOk = 0
        self.Battle = 0
        self.gameInfo = []  # 게임내 정보
        self.clientInfo = {0: {}, 1: {}, 2: {}}  # 클라이언트 고유 정보
        self.initAuto()
        self.jamsu = 0  #   잠수팅 방지
        self.deathHero = 0  # 죽은용병 살리기
        self.jamsuCount = 0

        self.timer = QTimer()
        self.timer.start(1000)  #   1초마다
        self.timer.timeout.connect(self.timer1Sec)

    def stop(self):
        self.isAuto = False

    def timer1Sec(self):
        if self.isAuto:
            self.gameInfoLog.emit(self.HandleCount, self.gameInfo)

            if self.jamsu:          #   30분 사냥터 팅방지
                self.jamsuCount = self.jamsuCount + 1       #   20분 이상 되면 잠수 방지 매클 동작



    def run(self):
        if self.isInitOk:
            self.isAuto = True
        while self.isAuto is True:
            self.autoStart()
            pass

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
            self.getWindowList()        #   오토 시작전 윈도우 핸들 가져오기
            for idx, handle in enumerate(self.searchProgramHandle):  #   클라이언트별 정보 초기화
                self.clientInfo[idx]['Handle'] = handle    # 클라이언트 handle
                self.clientInfo[idx]['ProgramPosition'] = self.searchImg.getProgramPos(handle)  #   클라이언트 위치좌표 확인
                self.centerPos = int(((self.searchImg.getProgramPos(handle)[0]*2)+self.searchImg.getProgramPos(handle)[2])/2), int(((self.searchImg.getProgramPos(handle)[1]*2)+self.searchImg.getProgramPos(handle)[3])/2)  # 클라이언트 위치좌표 확인
                self.gameInfo.append(gameInfoStruct())
                self.HandleCount = idx + 1
                self.isAuto = True  #   클라이언트 한개이상 실행하는 경우

    def set_foreground(self, handle):       #   프로그램 최상단으로
        """put the window in the foreground"""
        pyautogui.press("alt")
        win32gui.SetForegroundWindow(handle)
        time.sleep(0.3)

    def searhDeathHero(self):      # 사망한 용병 찾기
        deathPath = r'.\IMAGE\DEATH/*.bmp'
        return glob.glob(deathPath)  ## 폴더 안에 있는 모든 파일 출력

    def searchBattleMap(self):      # 전투 맵 이미지
        path = self.battlePath + '/*.bmp'
        return glob.glob(path)  ## 폴더 안에 있는 모든 파일 출력

    def autoStart(self):
        for i in range(0, self.HandleCount):
            self.set_foreground(self.clientInfo[i]['Handle'])  # 이미지 서치할 클라이언트 최상단
            pos = self.clientInfo[i]['ProgramPosition']
            # captureImg = self.searchImg.screenCapture(pos)  # 현재 화면 캡쳐
            # cv2.imshow("frame1", captureImg)
            # key = cv2.waitKey(1)
            if self.jamsuCount > 1700:
                self.returnCommand(i, 0, 0, "사냥터 팅방지 매크로 동작 {0}".format(self.jamsuCount))  # 사냥터 팅방지 매크로 동작
                self.EnterFunc()    #   잠수방지 매크로 동작

            if self.gameInfo[i].Status == 0:      # Home화면에서 행동
                captureImg = self.searchImg.screenCapture(pos)  # 현재 화면 캡쳐
                self.homeAct(i, captureImg)

            elif self.gameInfo[i].Status == 1:      #   전투 대기 상태
                captureImg = self.searchImg.screenCapture(pos)  # 현재 화면 캡쳐
                self.BattleAct(i, captureImg)

    def homeAct(self, idx, captureImg):  #   Home화면에서 행동
        pos = self.clientInfo[idx]['ProgramPosition']
        snackPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\snack.bmp')  # 삼색채 좌표
        creditPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\credit.bmp')  # 신용등급 좌표 -- 홈화면 확인 이미지
        deathPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\death.bmp')  # 사망 경고창 좌표
        chickenPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\chicken.bmp')  # 삼계탕 좌표
        checkPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\check.bmp')  # 확인버튼 좌표

        if deathPos:    #   사망 경고창 발견시
            self.returnCommand(idx, self.Mousecode(1, checkPos, 0), 0, "불사신부 사용")    #   불사신부 사용한다는 기준, 확인 버튼 으로 이동 후 클릭
            time.sleep(1)
            self.gameInfo[idx].DeathCount = self.gameInfo[idx].DeathCount + 1            #   사망카운트 증가
            self.returnCommand(idx, 0, self.KeyboardCode(0x04, "1111"), "삼계탕 사용")  # 삼계탕 사용
            time.sleep(1)
            self.gameInfo[idx].ChickenCount = self.gameInfo[idx].ChickenCount + 1   #   삼계탕 사용 카운트 증가
            self.gameInfo[idx].BattleCount = 0 #    삼계탕 사용시 포만감 채워지므로 포만감 섭취 카운트 초기화

        # if self.deathHero:
        #     for deathHero in self.searhDeathHero():       #   죽은 용병 찾기
        #         deathHeroPos = self.searchImg.trueSearchImage(pos, captureImg, deathHero)  # 전투맵 이미지 경로 저장
        #         if deathHeroPos:  # 죽은용병 확인시
        #             if chickenPos:  # 삼계탕 이미지 발견시
        #                 self.returnCommand(idx, self.Mousecode(2, chickenPos, 0), 0, "삼계탕 사용")  # 삼계탕 사용
        #                 self.gameInfo[idx].BattleCount = 0  #    삼계탕 사용시 포만감 채워지므로 포만감 섭취 카운트 초기화

        if creditPos:  # 정상적인 홈화면
            if self.gameInfo[idx].BattleCount > 4:  # 5번째 전투마다 삼색채 먹기
                self.snackEat(idx, snackPos)  # 삼색채 먹기

        self.gameInfo[idx].Status = self.gameInfo[idx].Status + 1

    def BattleAct(self, idx, captureImg):  #   전투 대기 상태
        pos = self.clientInfo[idx]['ProgramPosition']
        mapePos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\WARNING\mape.bmp')  # 암행 어사 발견 이미지 좌표
        mapePos1 = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\WARNING\mape_1.bmp')  # 암행 어사 발견 이미지 좌표
        warningCheckPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\WARNING\check.bmp')  # 확인 이미지 좌표
        battleEnterPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\BATTLE\battleEnter.bmp')  # 전투 진입 확인 이미지 좌표
        creditPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\credit.bmp')  # 신용등급 좌표 -- 홈화면 확인 이미지
        snackPos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\HOME\snack.bmp')  # 삼색채 좌표
        bottlePos = self.searchImg.searchImage(pos, captureImg, r'.\IMAGE\WARNING\bottle.bmp')  # 바닥에 십전대보탕 이미지 확인시

        if creditPos and self.gameInfo[idx].Battle == 1:  # 신용등급 이미지 이미지 발견시
            self.returnCommand(idx, 0, 0, "전투 종료")  # 신용등급 이미지 확인
            self.battleMapSearchPos = 0
            self.gameInfo[idx].Status = 0  # Home 화면 전환
            self.gameInfo[idx].Battle = 0
            self.gameInfo[idx].BattleCount = self.gameInfo[idx].BattleCount + 1
            self.gameInfo[idx].BattleTotalCount = self.gameInfo[idx].BattleTotalCount + 1
            self.snackEat(idx, snackPos)    #   삼색채 먹기

        elif battleEnterPos and self.gameInfo[idx].Battle == 0:    #   전투 진입 이미지 발견시
            self.jamsuCount = 0

            self.returnCommand(idx, self.Mousecode(0, self.centerPos, 0), 0, "1번부대 화면 및 마우스 중앙으로 이동")  # 1번부대 화면 및 마우스 중앙으로 이동

            skill = '1e2e3e4e'  # 전투맵 이미지 발견시 스킬 예약
            if self.battleMapSearchPos:         #   다른 클라이언트에서 찾은 이미지 좌표가 있다면
                self.returnCommand(idx, self.Mousecode(0, self.battleMapSearchPos, 0), self.KeyboardCode(0, skill), "서치 완료, 마우스 이동, {0}, {1}".format(self.battleMapSearchPos[0], self.battleMapSearchPos[1]))  # 전투 진입 이미지 이동
            else:
                for map in self.searchBattleMap():
                    battleMapSearchPos = self.searchImg.searchImage(pos, captureImg, map)  # 전투맵 이미지 경로 저장
                    if battleMapSearchPos:  # 전투맵 내부 이미지 인식시
                        self.returnCommand(idx, self.Mousecode(0, battleMapSearchPos, 0), self.KeyboardCode(0, skill), "발견된 이미지 {0}, 마우스 이동, {1}, {2}".format(map, battleMapSearchPos[0], battleMapSearchPos[1]))  # 전투 진입 이미지 이동
                        self.battleMapSearchPos = battleMapSearchPos
                        break
            self.gameInfo[idx].Battle = 1

        elif self.gameInfo[idx].Battle:
            skill = '11e2e3e4e'  # 1번 케릭터로 이동 및 마우스 센터로 옮기기
            self.returnCommand(idx, self.Mousecode(0, self.centerPos, 0), self.KeyboardCode(0, skill), "1번부대 화면 스킬 반복 시전")  # 1번부대 화면 스킬 반복시전

        elif mapePos:    #   암행어사 이미지 발견시
            self.returnCommand(idx, self.Mousecode(0, mapePos, 0), 0, "암행 어사 발견")  # 암행 어사 발견
            self.gameInfo[idx].MapeCount = self.gameInfo[idx].MapeCount + 1
            time.sleep(20)              #   마패 찾을시간

        elif mapePos1:    #   암행어사 이미지 발견시
            self.returnCommand(idx, self.Mousecode(0, mapePos1, 0), 0, "암행 어사 발견")  # 암행 어사 발견
            self.gameInfo[idx].MapeCount = self.gameInfo[idx].MapeCount + 1
            time.sleep(20)              #   마패 찾을시간

        elif warningCheckPos:    #   기타 경고 이미지 발견시
            self.returnCommand(idx, self.Mousecode(1, warningCheckPos, 0), 0, "경고창 발견")  # 확인창 이미지로 이동 후 클릭
            self.returnCommand(idx, self.Mousecode(0, self.centerPos, 0), 0, "경고창 확인 클릭 후 센터이동")  # 확인창 클릭 후 센터 이동
            self.gameInfo[idx].WarningCount = self.gameInfo[idx].WarningCount + 1
            
        elif bottlePos:    #   바닥에 십전대보탕 이미지 발견시
            self.returnCommand(idx, 0, self.KeyboardCode(0x04, "1111"), "삼계탕 사용")  # 삼계탕 사용
            time.sleep(2)  # 초마다 한번씩
            tx = self.CtrlAddCheckSum("$KEYBOARD,0,0,{0},*".format("p"))  # 파티말 변경
            self.autoSendReport.emit(tx)  # 키보드 제어 프로토콜 전송
            time.sleep(2)  # 초마다 한번씩
            tx = self.CtrlAddCheckSum("$KEYBOARD,0,0,{0}{1}{2},*".format(chr(0x05), idx, chr(0x05)))  # 엔터
            self.autoSendReport.emit(tx)  # 키보드 제어 프로토콜 전송
            time.sleep(5)  # 초마다 한번씩
            self.gameInfo[idx].BattleCount = 0  #   삼계탕 사용시 배틀카운트 초기화


    def BattleWait(self, idx, captureImg):  # 전투 대기 상태
        pass

    def snackEat(self, idx, snackPos): #   삼색채 먹기
        if self.gameInfo[idx].BattleCount > 5:  # 4번째 전투마다 삼색채 먹기
            if snackPos:  # 삼색채 이미지 발견시
                for repeat in range(0, 5):  # 5번반복
                    self.returnCommand(idx, 0, self.KeyboardCode(0x04, "22222"), "삼색채 사용")  # 삼색채 이미지 이동 후 우클릭
                    time.sleep(0.1)
                    self.gameInfo[idx].EatCount = self.gameInfo[idx].EatCount + 1
                self.returnCommand(idx, self.Mousecode(0, self.centerPos, 0), 0, "삼색채 사용 완료, 센터로 마우스 이동")  # 삼색채 완료 후 센터로 마우스이동
                time.sleep(0.1)
            self.gameInfo[idx].BattleCount = 0

    def returnCommand(self, idx, mouse, key, log):        #   시리얼통신으로 전달할 커맨드
        self.autoLog.emit(idx, log)
        if mouse:
            tx = self.CtrlAddCheckSum("$MOUSE,{0},{1},{2},{3},*".format(mouse[0], int((mouse[1] - pyautogui.position().x)), int((mouse[2] - pyautogui.position().y)), mouse[3]))
            self.autoSendReport.emit(tx)      #   마우스 제어 프로토콜 전송
            time.sleep(0.3)  # 대기시간
        if key:
            self.autoSendReport.emit(key)    #   키보드 제어 프로토콜 전송
            time.sleep(0.3)  # 대기시간
        time.sleep(0.1)

    def Mousecode(self, clcik, pos, wheel):
        hidSend = []
        hidSend.append(clcik)       #   0 동작X, 1 왼쪽 마우스 버튼, 2 오른쪽 마우스 버튼
        hidSend.append(pos[0])
        hidSend.append(pos[1])
        hidSend.append(wheel)   #   휠동작
        return hidSend

    def AltTabFunc(self):
        tx = self.CtrlAddCheckSum("$KEYBOARD,{0},0,{1},*".format(chr(0x04), chr(0x09)))  #   알트
        self.autoSendReport.emit(tx)  # 키보드 제어 프로토콜 전송

    def EnterFunc(self):    #   잠수방지
        tx = self.CtrlAddCheckSum("$KEYBOARD,0,0,{0},*".format("p")) #   파티말 변경
        self.autoSendReport.emit(tx)  # 키보드 제어 프로토콜 전송
        time.sleep(5)  #   초마다 한번씩
        tx = self.CtrlAddCheckSum("$KEYBOARD,0,0,{0}{1}{2},*".format(chr(0x05), ".", chr(0x05))) #   엔터
        self.autoSendReport.emit(tx)  # 키보드 제어 프로토콜 전송
        time.sleep(5)  #   초마다 한번씩

    def KeyboardCode(self, modifier, key):
        tx = self.CtrlAddCheckSum("$KEYBOARD,{0},0,{1},*".format(modifier, key))  #   알트
        return tx

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
