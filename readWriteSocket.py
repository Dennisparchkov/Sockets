"""Piece of code that reads input from a socket (arbitrary data) and writes it to another socket
proxy is used to receive data from one socket (client), do something with the data(processing), and write it to another
socket for the server to read from
"""


import socket
import time
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
        inputSocket.listen(5)
        connection, address = inputSocket.accept()

        message = proxyReceiveMessage(connection)
    except socket.error, e:
        errorCode = e[0]
        if errorCode == errno.EBADF:
            print "bad file descriptor: error 9 on receiving socket"
        sys.exit("Something went wrong with the connection on receiving socket")

    try:
        ''' write message to out
        put socket
        '''
        connection.send(str(messageReceived))  # send acknowledgment that timeout occurred (no more data on socket)

        outputSocket.connect((outputIP, outputPort))
        proxyOutput(outputSocket, message)
        connection.close()
        outputSocket.close()
    except socket.error, exception:
        errorCode = exception[0]
        if errorCode == errno.ECONNREFUSED:
            print "Connection problem with output socket"
            raise exception("Connection problem with output socket")
        elif errorCode == errno.WSAECONNRESET:
            print "Connection was forced to close with output socket"
            raise exception("Connection was forced to close with output socket")
        sys.exit("Something went wrong with the connection on Output socket")




def proxyReceiveMessage(connection):
    '''
    handle receiving a message of any size by using timeouts. Timout is set th 1 second,
    meaning that all the message has been received
    :param connection: already connected socket to read message from
    :return: message read from socket
    '''
    connection.setblocking(0)
    message = []
    begin = time.time()
    timeout = 1 #seconds
    while 1:
        if time.time()-begin > timeout:
            #timeout
            break
        try:
            data = connection.recv(1024)
            if data:
                message.append(data)
                begin = time.time()
            else:
                time.sleep(0.1)
        except socket.error, e:
            errorCode = e[0]
            if errorCode == errno.EWOULDBLOCK:  # non-blocking handler, try again
                pass
            else:  # unknown error
                raise e

    message = ''.join(message)
    return message






def proxyOutput(sock, data):
    '''
    puts given data on to given socket
    :param sock: socket to write data to
    :param data: message to put on socket
    :return: response message if successfull, can throw socket error for connection problem
    '''
    try:
        print "Proxy Sender: " + str(sock.getsockname())
        sock.send(data)
        return sock.recv(BUFFER_SIZE)
    except socket.error, exception:
        raise exception








