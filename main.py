import sys, os, datetime

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

        self.mySerial = mySerial()  # 시리얼포트 객체 생성
        self.searchImg = myOpenCV()
        self.searchImg.start()

        self.timer = QTimer()
        self.timer.start(100)  #   1초마다
        self.timer.timeout.connect(self.timer100msec)

        self.toggle = 0

        self.posX = 0
        self.posY = 0

        for idx, val in enumerate(self.mySerial.availablePorts()):  #   사용가능한 포트 확인
            self.ui.cb_comport.addItem(val)

        for i, baud in enumerate(serial.Serial.BAUDRATES):  # 9600이상 사용가능한 Baud rate 콤보 박스에 추가
            if (baud >= 9600):
                self.ui.cb_baudRate.addItem(str(baud))
            if (baud == 115200):
                self.ui.cb_baudRate.setCurrentIndex(4)      #   콤보박스 시작시 115200으로 시작하기

        # BUTTONS
        self.ui.pb_open.clicked.connect(self.buttonClick)

        # 이미지 서치 결과
        self.searchImg.searchPos.connect(self.searchImageResult)

        # 시리얼 수신
        self.mySerial.serialLog.connect(self.serialLog)
    def timer100msec(self):
        self.ui.le_posX.setText(str(pyautogui.position().x))
        self.ui.le_posY.setText(str(pyautogui.position().y))


    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()
        if btnName == "pb_open":
            if self.mySerial.serialOpen(self.ui.cb_comport.currentText(), self.ui.cb_baudRate.currentText()) == True:  # 시리얼 오픈
                self.mySerial.start()  # 쓰레드 시작

            self.ui.pb_open.setText({False: 'Open', True: 'Close'}[self.mySerial.isOpen])  # Port 상태에 따라 Open ↔ Close 버튼 글자 바꾸기

    @pyqtSlot(tuple)
    def searchImageResult(self, pos):
        if self.searchImg.programX != 0:
            self.ui.le_progX.setText(str(self.searchImg.programX))
            self.ui.le_progY.setText(str(self.searchImg.programY))

        self.posX = int(pos[0] - pyautogui.position().x)
        self.posY = int(pos[1] - pyautogui.position().y)

        if self.mySerial.isOpen:
            #print("$MOUSE,{0},{1},*\r\n".format(self.posX, self.posY))
            self.mySerial.txData("$MOUSE,{0},{1},*00\r\n".format(self.posX, self.posY))

    def serialLog(self, evtSerialLog):  #   시리얼 통신 로그
        print(evtSerialLog)





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


# import sys, os, datetime
#
# from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *
# from PyQt5.QtCore import Qt
#
# from UI.test import *                   #   Qt디자이너로 만든 UI
# from MODULE.mySerial import *           #   user Serial
# from MODULE.myAuto import *             #   user Auto
# from MODULE.myServerClient import *      #   user Server Client
# from MODULE.myKeyboardMouse import *      #   user 키보드 마우스 이벤트
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         QMainWindow.__init__(self)
#         self.ui = Ui_MainWindow()
#         self.ui.setupUi(self)       # Qt디자이너로 생성된 UI
#         self.show()
#         self.mySerial = mySerial()      #   시리얼포트 객체 생성
#         self.myAuto = myAuto()          #   오토 객체 생성
#         self.myServer = myServer()      #   서버 객체 생성
#         self.myKeyboardMouse = myKeyboardMouse()  # 키보드 마우스 이벤트 처리
#
#
#         for idx, val in enumerate(self.mySerial.availablePorts()):  #   사용가능한 포트 확인
#             self.ui.cb_PORT.addItem(val)
#
#         # BUTTONS
#         self.ui.pb_Open.clicked.connect(self.buttonClick)
#         self.ui.pb_Connect.clicked.connect(self.buttonClick)
#         self.ui.pb_loadImage1.clicked.connect(self.buttonClick)
#         self.ui.pb_keyEventRecord.clicked.connect(self.buttonClick)
#
#         # lineEdit
#         self.ui.le_txCommand.returnPressed.connect(self.lineEditEnter)
#
#         # 시리얼
#         self.mySerial.serialRead.connect(self.serialRead)
#         self.mySerial.serialLog.connect(self.serialLog)
#
#         #   오토
#         self.myAuto.autoLog.connect(self.autoLog)
#
#         #   서버
#         self.myServer.rcvMsgLog.connect(self.serverLog)
#
#         #   키보드 마우스 이벤트
#         self.myKeyboardMouse.keyLog.connect(self.keyLog)
#         self.myKeyboardMouse.keyRecordLog.connect(self.keyRecordLog)
#
#
#     def buttonClick(self):
#         # GET BUTTON CLICKED
#         btn = self.sender()
#         btnName = btn.objectName()
#
#         if btnName == "pb_keyEventRecord":
#             if self.myKeyboardMouse.isKey == False:
#                 self.myKeyboardMouse.isKey = True
#                 self.ui.te_keyEvent.clear()
#                 self.myKeyboardMouse.start()        #   키보드 이벤트 기록 시작
#             else:
#                 self.myKeyboardMouse.isKey = False  #   키보드 이벤트 기록 종료
#
#             self.ui.pb_keyEventRecord.setText({False: '매크로 설정 시작', True: '기록중...'}[self.myKeyboardMouse.isKey])
#
#         if btnName == "pb_Open":
#             if self.mySerial.serialOpen(self.ui.cb_PORT.currentText()) == True:    #   시리얼 오픈
#                 self.mySerial.start()   #   쓰레드 시작
#                 self.myAuto.start()
#             else:
#                 self.myAuto.isAuto = False
#
#             self.ui.pb_Open.setText({False: 'Open', True: 'Close'}[self.mySerial.isOpen])  # Port 상태에 따라 Open ↔ Close 버튼 글자 바꾸기
#
#         if btnName == "pb_Connect":
#             self.myServer.start()
#             self.myServer.clientInfo()
#             # self.ui.pb_Connect.setText({False: 'Connect', True: 'Disconnect'}[self.myServer.isServerOpen])  # server 상태에 따라 connect ↔ Disconnect 버튼 글자 바꾸기
#
#         if btnName == "pb_loadImage1":
#             fName = QFileDialog.getOpenFileName(self, 'Open File', './', 'Image File(*.png *.bmp *.jpg);;', options=QFileDialog.DontUseNativeDialog)  #   이미지 파일 불러오기
#
#             if fName[0]:    #   이미지 파일 경로
#                 pixmap = QPixmap(fName[0])
#                 self.ui.lb_image1.setPixmap(pixmap)
#
#     def lineEditEnter(self):
#         # GET BUTTON CLICKED
#         lineEdit = self.sender()
#         editName = lineEdit.objectName()
#
#         if editName == "le_txCommand":
#             self.mySerial.txData(self.ui.le_txCommand.text())
#             self.ui.le_txCommand.clear()
#
#     def serialLog(self, evtSerialLog):  #   시리얼 통신 로그
#         nowTime = datetime.datetime.now().strftime('(%H:%M:%S:%f')[:-3] + ')' + " : "  # 송,수신 시간 기록
#         self.ui.textEdit.append(nowTime + evtSerialLog)
#
#     def serialRead(self, rcvData):      #   시리얼 통신 이벤트
#         self.ui.textEdit.append(rcvData)
#
#     def serverLog(self, evtServerLog):      #   서버 클라이언트 이벤트
#         nowTime = datetime.datetime.now().strftime('(%H:%M:%S:%f')[:-3] + ')' + " : "  # 송,수신 시간 기록
#         self.ui.textEdit.append(nowTime + evtServerLog)
#
#     def keyLog(self, key):          #   키보드 마우스 이벤트
#         self.ui.te_keyEvent.append(key)
#         self.ui.pb_keyEventRecord.setText({False: '매크로 설정 시작', True: '기록중...'}[self.myKeyboardMouse.isKey])
#
#     def keyRecordLog(self, keyRecord):          #   키보드 마우스 기록 이벤트
#         print(keyRecord)
#         retStr = ''.join(keyRecord)
#         print(retStr)
#         self.mySerial.txData(retStr)
#
#     def autoLog(self, evtAutoLog):  # 오토 이벤트
#         nowTime = datetime.datetime.now().strftime('(%H:%M:%S:%f')[:-3] + ')' + " : "  # 송,수신 시간 기록
#         self.ui.textEdit.append(nowTime + evtAutoLog)
#         self.ui.textEdit.append(''.join(self.myKeyboardMouse.recordKey[:-2]))
#
#         #self.ui.textEdit.append(''.join(self.myKeyboardMouse.recordKey))
#
#
# # SETTINGS WHEN TO START
# # Set the initial class and also additional parameters of the "QApplication" class
# # ///////////////////////////////////////////////////////////////
# if __name__ == "__main__":
#     # APPLICATION
#     # ///////////////////////////////////////////////////////////////
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     # EXEC APP
#     # ///////////////////////////////////////////////////////////////
#     sys.exit(app.exec())