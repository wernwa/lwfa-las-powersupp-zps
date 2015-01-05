#!/usr/bin/python

import time
import socket
from SockConn import SockConn
from PowerSupply import PowerSupply
import thread

HOST, PORT = "zps-netzteile", 8003



#
#    tid = thread.start_new_thread(end_conn,(s,))

def init_ps(ps_nr):

    ps = PowerSupply(HOST,PORT,ps_nr)

    start = time.time()
    try:
        s = SockConn(HOST, PORT)

        idn = s.question('INST:NSEL %d\n*IDN?\n'%ps.NR)
        s.command('INST:NSEL %d\n*RST\nOUTP:STAT ON\n'%ps.NR)
        s.__del__()


    except Exception as e:
        print ps_nr,'err: ',e


    diff = time.time()-start
    print ps_nr,'difference time: ',diff


# reset all power supplies with *RST command
init_ps(31)
init_ps(1)
init_ps(2)
init_ps(3)
init_ps(4)
init_ps(5)
init_ps(6)
init_ps(7)
init_ps(8)
init_ps(9)


