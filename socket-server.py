#!/usr/bin/python

import SocketServer
import re
from random import random
import thread
import time

ps1=[random()*6, random()*30]
ps2=[random()*6, random()*30]
ps3=[random()*6, random()*30]
ps4=[random()*6, random()*30]
ps5=[random()*6, random()*30]
ps6=[random()*6, random()*30]
ps7=[random()*6, random()*30]
ps8=[random()*6, random()*30]
ps9=[random()*6, random()*30]
ps_relee=[random()*6, random()*30]

ps_VOLT=1
ps_CURR=0

nr_to_ps={
    1:ps1,
    2:ps2,
    3:ps3,
    4:ps4,
    5:ps5,
    6:ps6,
    7:ps7,
    8:ps8,
    9:ps9,
    31:ps_relee,
        }

ps_selected=None

#INST:NSEL 3
#:measure:voltage?
#:measure:current?

#INST:NSEL 6
#TRIG:SOUR BUS
#CURR:MODE WAVE
#LIST:CURR 0
#LIST:DWEL 4.52
#LIST:COUNT 1
#LIST:STEP AUTO
#INIT:CONT OFF
#INIT

def frange(x, y, jump):
    if jump>0:
        while x < y:
            yield x
            x += jump
    elif jump<0:
        while x > y:
            yield x
            x += jump
    else: raise Exception('frange: jump is zero')


#regex_curr_change = re.compile(r'LIST:CURR (\S+)', re.MULTILINE)
regex_curr_change = re.compile(r'INST:NSEL (\S+).*?LIST:CURR (\S+).*?LIST:DWEL (\S+)', re.DOTALL)


class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def set_curr_in_time(self,ps, curr_1, t):
        steps = 10.0
        sleep_sec = t/steps
        curr_0 = ps[ps_CURR]
        curr_step = (curr_1 - curr_0)/steps
        print 'curr_step',curr_step,'curr_0',curr_0,'curr_1',curr_1

        for i in frange(curr_0,curr_1,curr_step):
            time.sleep(sleep_sec)
            ps[ps_CURR]=i
        time.sleep(sleep_sec)
        ps[ps_CURR]=curr_1



    def handle(self):
        while True:
            # self.request is the TCP socket connected to the client
            self.data = self.request.recv(1024).strip()
            if not self.data: break
            #print "----- {} wrote: -----".format(self.client_address[0])
            #print self.data

            m = re.search('INST:NSEL (\d+)',self.data)
            if m!=None:
                ps_selected=nr_to_ps[int(m.group(1))]

            if ':measure:voltage?' in self.data:
                num = "%.3f\r\n" %(ps_selected[ps_VOLT])
                self.request.sendall(num)

            elif ':measure:current?' in self.data:
                num = "%.3f\r\n" %(ps_selected[ps_CURR])
                self.request.sendall(num)
            elif '*IDN?' in self.data:
                num = "IDN=%.3f\r\n" %(random())
                self.request.sendall(num)

            matches = [m.groups() for m in regex_curr_change.finditer(self.data)]
            for m in matches:
                ps=nr_to_ps[int(m[0])]
                curr=float(m[1])
                curr_time = float(m[2])
                #print int(m[0]),curr,curr_time
                #ps[ps_CURR]=curr
                thread.start_new_thread(self.set_curr_in_time,(ps,curr,curr_time,))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8003

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
