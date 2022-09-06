import sys, os, datetime

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt

from UI.test import *                   #   Qt디자이너로 만든 UI
from MODULE.mySerial import *           #   user Serial
from MODULE.myAuto import *             #   user Auto
from MODULE.myServerClient import *      #   user Server Client
from MODULE.myKeyboardMouse import *      #   user 키보드 마우스 이벤트
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)       # Qt디자이너로 생성된 UI
        self.show()
        self.mySerial = mySerial()      #   시리얼포트 객체 생성
        self.myAuto = myAuto()          #   오토 객체 생성
        self.myServer = myServer()      #   서버 객체 생성
        self.myKeyboardMouse = myKeyboardMouse()  # 키보드 마우스 이벤트 처리


        for idx, val in enumerate(self.mySerial.availablePorts()):  #   사용가능한 포트 확인
            self.ui.cb_PORT.addItem(val)

        # BUTTONS
        self.ui.pb_Open.clicked.connect(self.buttonClick)
        self.ui.pb_Connect.clicked.connect(self.buttonClick)
        self.ui.pb_loadImage1.clicked.connect(self.buttonClick)
        self.ui.pb_keyEventRecord.clicked.connect(self.buttonClick)

        # lineEdit
        self.ui.le_txCommand.returnPressed.connect(self.lineEditEnter)

        # 시리얼
        self.mySerial.serialRead.connect(self.serialRead)
        self.mySerial.serialLog.connect(self.serialLog)

        #   오토
        self.myAuto.autoLog.connect(self.autoLog)

        #   서버
        self.myServer.rcvMsgLog.connect(self.serverLog)

        #   키보드 마우스 이벤트
        self.myKeyboardMouse.keyLog.connect(self.keyLog)


    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        if btnName == "pb_keyEventRecord":
            if self.myKeyboardMouse.isKey == False:
                self.myKeyboardMouse.isKey = True
                self.ui.te_keyEvent.clear()
                self.myKeyboardMouse.start()        #   키보드 이벤트 기록 시작
            else:
                self.myKeyboardMouse.isKey = False  #   키보드 이벤트 기록 종료

            self.ui.pb_keyEventRecord.setText({False: '매크로 설정 시작', True: '기록중...'}[self.myKeyboardMouse.isKey])

        if btnName == "pb_Open":
            if self.mySerial.serialOpen(self.ui.cb_PORT.currentText()) == True:    #   시리얼 오픈
                self.mySerial.start()   #   쓰레드 시작
                self.myAuto.start()
            else:
                self.myAuto.isAuto = False

            self.ui.pb_Open.setText({False: 'Open', True: 'Close'}[self.mySerial.isOpen])  # Port 상태에 따라 Open ↔ Close 버튼 글자 바꾸기

        if btnName == "pb_Connect":
            self.myServer.start()
            self.myServer.clientInfo()
            # self.ui.pb_Connect.setText({False: 'Connect', True: 'Disconnect'}[self.myServer.isServerOpen])  # server 상태에 따라 connect ↔ Disconnect 버튼 글자 바꾸기

        if btnName == "pb_loadImage1":
            fName = QFileDialog.getOpenFileName(self, 'Open File', './', 'Image File(*.png *.bmp *.jpg);;', options=QFileDialog.DontUseNativeDialog)  #   이미지 파일 불러오기

            if fName[0]:    #   이미지 파일 경로
                pixmap = QPixmap(fName[0])
                self.ui.lb_image1.setPixmap(pixmap)

    def lineEditEnter(self):
        # GET BUTTON CLICKED
        lineEdit = self.sender()
        editName = lineEdit.objectName()

        if editName == "le_txCommand":
            self.mySerial.txData(self.ui.le_txCommand.text())
            self.ui.le_txCommand.clear()

    def serialLog(self, evtSerialLog):  #   시리얼 통신 로그
        nowTime = datetime.datetime.now().strftime('(%H:%M:%S:%f')[:-3] + ')' + " : "  # 송,수신 시간 기록
        self.ui.textEdit.append(nowTime + evtSerialLog)

    def serialRead(self, rcvData):      #   시리얼 통신 이벤트
        self.ui.textEdit.append(rcvData)

    def serverLog(self, evtServerLog):      #   서버 클라이언트 이벤트
        nowTime = datetime.datetime.now().strftime('(%H:%M:%S:%f')[:-3] + ')' + " : "  # 송,수신 시간 기록
        self.ui.textEdit.append(nowTime + evtServerLog)

    def keyLog(self, key):          #   키보드 마우스 이벤트
        self.ui.te_keyEvent.append(key)
        self.ui.pb_keyEventRecord.setText({False: '매크로 설정 시작', True: '기록중...'}[self.myKeyboardMouse.isKey])

    def autoLog(self, evtAutoLog):  # 오토 이벤트
        nowTime = datetime.datetime.now().strftime('(%H:%M:%S:%f')[:-3] + ')' + " : "  # 송,수신 시간 기록
        self.ui.textEdit.append(nowTime + evtAutoLog)
        self.ui.textEdit.append(''.join(self.myKeyboardMouse.recordKey[:-2]))
        #self.ui.textEdit.append(''.join(self.myKeyboardMouse.recordKey))


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