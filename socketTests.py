import unittest
import readWriteSocket
import socket
from threading import Thread
import time



class TestClient(Thread):


    IP = '127.0.0.1'
    BUFFER_SIZE = 1024

    def __init__(self, message, port):
        self.testClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        self.message = message
        self.connect()
        self.sendMessage()
        self.response = self.receive()
        self.closeSocket


    def connect(self):
        self.testClientSocket.connect((self.IP, self.port))

    def sendMessage(self):
        self.testClientSocket.sendall(self.message)

    def receive(self):
        self.testClientSocket.recv(self.BUFFER_SIZE)

    def closeSocket(self):
        self.testClientSocket.close()





class TestProxy(Thread):


    IP = '127.0.0.1'
    message = None

    def __init__(self, portNumber):
        Thread.__init__(self)
        self.portNumber = portNumber
        self.testServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
            self.receiveMessage()

    def receiveMessage(self):

            self.testServerSocket.bind((self.IP, self.portNumber))
            self.testServerSocket.listen(5)
            connection, address = self.testServerSocket.accept()

            self.message = readWriteSocket.proxyReceiveMessage(connection)
            connection.send(str(True))
            connection.close()


class TestProxyReceiveMethods(unittest.TestCase):

    def test_proxy_receive_message(self):
        longMessage = 4096 * '0'

        proxy = TestProxy(5002)
        proxy.start()
        client = TestClient(longMessage, 5002)
        proxy.join()

        self.assertEqual(client.message, proxy.message)
        client.closeSocket()


    def test_proxy_receive_message_long_message(self):
        longMessage = 16000 * '1'

        proxy = TestProxy(5001)
        proxy.start()
        client = TestClient(longMessage, 5001)
        proxy.join()

        self.assertEqual(client.message, proxy.message)
        client.closeSocket()






if __name__ == '__main__':
    unittest.main()

