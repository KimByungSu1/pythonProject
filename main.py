import sys, pyautogui
from PyQt5.QtWidgets import *

from UI.test import *              #   Qt디자이너로 만든 UI
from MODULE.mySerial import *      #   user Serial
from MODULE.myWin32API import *    #   user Win32 API
from MODULE.myOpenCV import *      #   user OpenCV

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Qt디자이너로 생성된 UI
        self.show()
        self.mySerial = mySerial()  #   시리얼포트 객체 생성
        self.myWin32API = myWin32API()

        for win in self.myWin32API.getWindowList():
           if (win[0] == 'Gersang'):
                print(self.myWin32API.getWindowRect(win[1]))

        button5location = pyautogui.locateOnScreen('./TARGET_IMAGE/COMMON/asd.png')  # 이미지가 있는 위치를 가져옵니다.
        center = pyautogui.center(button5location)
        pyautogui.moveTo(center)


        for idx, val in enumerate(self.mySerial.availablePorts()):  #   사용가능한 포트 확인
            self.ui.comboBox.addItem(val)

        # BUTTONS
        self.ui.pushButton_2.clicked.connect(self.buttonClick)

    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        if btnName == "pushButton_2":
            if self.mySerial.serialOpen(self.ui.comboBox.currentText()) == True:    #   시리얼 오픈
                self.mySerial.start()   #   쓰레드 시작
            self.ui.pushButton_2.setText({False: 'Connect', True: 'Disconnect'}[self.mySerial.isOpen])  # Port 상태에 따라 Connect ↔ Disconnect 버튼 글자 바꾸기





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