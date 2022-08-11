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

    def __del__(self):
        self.stop()

    def run(self):
        asyncio.run(self.run_server())

    def stop(self):
        print('stop')

    async def run_server(self):
        server = await asyncio.start_server(self.handle_client, HOST, PORT)
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        request = None
        while request != 'quit':
            request = (await reader.read(255)).decode('utf8')
            self.rcvMsgLog.emit(request)
            writer.write(request.encode('utf8'))
            await writer.drain()
            print(request)
        writer.close()

# class myServer(QObject):
#     update_signal = pyqtSignal(tuple, bool)
#     recv_signal = pyqtSignal(str)
#
#     def __init__(self):
#         super().__init__()
#         self.bListen = False
#         self.clients = []
#         self.ip = []
#         self.threads = []
#
#     def __del__(self):
#         self.stop()
#
#     def start(self):
#         # 서버 소켓 설정
#         self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         try:
#             self.server.bind((HOST, PORT))
#         except Exception as e:
#             print('Bind Error : ', e)
#             return False
#         else:
#             self.bListen = True
#             self.t = threading.Thread(target=self.listen, args=(self.server,))
#             self.t.start()
#             print('Server Listening...')
#
#     def stop(self):
#         self.bListen = False
#         if hasattr(self, 'server'):
#             self.server.close()
#             print('Server Stop')
#
#     def listen(self, server):
#         while self.bListen:
#             server.listen(5)
#             try:
#                 client, addr = server.accept()
#             except Exception as e:
#                 print('Accept() Error : ', e)
#                 break
#             else:
#                 self.clients.append(client)
#                 self.ip.append(addr)
#                 self.update_signal.emit(addr, True)
#                 t = threading.Thread(target=self.receive, args=(addr, client))
#                 self.threads.append(t)
#                 t.start()
#
#         self.removeAllClients()
#         self.server.close()
#
#     def receive(self, addr, client):
#         print('receive')
#         while True:
#             try:
#                 recv = client.recv(1024)
#             except Exception as e:
#                 print('Recv() Error :', e)
#                 break
#             else:
#                 msg = str(recv, encoding='utf-8')
#                 if msg:
#                     self.send(msg)
#                     self.recv_signal.emit(msg)
#                     print('[RECV]:', addr, msg)
#
#         self.removeClient(addr, client)
#
#     def send(self, msg):
#         try:
#             for c in self.clients:
#                 c.send(msg.encode())
#         except Exception as e:
#             print('Send() Error : ', e)
#
#     def removeClient(self, addr, client):
#         # find closed client index
#         idx = -1
#         for k, v in enumerate(self.clients):
#             if v == client:
#                 idx = k
#                 break
#
#         client.close()
#         self.ip.remove(addr)
#         self.clients.remove(client)
#
#         del (self.threads[idx])
#         self.update_signal.emit(addr, False)
#         self.resourceInfo()
#
#     def removeAllClients(self):
#         for c in self.clients:
#             c.close()
#
#         for addr in self.ip:
#             self.update_signal.emit(addr, False)
#
#         self.ip.clear()
#         self.clients.clear()
#         self.threads.clear()
#
#         self.resourceInfo()
#
#     def resourceInfo(self):
#         print('Number of Client ip\t: ', len(self.ip))
#         print('Number of Client socket\t: ', len(self.clients))
#         print('Number of Client thread\t: ', len(self.threads))