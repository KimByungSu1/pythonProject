import sys, serial, cv2
from PyQt5.QtWidgets import *

from UI.test import *              #   Qt디자이너로 만든 UI
from MODULE.mySerial import *      #   사용자 Module


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Qt디자이너로 생성된 UI
        self.show()
        self.mySerial = mySerial()  #   시리얼포트 객체 생성

        for idx, val in enumerate(self.mySerial.availablePorts()):  #   사용가능한 포트 확인
            self.ui.comboBox.addItem(val)

        # BUTTONS
        self.ui.pushButton_2.clicked.connect(self.buttonClick)

    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        if btnName == "pushButton_2":
            if self.mySerial.serialOpen(self.ui.comboBox.currentText()) == True:
                self.mySerial.start()






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