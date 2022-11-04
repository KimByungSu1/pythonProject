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
    searchImgFile = pyqtSignal(str)  # 찾은 이미지 파일

    def __init__(self):
        QThread.__init__(self)
        self.searchProgramName = "Gersang"      #   프로그램 이름
        self.searchProgramHandle = []           #   프로그램 핸들
        self.searchProgramPos = {}              #   프로그램 좌표

        self.templateBattle = {}                # 전투 템플릿 이미지
        self.templatehome = {}                  # 홈 템플릿 이미지
        
        self.wait_time = 1 / FRAME_RATE         #   서치 시간
        
        self.state = 0   #   현재 단계 확인
        self.battleSuccess = 0  #   정상적으로 전투 완료 한 횟수
        self.totalBattle = 0  # 총 전투 완료 횟수

        self.methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
        self.getWindowList()
        self.searchTemplateFolder()

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
                self.currentState(self.searchProgramPos[i], captureImg)         #   상태에 따른 이미지 찾기

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
            searchImagePos = [0, int((startX + endX)/2) + pos[0] - self.X_POS, int((startY + endY)/2) + pos[1], 0]   #   발견된 이미지 가운데 좌표 가져오기
            return [True, searchImagePos]

    def currentState(self, pos, captureImg):     #   현재 오토 단계 확인
        if self.state == 0: # 대기화면
            result = self.searchImage(pos, captureImg, r'.\IMAGE\HOME\death.bmp')    #   사망 확인창 발견시
            if result != None: #   사망 경고창 확인
                self.searchImgFile.emit("찾은 이미지 : {0}, 수행단계 : {1}, 케릭터 사망".format(str(r'.\IMAGE\HOME\death.bmp'), self.state))

                result = self.searchImage(pos, captureImg, r'.\IMAGE\HOME\check.bmp')  #   불사신부 사용
                if result[0] == True:
                    result[1][0] = 1   # 좌클릭
                    self.searchPos.emit(result[1])
                    self.searchImgFile.emit("찾은 이미지 : {0}, 수행단계 : {1}, 불사신부 사용".format(str(r'.\IMAGE\HOME\check.bmp'), self.state))

                    result = self.searchImage(pos, captureImg, r'.\IMAGE\HOME\chicken.bmp')  # 반계탕, 삼계탕 사용
                    if result[0] == True:  # 반계탕, 삼계탕 사용
                        result[1][0] = 2  # 우클릭
                        self.searchPos.emit(result[1])
                        self.searchImgFile.emit("찾은 이미지 : {0}, 수행단계 : {1}, 반계탕 or 삼계탕 먹기".format(str(r'.\IMAGE\HOME\chicken.bmp'), self.state))

            if self.battleSuccess > 4:      #   정상적으로 전투 종료 횟수가 x회 이상이면
                result = self.searchImage(pos, captureImg, r'.\IMAGE\HOME\snack.bmp')  # 삼색채 먹기
                if result[0] == True:  # 반계탕, 삼계탕 사용
                    result[1][0] = 2  # 우클릭
                    self.searchPos.emit(result[1])
                    self.searchPos.emit(result[1])
                    self.searchPos.emit(result[1])
                    self.searchPos.emit(result[1])
                    self.searchImgFile.emit("찾은 이미지 : {0}, 수행단계 : {1}, 포만감 채우기".format(str(r'.\IMAGE\HOME\snack.bmp'), self.state))
                self.battleSuccess = 0

            self.state = self.state + 1

        elif self.state == 1: # 몬스터 클릭 후 경고 화면 또는 암행어사 발견시
            result = self.searchImage(pos, captureImg, r'.\IMAGE\WARNING\check.bmp')  # 경고창 발견시
            if result != None:  # 경고창 발견시
                result = self.searchImage(pos, captureImg, r'.\IMAGE\WARNING\check.bmp')  # 경고창 확인 버튼 이미지 발견시
                if result[0] == True:
                    result[1][0] = 1  # 좌클릭
                    self.searchPos.emit(result[1])
                    self.searchImgFile.emit("찾은 이미지 : {0}, 수행단계 : {1}, 몬스터 클릭 후 경고창 확인 버튼 클릭".format(str(r'.\IMAGE\WARNING\check.bmp'), self.state))
                    
            result = self.searchImage(pos, captureImg, r'.\IMAGE\WARNING\mape.bmp')         # 암행어사 발견시
            if result != None:  # 암행어사 이미지 발견시
                self.searchImgFile.emit("찾은 이미지 : {0}, 수행단계 : {1}, 몬스터 클릭 후 암행어사창 발견".format(str(r'.\IMAGE\WARNING\mape.bmp'), self.state))
                playsound("Warning.mp3")
                
            result = self.searchImage(pos, captureImg, r'.\IMAGE\BATTLE\battleOption.bmp')         # 정상적으로 전투 진입시
            if result != None:  # 전투 진입 후 옵션창 발견시
                self.searchPos.emit(result[1])  # 해당위치로 마우스 이동
                self.searchImgFile.emit("찾은 이미지 : {0}, 수행단계 : {1}, 전투 진입 후 옵션창 발견".format(str(r'.\IMAGE\BATTLE\battleOption.bmp'), self.state))
                self.state = self.state + 1
                
        elif self.state == 2: # 전투 중
            for imgPath in self.searchTemplateFolder():
                result = self.searchImage(pos, captureImg, imgPath)  # 전투 종료 대기, 종료 판단은 메인화면 신용등급 이미지로 확인
                if result != None:  #전투중 스킬 사용하고자 하는 이미지 인식되었다면
                    self.searchPos.emit(result[1])  #   해당위치로 마우스 이동
                    self.searchImgFile.emit("찾은 이미지 : {0}, 수행단계 : {1}, 해당 좌표로 이동".format(str(imgPath), self.state))
                    break
            self.state = self.state + 1

        elif self.state == 3: # 전투 종료 대기
            result = self.searchImage(pos, captureImg, r'.\IMAGE\HOME\credit.bmp')  # 전투 종료 대기, 종료 판단은 메인화면 신용등급 이미지로 확인
            if result != None:  # 전투 종료 후 신용등급 이미지 발견시
                self.searchImgFile.emit("찾은 이미지 : {0}, 수행단계 : {1}, 정상적으로 전투 종료".format(str(r'.\IMAGE\HOME\credit.bmp'), self.state))
                self.state = self.state + 1
                
        elif self.state == 4:  # 전투 종료
            self.battleSuccess = self.battleSuccess + 1
            self.totalBattle = self.totalBattle + 1
            self.searchImgFile.emit("총 전투 횟수 : {0}, 정상 전투 횟수 : {1}, 수행단계 : {2}".format(self.totalBattle, self.battleSuccess, self.state))
            self.state = 0  #   다시 원점으로
            
        #self.searchPos.emit(pos)
        #self.searchImgFile.emit("찾은 이미지 : {0}, 수행단계 : {1}".format(str(img), self.state))

        #self.state = self.state + 1  # 다음단계로

    # def searchImage(self, pos, img_src, img_template):
    #     image = img_src
    #     image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)    #   흑백으로 변환
    #
    #     searchPath = self.searchTemplateFolder()
    #
    #     for imgPath in searchPath:                              #   이미지 폴더 내부에 있는 파일 전부 비교
    #         template = cv2.imread(imgPath, 0)
    #         w, h = template.shape[::-1]
    #         result = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)
    #
    #         threshold = self.imgAccuracy # 임계치 설정
    #         box_loc = np.where(result >= threshold) # 임계치 이상의 값들만 사용
    #
    #         for box in zip(*box_loc[::-1]):     #   이미지 비교 일치한 데이터 빨간 사각형 테두리 전부 그리기
    #             startX, startY = box
    #             endX, endY = startX + w, startY + h
    #             cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)    #   발견된 이미지 빨간 사각형 테두리 그리기
    #             searchImagePos = (int((startX + endX)/2) + pos[0] - self.X_POS, int((startY + endY)/2) + pos[1])   #   발견된 이미지 가운데 좌표 가져오기
    #             self.searchPos.emit(searchImagePos)
    #
    #         if result >= self.imgAccuracy:
    #             self.searchImgFile.emit("이미지 폴더 : {0}, 수행단계 : {1}".format(str(imgPath), self.state))
    #             self.currentState() #   해당이미지 발견시 마우스 동작 제어
    #             break



    def gaussianBlur(self, img):
        image_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 흑백으로 변환
        return cv2.GaussianBlur(image_gray, (5, 5), 0)




# image = cv2.imread('image/1.bmp')
# image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# template = cv2.imread('image/2.bmp', 0)
# w, h = template.shape[::-1]
#
# result = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)
# threshold = 0.95 # 임계치 설정
# box_loc = np.where(result >= threshold) # 임계치 이상의 값들만 사용
#
# for box in zip(*box_loc[::-1]):
#     startX, startY = box
#     endX, endY = startX + w, startY + h
#     cv2.rectangle(image, (startX, startY), (endX, endY), (0,0,255), 1)
#
# cv2.imwrite('result.png', image)

