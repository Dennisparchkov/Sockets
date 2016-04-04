import unittest
import readWriteSocket
import socket
import threading
import time
import errno
import sys
from StringIO import StringIO



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





class TestServer(threading.Thread):

    '''
    Mock server for testing
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

            self.message = readWriteSocket.proxyReceiveMessage(connection)
            connection.send(str(True))
            connection.close()

    def receiveMessage(self):
            self.start()



class TestProxy(threading.Thread):
    '''
    Mock proxy for testing
    '''
    IP = '127.0.0.1'


    def __init__(self, inputPort, outputPort, inputSocket, outputSocket):
        super(TestProxy, self).__init__()
        self._stop = threading.Event()
        self.inputSocket = inputSocket
        self.outputSocket = outputSocket
        self.inputPort = inputPort
        self.outputPort = outputPort


    def run(self):
        try:
            readWriteSocket.proxy(self.inputSocket, self.IP, self.inputPort, self.outputSocket, self.IP, self.outputPort)
        except socket.error, e:
            raise e
            self._stop.set()


#######################################################################################################################
#TEST CASES


class TestProxyReceiveMethods(unittest.TestCase):
    '''
    test the proxies receive method of different size messages, and timeout and null messages
    '''

    def test_proxy_receive_message(self):
        longMessage = 4096 * '0'

        proxy = TestServer(5002)
        proxy.receiveMessage()
        client = TestClient(longMessage, 5002)
        proxy.join()

        self.assertEqual(client.message, proxy.message)
        client.closeSocket()


    def test_proxy_receive_message_long_message(self):
        longMessage = 16000 * '1'

        proxy = TestServer(5001)
        proxy.receiveMessage()
        client = TestClient(longMessage, 5001)
        proxy.join()

        self.assertEqual(client.message, proxy.message)
        client.closeSocket()

    def test_proxy_receive_timeout_and_null_message(self):
        startTime = time.time()

        shortestMessage = ''


        proxy = TestServer(5001)
        proxy.receiveMessage()
        client = TestClient(shortestMessage, 5001)
        proxy.join()

        endTime = time.time()

        self.assertEqual(shortestMessage, proxy.message)
        self.assertTrue(endTime - startTime > 1)
        client.closeSocket()

    def test_proxy_receive_null(self):
        emptyMessage = ''

        proxy = TestServer(5001)
        proxy.receiveMessage()
        client = TestClient(emptyMessage, 5001)

        proxy.join()
        client.closeSocket()
        self.assertEqual(emptyMessage, proxy.message)


class TestProxyOutputMethods(unittest.TestCase):

    '''
    Test the proxies output methods including erros du to connection, null messages and normal messages
    '''

    message = 4096*'0'
    nullMessage = ''

    def test_proxy_output_normal(self):
        testServr = TestServer(5001)
        testServr.receiveMessage()

        outputsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        outputsocket.connect(('127.0.0.1', 5001))
        readWriteSocket.proxyOutput(outputsocket, self.message)

        testServr.join()
        outputsocket.close()

        self.assertEqual(self.message, testServr.message)

    def test_proxy_output_error_no_connection(self):
        try:
            TestClient(self.message, 5001)
        except socket.error, e:
            self.assertEqual(e.errno, errno.ECONNREFUSED)
        else:
            self.fail("expecting connection error")


    def test_proxy_output_null_message(self):
        testServr = TestServer(5001)
        testServr.receiveMessage()

        outputsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        outputsocket.connect(('127.0.0.1', 5001))
        readWriteSocket.proxyOutput(outputsocket, self.nullMessage)

        testServr.join()
        outputsocket.close()

        self.assertEqual(self.nullMessage, testServr.message)


class TestProxyTotal(unittest.TestCase):
    '''
    Test the full proxy given 2 sockets and port numbers
    '''

    message = 4096 * '1'
    proxyInputSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxyOutputSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def test_proxy_receive_and_output(self):

        testProxy = TestProxy(5001, 5002, self.proxyInputSocket, self.proxyOutputSocket)
        testProxy.start()

        testServer = TestServer(5002)
        testServer.receiveMessage()

        testClient = TestClient(self.message, 5001)

        #WAIT FOR THREADS TO FINISH
        testServer.join()
        testProxy.join()

        self.assertEqual(testClient.message, testServer.message)





if __name__ == '__main__':
    unittest.main()

