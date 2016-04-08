import unittest
import readWriteSocket
import socket
import threading




class TestClient(threading.Thread):
    '''
    Mock client for testing
    '''

    IP = '127.0.0.1'
    BUFFER_SIZE = 1024

    def __init__(self, message, port):
        self.testClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        self.message = message
        self.connect()
        self.sendMessage()
#        self.response = self.receive()
        self.closeSocket


    def connect(self):
        self.testClientSocket.connect((self.IP, self.port))

    def sendMessage(self):
        self.testClientSocket.sendall(self.message)

    def receive(self):
        self.testClientSocket.recv(self.BUFFER_SIZE)

    def closeSocket(self):
        self.testClientSocket.close()





class TestServer(threading.Thread):

    '''
    Mock TCP server for testing
    '''

    IP = '127.0.0.1'
    message = None

    def __init__(self, portNumber):
        threading.Thread.__init__(self)
        self.portNumber = portNumber
        self.testServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
            self.testServerSocket.bind((self.IP, self.portNumber))
            self.testServerSocket.listen(5)
            connection, address = self.testServerSocket.accept()
            connection.setblocking(1)
            connection.settimeout(1)
            message = ''
            while 1:
                try:
                    message = message + connection.recv(1024)
                except socket.timeout:
                    break
            self.message = message


            connection.send(str(True))
            connection.close()

    def receiveMessage(self):
            self.start()

class TestServerUDP(threading.Thread):
    '''
    UDP server for porxy output test
    '''
    message = None

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.testServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        self.testServerSocket.bind(("127.0.0.1", self.port))
        self.testServerSocket.settimeout(1)
        message = ''

        while  1:
            try:
                data, address = self.testServerSocket.recvfrom(1024)
                message = message + data
            except socket.timeout:
                break

        self.message = message

class TestProxy(threading.Thread):
    '''
    Mock proxy for testing
    '''
    IP = '127.0.0.1'


    def __init__(self, inputPort, outputPort, inputSocket, outputSocket):
        super(TestProxy, self).__init__()
        self.inputSocket = inputSocket
        self.outputSocket = outputSocket
        self.inputPort = inputPort
        self.outputPort = outputPort


    def run(self):
        try:
            readWriteSocket.proxy(self.inputSocket, self.IP, self.inputPort, self.outputSocket, self.IP, self.outputPort)
        except socket.error, e:
            raise e

class UpdClient():

    IP = "127.0.0.1"

    def __init__(self, message, port):
        self.message = message
        self.port = port
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send()

    def send(self):
        self.clientSock.sendto(self.message, (self.IP, self.port))




#######################################################################################################################
#TEST CASES



class TCPproxy(unittest.TestCase):
    '''
    Test the full proxy given TCP 2 sockets and port numbers, tests long message and null message
    '''

    message = 16000*'1'
    emptyMessage = ''



    def test_proxy_receive_and_output(self):
        self.proxy_test(self.message)


    def test_proxy_null_message(self):
        self.proxy_test(self.emptyMessage)

    def proxy_test(self, message):
        proxyInputSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxyOutputSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


        testProxy = TestProxy(5001, 5002, proxyInputSocket, proxyOutputSocket)
        testProxy.start()

        testServer = TestServer(5002)
        testServer.receiveMessage()

        testClient = TestClient(message, 5001)

        #WAIT FOR THREADS TO FINISH
        testServer.join()
        testProxy.join()

        self.assertEqual(testClient.message, testServer.message)

class UDPproxy(unittest.TestCase):
    '''
    Test the full proxy given UDP 2 sockets and port numbers, tests long message and null message
    '''

    message = 1024*'1'
    emptyMessage = ''



    def test_proxy_receive_and_output(self):
        self.proxy_test(self.message)


    def test_proxy_null_message(self):
        self.proxy_test(self.emptyMessage)

    def proxy_test(self, message):

        inputSocketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        outputSocketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


        testProxy = TestProxy(5001, 5002, inputSocketUDP, outputSocketUDP)
        testProxy.start()






        server = TestServerUDP(5002)
        server.start()

        UpdClient(message, 5001)


        #WAIT FOR THREADS TO FINISH
        server.join()
        testProxy.join()

        self.assertEqual(message, server.message)



if __name__ == '__main__':
    unittest.main()

