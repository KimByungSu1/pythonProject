import socketserver, socket

from PyQt5.QtCore import *
from PyQt5.QtNetwork import *

HOST = '192.168.1.143'
PORT = 5050
SIZE = 1024
ADDR = (HOST, PORT)
SIZEOF_UINT32 = 4

class myServerClient(QThread):
    serverlLog = pyqtSignal(str)  # 서버 이벤트 시그널
    def __init__(self):
        QThread.__init__(self)
        self.isServer = False
        pass

    def run(self):
        self.isServer ^= True
        with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server.serve_forever()

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())