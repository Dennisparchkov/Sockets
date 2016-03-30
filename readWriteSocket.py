'''Piece of code that reads input from a socket (arbitrary) and writes it to another socket
3 tier architecture, this acts as the middleware, receiving some data from a socket, processing the data,
then writing it to another socket(going to the front end database)
'''


import socket
from threading import Thread
import struct


INET_IP = '127.0.0.1' #done on localhost
INPUT_PORT = 5001 #port used from input to middleware
OUTPUT_PORT = 5002 #port used from middlware to server
BUFFER_SIZE = 2

#sockets used
inputSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
middlewareReceiverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
middlewareOutputSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        data = inputSenderSocket.recv(BUFFER_SIZE)
    except:
        print "Buffer size to small"
    inputSenderSocket.close()



#Middle ware receives data (can do porcessing) and copies it to another socket (destined for the server)
def middlewareReceiver():

    middlewareReceiverSocket.bind((INET_IP, INPUT_PORT))
    print "Proxy receiver : " + str(middlewareReceiverSocket.getsockname())
    middlewareReceiverSocket.listen(5)
    conn, addr = middlewareReceiverSocket.accept()

    middlewareOutputSocket.connect((INET_IP, OUTPUT_PORT))

    while 1:
        try:
            data = conn.recv(BUFFER_SIZE)
            if not data: break
            print "Data received, Doing something with it"
            data = data + " And  i added this"
            middlewareOutput(middlewareOutputSocket, data)
        except:
            print "Buffer size to small"
            break
        conn.send(str(messageReceived))

    conn.close()


#outputs middleware data to server socket
def middlewareOutput(sock, data):
      print "Proxy Sender: "+ str(sock.getsockname())
      sock.send(data)
      data = sock.recv(BUFFER_SIZE)
      sock.close()


#Server reads data from middleware
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
             serverConn.send(str(messageReceived))
         except:
            print "Buffer size to small"
            break
     serverConn.close()


#runs 3 separate threads representing 3 different processes:
# middleware handles receiving message, procesing and adding to server socket
# generation of input sockets with input, passing to middleware
# server receiving message from middleware socket
def main():
     try :
        Thread(target=middlewareReceiver, args=()).start()
        Thread(target=generateInputsocket, args=()).start()
        Thread(target=server, args=()).start()
     except:
         print "cannot start thereads"




if __name__ == "__main__":
   main()






