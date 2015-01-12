#
#   SockConn for a socket connection
#
import socket
import sys
import time

current_millis = lambda: int(round(time.time()*1000))


class SockConn:
    HOST, PORT = "localhost", 9999
    sock=None

    #
    #   Constructor
    #
    def __init__(self,host,port):
        self.HOST=host
        self.PORT=port
        # Create a socket (SOCK_STREAM means a TCP socket)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to server
        self.sock.connect((self.HOST, self.PORT))

    #
    #   reads a string from the socket until delim accrues
    #
    def readline(self,asock, recv_buffer=4096, delim='\r\n', timeout=2):
        buffer = ''
        data = True
        self.sock.settimeout(timeout)
        while data:
            data = self.sock.recv(recv_buffer)
            buffer += data

            while buffer.find(delim) != -1:
                line, buffer = buffer.split('\r\n', 1)
                return line
        return

    #
    #   send a command without waiting for an answer
    #
    def command(self,data):
        self.sock.sendall(data+"\n")
        #print "SCPI "+data+"\n"

    #
    #   sends a command and returns also an answer string
    #
    def question(self,data,timeout=1):
        #try:
        start_millis=current_millis()

        self.command(data)
        received = self.readline(self.sock,timeout=timeout)

        msecs=current_millis()-start_millis


        #print "Sent:     {}".format(data)
        #print "Received: {}".format(received)
        #print "Microseconds: {}".format(msecs)

        return received
    #except:

    #
    #   Destructor, closes the socket connection and sleeps for some relax time
    #
    def __del__(self):
        #print "close socket\n"
        self.sock.close()
        time.sleep(0.01)


