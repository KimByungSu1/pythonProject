import serial, serial.tools.list_ports, queue

from PyQt5.QtCore import *

TIME_OUT = 0.01
ports = serial.tools.list_ports.comports(include_links=False)

class mySerial(QThread):
    serialRead = pyqtSignal(str)  # 시리얼 수신 완료시 시그널
    serialLog = pyqtSignal(str)  # 시리얼 이벤트 시그널

    def __init__(self):
        QThread.__init__(self)
        self.mySerial = serial.Serial()  # 시리얼 관련 객체 생성
        self.isOpen = False
        self.txBuf = queue.Queue()  # 송신 버퍼

    def run(self):
        while self.isOpen == True:
            buf = self.mySerial.readall()

            if buf:  # 수신 Data 존재시

                print(buf)
                print(buf.decode('latin-1', errors='backslashreplace'))
                self.serialRead.emit(buf.decode('latin-1', errors='backslashreplace'))

            if self.txBuf.empty() == False:  # 송신버퍼에 데이터가 있으면
                txd = chr(0x1E) + self.txBuf.get() + chr(0x1F)   # 시작문자 0x02, 종료문자 0x03
                self.mySerial.write(txd.encode(encoding='UTF-8'))       # 시리얼 데이터 전송
                # self.serialLog.emit(txd)              #   송신 로그 남기기


    def availablePorts(self):       #   사용가능한 포트 검색후 리스트 형식으로 반환
        returnAvailablePorts = []
        for port in ports:
            returnAvailablePorts.append(port.device)
        return returnAvailablePorts

    def txData(self, tx):       #   사용가능한 포트 검색후 리스트 형식으로 반환
        self.txBuf.put(tx)

    def serialOpen(self, COMPORT):  #   시리얼 포트 Open/Close
        try:
            if self.isOpen == False:
                self.mySerial.port = COMPORT  # combobox에 있는 컴포트
                self.mySerial.baudrate = 9600  # baudRate
                self.mySerial.timeout = TIME_OUT
                self.mySerial.open()  # 포트 열기
                self.isOpen = True
                self.serialLog.emit('Serial Open')
            else:
                self.isOpen = False
                self.serialLog.emit('Serial Close')
                self.mySerial.close()  # 포트 닫기

        except serial.SerialException as e:
            self.isOpen = False
            self.serialLog.emit(e)

        return self.isOpen