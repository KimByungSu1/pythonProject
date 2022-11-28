import sys, os, datetime
import time

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt

from UI.test import *                   #   Qt디자이너로 만든 UI
from MODULE.myOpenCV import *           #   user Serial
from MODULE.mySerial import *           #   user Serial
from MODULE.myAuto import *             #   user Auto
from MODULE.myFile import *             #   user file save
from MODULE.myServerClient import *      #   user Server Client
from MODULE.myKeyboardMouse import *      #   user 키보드 마우스 이벤트


# startMMSI = 44070
# endMMSI = 44101
# count = 0
#
# txtDic = {}
# imgDic = {}
#
# resultTotalCount = 0
# resultImgTotalCount = 0
#
#
# path = r'C:\Users\BSK\Downloads\25'
# file_list = os.listdir(path)
# file_list_py = [file for file in file_list if file.endswith("44070.txt")]
#
# for length in range(0, endMMSI-startMMSI):
#     count = 0
#     for file in file_list:
#         if file.endswith("{0}.txt".format(startMMSI)):
#             #print(startMMSI, file)
#             count = count + 1
#     txtDic[startMMSI] = count
#     resultTotalCount = resultTotalCount + count
#     startMMSI = startMMSI + 1
#
# startMMSI = 44070
# for length in range(0, endMMSI-startMMSI):
#     count = 0
#     for file in file_list:
#         if file.endswith("{0}-1.jpg".format(startMMSI)):
#             #print(startMMSI, file)
#             count = count + 1
#         if file.endswith("{0}-2.jpg".format(startMMSI)):
#             #print(startMMSI, file)
#             count = count + 1
#         if file.endswith("{0}-3.jpg".format(startMMSI)):
#             #print(startMMSI, file)
#             count = count + 1
#     imgDic[startMMSI] = count
#     resultImgTotalCount = resultImgTotalCount + count
#     startMMSI = startMMSI + 1
#
# print('MMSI 국소별 시정 센서 수신 카운트 : ', txtDic.values())
# print('MMSI 국소별 이미지 수신 카운트 : ', imgDic.values())
# print('txt file total count : ', resultTotalCount)
# print('image1 file total count : ', resultImgTotalCount)
# print('total img txt file : ', resultTotalCount + resultImgTotalCount)
#print ("file_list_py: {0}".format(file_list_py))
#print ("file_list_44070: {0}".format(len(file_list_py)))


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)       # Qt디자이너로 생성된 UI
        self.show()

        self.move(10, 10)            #   프로그램 실행시 시작위치 10,10 으로 이동

        self.timer = QTimer()
        self.timer.start(100)  #   1초마다
        self.timer.timeout.connect(self.timer100msec)

        self.mySerial = mySerial()  # 시리얼포트 객체 생성
        self.myAuto = myAuto()

        self.ui.pb_start.setShortcut('F10')
        for idx, val in enumerate(self.mySerial.availablePorts()):  #   사용가능한 포트 확인
            self.ui.cb_comport.addItem(val)
            self.ui.cb_comport.setCurrentIndex(idx)

        # for i, baud in enumerate(serial.Serial.BAUDRATES):  # 9600이상 사용가능한 Baud rate 콤보 박스에 추가
        #     if (baud >= 9600):
        #         self.ui.cb_baudRate.addItem(str(baud))
        #     if (baud == 115200):
        #         self.ui.cb_baudRate.setCurrentIndex(4)      #   콤보박스 시작시 115200으로 시작하기

        if self.ui.cb_battleMapList.currentText() == '흑룡담':
            self.myAuto.battlePath = r'.\IMAGE\BATTLE\BLACK_DRAGON_MAP'


        # BUTTONS
        self.ui.pb_start.clicked.connect(self.buttonClick)
        self.ui.pb_restart.clicked.connect(self.buttonClick)
        self.ui.pb_client_1.clicked.connect(self.buttonClick)
        self.ui.pb_client_2.clicked.connect(self.buttonClick)
        self.ui.pb_client_3.clicked.connect(self.buttonClick)

        # 오토 동작 결과
        self.myAuto.autoLog.connect(self.autoLog)
        self.myAuto.autoSendReport.connect(self.sendCommand)
        self.myAuto.gameInfoLog.connect(self.gameInfoLog)

        # 시리얼 수신
        self.mySerial.serialLog.connect(self.serialLog)

    def timer100msec(self):
        self.ui.le_posX.setText(str(pyautogui.position().x))
        self.ui.le_posY.setText(str(pyautogui.position().y))

        if self.ui.chkb_jamsu.isChecked():
            self.myAuto.jamsu = 1

        if self.ui.chkb_deathHero.isChecked():
            self.myAuto.deathHero = 1

        if self.ui.chkb_telegram.isChecked():
            self.myAuto.ChkTelegram = 1

    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()
        
        if btnName == "pb_restart":     #   프로그램 재시작
            QtCore.QCoreApplication.quit()
            status = QtCore.QProcess.startDetached(sys.executable, sys.argv)

        if btnName == "pb_start":
            if self.mySerial.serialOpen(self.ui.cb_comport.currentText(), 115200) == True:  # 시리얼 오픈
                self.mySerial.start()  # 쓰레드 시작
                self.myAuto.start()
            else:
                self.myAuto.stop()
            self.ui.pb_start.setText({False: '시작', True: '정지'}[self.mySerial.isOpen])  # Port 상태에 따라 Open ↔ Close 버튼 글자 바꾸기

        if btnName == "pb_client_1":    #   1번클라이언트 핸들 지정하기
            if self.myAuto.clientInfo[0]['Handle']:
                self.myAuto.set_foreground(self.myAuto.clientInfo[0]['Handle'])
                self.ui.le_handle_1.setText(str(self.myAuto.clientInfo[0]['Handle']))
                self.myAuto.clientInfo[0]['Attacker'] = self.ui.cb_attacker_1.currentText()
                self.myAuto.clientInfo[0]['Tanker'] = self.ui.cb_tanker_1.currentText()
                self.myAuto.clientInfo[0]['supporter'] = self.ui.cb_support_1.currentText()

        if btnName == "pb_client_2":    #   2번클라이언트 핸들 지정하기
            if self.myAuto.clientInfo[1]['Handle']:
                self.ui.le_handle_2.setText(str(self.myAuto.clientInfo[1]['Handle']))
                self.ui.le_handle_2.setText(str(self.myAuto.clientInfo[1]['Handle']))
                self.myAuto.clientInfo[1]['Attacker'] = self.ui.cb_attacker_2.currentText()
                self.myAuto.clientInfo[1]['Tanker'] = self.ui.cb_tanker_2.currentText()
                self.myAuto.clientInfo[1]['supporter'] = self.ui.cb_support_2.currentText()

        if btnName == "pb_client_3":    #   3번클라이언트 핸들 지정하기
            if self.myAuto.clientInfo[2]['Handle']:
                self.ui.le_handle_3.setText(str(self.myAuto.clientInfo[2]['Handle']))
                self.ui.le_handle_3.setText(str(self.myAuto.clientInfo[2]['Handle']))
                self.myAuto.clientInfo[2]['Attacker'] = self.ui.cb_attacker_3.currentText()
                self.myAuto.clientInfo[2]['Tanker'] = self.ui.cb_tanker_3.currentText()
                self.myAuto.clientInfo[2]['supporter'] = self.ui.cb_support_3.currentText()

    @pyqtSlot(int, list)
    def gameInfoLog(self, idx, Info):

        for x in range(0, idx):
            status = {0: '대기중', 1: '전투대기중', 2: '전투중'}
            if x == 0:
                self.ui.le_status_1.setText(status[Info[x].Status])
                self.ui.le_battleCount_1.setText(str(Info[x].BattleTotalCount))
                self.ui.le_snackCount_1.setText(str(Info[x].EatCount))
            if x == 1:
                self.ui.le_status_2.setText(status[Info[x].Status])
                self.ui.le_battleCount_2.setText(str(Info[x].BattleTotalCount))
                self.ui.le_snackCount_2.setText(str(Info[x].EatCount))
            if x == 2:
                self.ui.le_status_3.setText(status[Info[x].Status])
                self.ui.le_battleCount_3.setText(str(Info[x].BattleTotalCount))
                self.ui.le_snackCount_3.setText(str(Info[x].EatCount))

    @pyqtSlot(str)
    def sendCommand(self, tx):
        self.mySerial.txData(tx)

    @pyqtSlot(int, str)
    def autoLog(self, ch, log):
        if ch == 0: #   1번 클라이언트
            if (len(self.ui.te_clientLog_1.toPlainText())) > 60000:  # history log가 x만줄 이상이면
                self.ui.te_clientLog_1.clear()  # ASCII tx 로그 초기화

            self.ui.te_clientLog_1.append(log)

        if ch == 1: #   2번 클라이언트
            if (len(self.ui.te_clientLog_2.toPlainText())) > 60000:  #  log가 x만줄 이상이면
                self.ui.te_clientLog_2.clear()  # ASCII tx 로그 초기화

            self.ui.te_clientLog_2.append(log)

        if ch == 2: #   3번 클라이언트
            if (len(self.ui.te_clientLog_3.toPlainText())) > 60000:  # history log가 x만줄 이상이면
                self.ui.te_clientLog_3.clear()  # ASCII tx 로그 초기화

            self.ui.te_clientLog_3.append(log)

    def serialLog(self, evtSerialLog):  #   시리얼 통신 로그
        splitString = evtSerialLog.split(',')

        if splitString[0] == '$MOUSE':
            pass

        if splitString[0] == '$KEYBOARD':
            pass




# SETTINGS WHEN TO START
# Set the initial class and also additional parameters of the "QApplication" class
# ///////////////////////////////////////////////////////////////
if __name__ == "__main__":
    # APPLICATION
    # ///////////////////////////////////////////////////////////////
    app = QApplication(sys.argv)
    window = MainWindow()
    # EXEC APP
    # ///////////////////////////////////////////////////////////////
    sys.exit(app.exec())


