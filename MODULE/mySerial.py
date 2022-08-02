import time, datetime

import serial, serial.tools.list_ports

from PyQt5.QtCore import QThread

TIME_OUT = 0.01
ports = serial.tools.list_ports.comports(include_links=False)

class mySerial(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.mySerial = serial.Serial()  # 시리얼 관련 객체 생성
        self.isOpen = False

    def run(self):
        while self.isOpen == True:
            buf = self.mySerial.readall()
            nowTime = datetime.datetime.now().strftime('(%H:%M:%S:%f')[:-3] + ')'  # 송,수신 시간 기록

            if buf:  # 수신 Data 존재시
                print(nowTime)
        print('serial Thread Stop!!')

    def availablePorts(self):
        returnAvailablePorts = []
        for port in ports:
            returnAvailablePorts.append(port.device)
        return returnAvailablePorts

    def serialOpen(self, COMPORT):
        try:
            if self.isOpen == False:
                self.mySerial.port = COMPORT  # combobox에 있는 컴포트
                self.mySerial.baudrate = 9600  # baudRate
                self.mySerial.timeout = TIME_OUT
                self.mySerial.open()  # 포트 열기
                self.isOpen = True
                print('Serial Open')
            else:
                self.isOpen = False
                print('Serial Close')
                self.mySerial.close()  # 포트 닫기


        except serial.SerialException as e:
            self.isOpen = False
            print(e)

        return self.isOpen