import socketserver, socket, asyncio
import sys
import time
import traceback
from threading import Thread

from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
HOST = socket.gethostbyname(socket.gethostname())
print(HOST)
PORT = 502
SIZE = 1024
ADDR = (HOST, PORT)
SIZEOF_UINT32 = 4

# class clientThread(QThread):
#     clientMsgLog = pyqtSignal(str)  # 시리얼 이벤트 시그널
#
#     def __init__(self, clientAddress, clientsocket):
#         QThread.__init__(self)
#         self.csocket = clientsocket
#         self.caddress = clientAddress
#         print("New connection added : ", clientAddress)
#
#     def run(self):
#         print("Connection from : ", self.caddress)
#         #self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
#         msg = ''
#         while True:
#             data = self.csocket.recv(2048)
#             msg = data.decode()
#             if msg=='':     #   클라이언트 측에서 접속 종료시 공백문자 수신됨
#                 break
#
#             print("from client", msg)
#             self.csocket.send(bytes(msg, 'UTF-8'))
#         self.csocket.close()
#         # self.clientMsgLog.emit("disconnected...")
#         print("Client at ", self.caddress, " disconnected...")

class clientThread(QObject):
    clientMsgLog = pyqtSignal(str)  # 시리얼 이벤트 시그널

    def __init__(self, clientAddress, clientsocket):
        super().__init__(self)
        self.csocket = clientsocket
        self.caddress = clientAddress
        print("New connection added : ", clientAddress)

    def run(self):
        print("Connection from : ", self.caddress)
        #self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        while True:
            data = self.csocket.recv(2048)
            msg = data.decode()
            if msg=='':     #   클라이언트 측에서 접속 종료시 공백문자 수신됨
                break

            print("from client", msg)
            self.csocket.send(bytes(msg, 'UTF-8'))
        self.csocket.close()
        # self.clientMsgLog.emit("disconnected...")
        print("Client at ", self.caddress, " disconnected...")

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
            server_socket.bind(ADDR)  # 주소 바인딩
            server_socket.listen()  # 클라이언트의 요청을 받을 준비

            # 무한루프 진입
            while True:
                client_socket, client_addr = server_socket.accept()  # 수신대기, 접속한 클라이언트 정보 (소켓, 주소) 반환
                t = Thread(target=self.receive, args=(client_addr, client_socket))
                self.th.append(t)
                self.client.append(client_socket)
                self.address.append(client_addr)
                t.start()

                # msg = client_socket.recv(SIZE)  # 클라이언트가 보낸 메시지 반환
                # print("[{}] message : {}".format(client_addr, msg))  # 클라이언트가 보낸 메시지 출력
                #
                # client_socket.sendall("welcome!".encode())  # 클라이언트에게 응답
                #
                # client_socket.close()  # 클라이언트 소켓 종료
    def receive(self, clientAddress, clientSocket):
        self.rcvMsgLog.emit("Connection from : {0}".format(clientAddress))
        while True:
            data = clientSocket.recv(2048)
            msg = data.decode()
            if msg == '':  # 클라이언트 측에서 접속 종료시 공백문자 수신됨
                break
            self.rcvMsgLog.emit("from {0} : {1}".format(clientAddress, msg))
            clientSocket.send(bytes(msg, 'UTF-8'))

        clientSocket.close()
        self.rcvMsgLog.emit("Client at : {0} disconnected...".format(clientAddress))

        for idx, cli in enumerate(self.client):
            if cli == clientSocket:
                print(idx)
                print(cli)
                #self.client.remove(idx+1)

        #for idx, addr in enumerate(self.address):
        #    if addr == clientAddress:
        #        self.address.remove(idx+1)

    def clientInfo(self):
        print(self.client)
        print(self.address)
        print(self.th)

    def clientDisconnect(self, msg):
        print(msg)


# class myServer(QThread):
#     rcvMsgLog = pyqtSignal(str)  # 시리얼 이벤트 시그널
#
#     def __init__(self):
#         QThread.__init__(self)
#         self.server = None
#         self.isServerOpen = False
#         self.threads = []
#         self.client = []
#
#     def run(self):
#         self.server.listen()
#         while self.isServerOpen:
#             self.rcvMsgLog.emit("Multithreaded Python server : Waiting for connections from TCP clients...")
#             (client, addr) = self.server.accept()
#             self.client.append(client)
#             newthread = clientThread(addr, client)
#             newthread.start()
#             self.threads.append(newthread)
#         self.server.close()
#
#     def serverOpen(self):
#         if self.isServerOpen == False:
#             self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#
#             try:
#                 self.server.bind(ADDR)
#             except Exception as e:
#                 self.rcvMsgLog.emit('Bind Error : ' + str(e))
#                 self.isServerOpen = False
#             else:
#                 self.rcvMsgLog.emit('Server Listening...')
#                 self.isServerOpen = True
#                 return self.isServerOpen
#         else:
#             if self.client:
#                 for c in self.client:
#                     c.close()
#                 self.client.clear()
#             self.isServerOpen = False





# class myServer(QThread):
#     rcvMsgLog = pyqtSignal(str)  # 시리얼 이벤트 시그널
#
#     def __init__(self):
#         QThread.__init__(self)
#
#     def __del__(self):
#         self.stop()
#
#     def run(self):
#         asyncio.run(self.run_server())
#
#     def stop(self):
#         print('stop')
#
#     async def run_server(self):
#         server = await asyncio.start_server(self.handle_client, HOST, PORT)
#         async with server:
#             await server.serve_forever()
#
#     async def handle_client(self, reader, writer):
#         request = None
#         while request != 'quit':
#             request = (await reader.read(255)).decode('utf8')
#             self.rcvMsgLog.emit(request)
#             writer.write(request.encode('utf8'))
#             await writer.drain()
#             print(request)
#         writer.close()
