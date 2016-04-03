"""Piece of code that reads input from a socket (arbitrary data) and writes it to another socket
proxy is used to receive data from one socket (client), do something with the data(processing), and write it to another
socket for the server to read from
"""


import socket
import time
import errno
import sys
from threading import Thread


INET_IP = '127.0.0.1'  # done on localhost
INPUT_PORT = 5001  # port used for the receiving proxy socket
OUTPUT_PORT = 5002  # port used for the receiving server socket
BUFFER_SIZE = 1024  # Allocated size for data being received by socket

# sockets used
inputSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxyReceiverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

proxyOutputSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverReceiverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# boolean representing a successful reception of data from a process
messageReceived = True


# '''Generates some data message and writes to proxy socket
# '''
# def generateInputsocket():
#     message = 4096*"0"
#
#     try:
#         inputSenderSocket.connect((INET_IP, INPUT_PORT))
#         print "Client : " + str(inputSenderSocket.getsockname())
#         inputSenderSocket.sendall(message)
#         response = inputSenderSocket.recv(BUFFER_SIZE)
#         if response:
#             inputSenderSocket.close()
#
#     except socket.error, exception:
#         errorCode = exception[0]
#
#         if errorCode == errno.ECONNREFUSED:
#             print "Connection problem"
#         elif errorCode == errno.WSAECONNRESET:
#             print "Connection was forced to close"
#
#






'''Proxy receives data (can do processing) and copies it to another socket (destined for the server)
#inputSocket = client socket that prxy reads input from,
#outputSocket = socket used for output, writing the input received on this socket (for server)
'''
def proxy(inputSocket, inputIP, inputPort,  outputSocket, outputIP, outputPort):

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

        print len(message)
        outputSocket.connect((outputIP, outputPort))
        proxyOutput(outputSocket, message)
        connection.close()
        outputSocket.close()
    except socket.error, exception:
        errorCode = exception[0]
        if errorCode == errno.ECONNREFUSED:
            print "Connection problem with output socket"
        elif errorCode == errno.WSAECONNRESET:
            print "Connection was forced to close with output socket"




def proxyReceiveMessage(connection):
    connection.setblocking(0)
    message = [];
    begin = time.time()
    timeout = 1 #seconds
    while 1:
        if message and time.time()-begin>timeout:
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






'''outputs proxy data to server socket
#sock = second socket to write data on
#data = input received from 1st socket(client)
'''
def proxyOutput(sock, data):
    try:
        print "Proxy Sender: " + str(sock.getsockname())
        sock.send(data)
        response = sock.recv(BUFFER_SIZE)
    except socket.error, exception:
        raise exception


# '''Server reads data written by proxy socket
# '''
# def server():
#      serverReceiverSocket.bind((INET_IP, OUTPUT_PORT))
#      print "Server: " + str(serverReceiverSocket.getsockname())
#      serverReceiverSocket.listen(1)
#      serverConn, addr = serverReceiverSocket.accept()
#      while 1:
#          try:
#              data = serverConn.recv(BUFFER_SIZE)
#              if not data: break
#              print len(data)
#              serverConn.send(str(messageReceived))#send acknowledgment
#          except socket.error:
#             print "Buffer size to small server"
#             break
#      serverConn.close()
#
#
# '''runs 3 separate threads representing 3 different processes:
# # proxy handles receiving input from client, processing and writing to server socket.
# '''
# def main():
#      try :
#         #Thread(target=proxy, args=(proxyReceiverSocket,INET_IP, INPUT_PORT, proxyOutputSocket, INET_IP, OUTPUT_PORT)).start()
#         Thread(target=generateInputsocket, args=()).start() #generates input data.
#         Thread(target=server, args=()).start() #generates input data.
#      except:
#          print "cannot start thereads"
#
#
#
#
# if __name__ == "__main__":
#    main()






