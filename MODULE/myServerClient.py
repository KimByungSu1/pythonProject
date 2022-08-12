import socketserver, socket, asyncio
import time

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
        self.server = None
        self.threads = []

    def __del__(self):
        # self.stop()
        pass

    def run(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.server.bind(ADDR)
        except Exception as e:
            self.rcvMsgLog.emit('Bind Error : ' + str(e))
            return False
        else:
            self.server.listen()
            self.rcvMsgLog.emit('Server Listening...')
            while True:
                self.rcvMsgLog.emit("Multithreaded Python server : Waiting for connections from TCP clients...")
                (client, addr) = self.server.accept()
                newthread = ClientThread(client, addr)
                newthread.start()
                self.threads.append(newthread)

    def stop(self):
        if self.isRunning():
            self.server.close()
            print('Server stop')


class ClientThread(QThread):

    def __init__(self, client, addr):
        QThread.__init__(self)
        self.client = client
        self.addr = addr
        print(client)
        print(addr)
        print("[+] New server socket thread started for : ")

    def __del__(self):
        self.stop()

    def run(self):
        while True:
            data = self.client.recv(1024)
            print(data)

    def stop(self):
        if self.isRunning():
            self.client.close()
            print('Client stop')



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
