"""Piece of code that reads input from a socket (arbitrary data) and writes it to another socket
proxy is used to receive data from one socket (client), do something with the data(processing), and write it to another
socket for the server to read from
"""


import socket
import errno
import sys



INET_IP = '127.0.0.1'  # done on localhost
BUFFER_SIZE = 1024  # Allocated size for data being received by socket

# boolean representing a successful reception of data from a process
messageReceived = True



def proxy(inputSocket, inputIP, inputPort,  outputSocket, outputIP, outputPort):
    '''
    Proxy receives data (can do processing) and copies it to another socket (destined for the server)
    :param inputSocket: client socket that proxy reads from
    :param inputIP: IP address for input socket
    :param inputPort: port number for input socket
    :param outputSocket: proxy writes message to this socket
    :param outputIP: output socket IP address
    :param outputPort: output socket port
    :return: null
    '''

    try:
        ''' receive message from socket inputSocket
        '''
        inputSocket.bind((inputIP, inputPort))
        print "Proxy receiver : " + str(inputSocket.getsockname())
        #TCP socket
        if inputSocket.type == 1 and outputSocket.type == 1:
            inputSocket.listen(5)
            connection, address = inputSocket.accept()
            outputSocket.connect((outputIP, outputPort))
            forwardTCP(connection, outputSocket)
            connection.close()
            outputSocket.close()
        #UDP socket
        elif inputSocket.type == 2 and outputSocket.type == 2 :
            forwardUDP(inputSocket, outputSocket, outputPort)

    except socket.error, e:
        errorCode = e[0]
        if errorCode == errno.EBADF:
            print "bad file descriptor: error 9 on receiving socket"
        elif errorCode == errno.ECONNREFUSED:
            print "Connection problem with output socket"
            raise e("Connection problem with output socket")
        elif errorCode == errno.WSAECONNRESET:
            print "Connection was forced to close with output socket"
            raise e("Connection was forced to close with output socket")
        sys.exit("Something went wrong with the connection on receiving socket")




def forwardUDP(input, output, outputPort):
    '''
     handle receiving a message of any size by using timeouts using UDP sockets. Timout is set th 1 second,
    meaning that all the message has been received
    :param input: reading UDP socket
    :param output: writing UDP socket
    :return:
    '''
    input.setblocking(0)
    input.settimeout(1)
    while 1:
        try:
            output.sendto(input.recv(1024), ("127.0.0.1", outputPort))
        except socket.error, e:
            raise e
        except socket.timeout:
            break

def forwardTCP(connection, out):
    '''
    handle receiving a message of any size by using timeouts using TCP sockets. Timout is set th 1 second,
    meaning that all the message has been received
    :param connection: receiving socket TCP
    :param out: output socket TCP
    :return:
    '''
    connection.settimeout(1)
    while 1:
        try:
            out.send(connection.recv(1024))
        except socket.error, e:
            raise e
        except socket.timeout:
            break













