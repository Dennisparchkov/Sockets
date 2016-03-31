'''Piece of code that reads input from a socket (arbitrary) and writes it to another socket
proxy is used to receive data from one socket (client), do something with the data and write it to another socket
for the server to read from
'''


import socket
from threading import Thread
import struct


INET_IP = '127.0.0.1' #done on localhost
INPUT_PORT = 5001 #port used for the receiving proxy socket
OUTPUT_PORT = 5002 #port used for the receiving server socket
BUFFER_SIZE = 64

#sockets used
inputSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxyReceiverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxyOutputSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverReceiverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#boolean representing a successful reception of data from a process
messageReceived = True


#Generates some data message and sends to socket
def generateInputsocket():
    message = "Here is some data"
    inputSenderSocket.connect((INET_IP, INPUT_PORT))
    print "Client : " + str(inputSenderSocket.getsockname())
    inputSenderSocket.sendall(message)
    try:
        responce = inputSenderSocket.recv(BUFFER_SIZE)
    except:
        print "Buffer size to small"
    inputSenderSocket.close()



#Proxy receives data (can do processing) and copies it to another socket (destined for the server)
#inputSocket = client socket that prxy reads input from,
#outputSocket = socket used for output, writing the input received on this socket (for server)
#
def proxy(inputSocket, outputSocket):

    inputSocket.bind((INET_IP, INPUT_PORT))
    print "Proxy receiver : " + str(inputSocket.getsockname())
    inputSocket.listen(5)
    connection, address = inputSocket.accept()

    outputSocket.connect((INET_IP, OUTPUT_PORT))

    while 1:
        try:
            data = connection.recv(BUFFER_SIZE)
            if not data: break
            print "Data received, Doing something with it"
            data = data + " And  i added this"
            proxyOutput(outputSocket, data)
        except:
            print "Buffer size to small"
            break
        connection.send(str(messageReceived))#send acknowledgment

    connection.close()


#outputs proxy data to server socket
#sock = second socket to write data on
#data = input received from 1st socket(client)
def proxyOutput(sock, data):
      print "Proxy Sender: " + str(sock.getsockname())
      sock.send(data)
      response = sock.recv(BUFFER_SIZE)
      sock.close()


#Server reads data from proxy socket
def server():
     serverReceiverSocket.bind((INET_IP, OUTPUT_PORT))
     print "Server: " + str(serverReceiverSocket.getsockname())
     serverReceiverSocket.listen(1)
     serverConn, addr = serverReceiverSocket.accept()
     while 1:
         try:
             data = serverConn.recv(BUFFER_SIZE)
             if not data: break
             print data
             serverConn.send(str(messageReceived))#send acknowledgment
         except:
            print "Buffer size to small"
            break
     serverConn.close()


#runs 3 separate threads representing 3 different processes:
# proxy handles receiving input from client, processing and writing to server socket.
def main():
     try :
        Thread(target=proxy, args=(proxyReceiverSocket, proxyOutputSocket)).start()
        Thread(target=generateInputsocket, args=()).start() #generates input data.
        Thread(target=server, args=()).start() #echo server for reading from second socket.
     except:
         print "cannot start thereads"




if __name__ == "__main__":
   main()






