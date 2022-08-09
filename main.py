import sys, os, datetime

from PyQt5.QtWidgets import *

from UI.test import *                   #   Qt디자이너로 만든 UI
from MODULE.mySerial import *           #   user Serial
from MODULE.myAuto import *             #   user Auto
from MODULE.myServerClient import *      #   user Server Client

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)       # Qt디자이너로 생성된 UI
        self.show()
        self.mySerial = mySerial()  #   시리얼포트 객체 생성
        self.myAuto = myAuto()  #   오토 객체 생성

        for idx, val in enumerate(self.mySerial.availablePorts()):  #   사용가능한 포트 확인
            self.ui.comboBox.addItem(val)

        # BUTTONS
        self.ui.pushButton_2.clicked.connect(self.buttonClick)

        # 시리얼
        self.mySerial.serialRead.connect(self.serialRead)
        self.mySerial.serialLog.connect(self.serialLog)

        #   오토
        self.myAuto.autoLog.connect(self.autoLog)



    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        if btnName == "pushButton_2":
            if self.mySerial.serialOpen(self.ui.comboBox.currentText()) == True:    #   시리얼 오픈
                self.mySerial.start()   #   쓰레드 시작
                self.myAuto.initAuto()
            self.ui.pushButton_2.setText({False: 'Open', True: 'Close'}[self.mySerial.isOpen])  # Port 상태에 따라 Open ↔ Close 버튼 글자 바꾸기

    def autoLog(self, evtAutoLog):
        nowTime = datetime.datetime.now().strftime('(%H:%M:%S:%f')[:-3] + ')' + " : "  # 송,수신 시간 기록
        self.ui.textEdit.append(nowTime + evtAutoLog)

    def serialLog(self, evtSerialLog):
        nowTime = datetime.datetime.now().strftime('(%H:%M:%S:%f')[:-3] + ')' + " : "  # 송,수신 시간 기록
        self.ui.textEdit.append(nowTime + evtSerialLog)

    def serialRead(self, rcvData):
        self.ui.textEdit.append(rcvData)













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