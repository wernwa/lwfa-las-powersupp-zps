#!/usr/bin/python

import SocketServer
import re
from random import random

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        while True:
            # self.request is the TCP socket connected to the client
            self.data = self.request.recv(1024).strip()
            if not self.data: break
            print "----- {} wrote: -----".format(self.client_address[0])
            print self.data

            m = re.search('\?',self.data)
            if m!=None:
                num = "%.3f\r\n" %(random()*4)
                # send back the random number
                self.request.sendall(num)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8003

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
