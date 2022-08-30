import socket
import threading

from PyQt5.QtCore import *

HOST = socket.gethostbyname(socket.gethostname())
PORT = 502
SIZE = 1024
ADDR = (HOST, PORT)
SIZEOF_UINT32 = 4


class myServer(QThread):
    rcvMsgLog = pyqtSignal(str)  # 시리얼 이벤트 시그널

    def __init__(self):
        QThread.__init__(self)
        self.client = []
        self.address = []
        self.th = []

    def run(self):
        # 서버 소켓 설정
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(ADDR)  # 주소 바인딩
            server_socket.listen()  # 클라이언트의 요청을 받을 준비
            # 무한루프 진입
            while True:
                client_socket, client_addr = server_socket.accept()  # 수신대기, 접속한 클라이언트 정보 (소켓, 주소) 반환
                t = threading.Thread(target=self.receive, args=(client_addr, client_socket))
                self.th.append(t)   #   클라이언트 쓰레드 정보
                self.client.append(client_socket)   #   클라이언트 소켓정보
                self.address.append(client_addr)    #   클라이언트 IP정보
                t.daemon = True  # 프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
                t.start()

    def receive(self, clientAddress, clientSocket):
        self.rcvMsgLog.emit("New connection added : {0}".format(clientAddress))
        self.rcvMsgLog.emit("Connection from : {0}".format(clientAddress))
        while True:
            data = clientSocket.recv(2048)
            msg = data.decode()
            if msg == '':  # 클라이언트 측에서 접속 종료시 지속적으로 공백문자 수신됨
                break
            self.rcvMsgLog.emit("from {0} : {1}".format(clientAddress, msg))
            clientSocket.send(msg.encode())

        clientSocket.close()    #   클라이언트 접속 종료시
        self.rcvMsgLog.emit("Client at : {0} disconnected...".format(clientAddress))    #   클라이언트 종료메시지
        for idx, cli in enumerate(self.client): #   클라이언트 관련 접속 기록 삭제
            if cli == clientSocket:
                del self.client[idx]    #   소켓정보 삭제
                del self.address[idx]   #   IP정보 삭제
                del self.th[idx]        #   쓰레드 정보 삭제

    def clientInfo(self):
        print(self.client)
        print(self.address)
        print(self.th)
        print(threading.current_thread())
