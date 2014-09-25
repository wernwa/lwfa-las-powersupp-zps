#!/usr/bin/python

#import os
#
#os.environ["EPICS_CA_REPEATER_PORT"] = "20000"
#os.environ["EPICS_CA_SERVER_PORT"] = "20001"

from pcaspy import Driver, SimpleServer, Severity
import random
import thread
import serial
from SockConn import SockConn
from PowerSupply import PowerSupply

ps = range(11)
HOST, PORT = "zps-netzteile", 8003

prefix = 'shicane:'
pvdb = {
    'relee:volt' : {
        'prec' : 3,
#        'scan' : 0.5,
		'unit' : 'V',
    },
    'relee:curr' : {
        'prec' : 3,
#        'scan' : 0.5,
		'unit' : 'A',
    },

    'q1:volt' : {
        'prec' : 3,
        'scan' : 0.5,
		'unit' : 'V',
    },
    'q1:curr' : {
        'prec' : 3,
 #       'scan' : 0.5,
		'unit' : 'A',
    },
}
tempcnt = 7

class myDriver(Driver):
    def  __init__(self):
        super(myDriver, self).__init__()
        #self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        #self.tid = thread.start_new_thread(self.read_tty,())

	global ps_relee, ps2, ps3, ps4, ps5, ps6, ps7, ps8, ps9, ps10
	global q1, q2, q3, q4, q5, q6, q7, d1, d2

	ps_relee = PowerSupply(HOST,PORT,1)
	q1 = ps8 = PowerSupply(HOST,PORT,8)

	global record_to_ps 
	record_to_ps = {
		'relee:volt':ps_relee,
		'relee:curr':ps_relee,
		'q1:volt':ps8,
		'q1:curr':ps8,

	}

    def read(self, reason):
		ps = record_to_ps[reason]
		if 'volt' in reason: return ps.getVolt()
		elif 'curr' in reason: return ps.getCurr()

		return self.getParam(reason)
		
    def write(self, reason, value):
		status = True
		ps = record_to_ps[reason]
		if 'volt' in reason: ps.setVolt(value)
		elif 'curr' in reason: ps.setCurr(value)

		#if status:
		#	self.setParam(reason, value)

		return status


    def read_tty(self):
        global tempcnt
        while True:
            line = self.ser.readline()
	    #print line
            t_arr = line.split(' ')
            if (len(t_arr)!=tempcnt+1):
                continue
            #print t_arr
            self.setParam('q1:temp', t_arr[0])
            self.setParam('q2:temp', t_arr[1])
            self.setParam('q3:temp', t_arr[2])
            self.setParam('q4:temp', t_arr[3])
            self.setParam('q5:temp', t_arr[4])
            self.setParam('q6:temp', t_arr[5])
            self.setParam('q7:temp', t_arr[6])
            self.updatePVs()

if __name__ == '__main__':


    server= SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while True:
        server.process(0.1)

