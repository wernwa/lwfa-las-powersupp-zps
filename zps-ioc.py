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
import time
import sys

zps_poling_time = 0.2		# in sesonds
HOST, PORT = "zps-netzteile", 8003

prefix = 'shicane:'
pvdb = {
    'relee:volt' : {
        'prec' : 3,
		'unit' : 'V',
    },
    'relee:curr' : {
        'prec' : 3,
		'unit' : 'A',
    },

    'q1:volt' : {
        'prec' : 3,
		'unit' : 'V',
    },
    'q1:curr' : {
        'prec' : 3,
		'unit' : 'A',
    },
}
tempcnt = 7

class myDriver(Driver):
    def  __init__(self):
        super(myDriver, self).__init__()
        self.tid = thread.start_new_thread(self.continues_polling,())
		

	global ps_relee, ps2, ps3, ps4, ps5, ps6, ps7, ps8, ps9, ps10
	global q1, q2, q3, q4, q5, q6, q7, d1, d2

	ps_relee = PowerSupply(HOST,PORT,1)
	q1 = ps8 = PowerSupply(HOST,PORT,8)

	global prefix_to_ps, ps_to_prefix, record_to_ps
	prefix_to_ps = {
		'relee' : ps_relee,
		'q1'	: ps8,
	}

	ps_to_prefix = {}
	for key in prefix_to_ps: ps_to_prefix[prefix_to_ps[key]]=key

	record_to_ps = {}
	for key in prefix_to_ps:
		record_to_ps['%s:volt'%key] = prefix_to_ps[key]
		record_to_ps['%s:curr'%key] = prefix_to_ps[key]
	global zps_lock, zps_conn
	zps_lock = thread.allocate_lock()
	zps_conn = False

    def read(self, reason):
		#ps = record_to_ps[reason]
		#zps_lock.acquire()
		#zps_conn = True
		##if 'volt' in reason: return ps.getVolt()
		##elif 'curr' in reason: return ps.getCurr()
		#zps_conn = False
		#zps_lock.release()

		return self.getParam(reason)
		
    def write(self, reason, value):
		status = True
		ps = record_to_ps[reason]
		zps_lock.acquire()
		#zps_conn = True
		if 'volt' in reason: ps.setVolt(value)
		elif 'curr' in reason: ps.setCurr(value)
		#zps_conn = False
		zps_lock.release()

		#if status:
		#	self.setParam(reason, value)

		return status


    def continues_polling(self):
        active_ps_list = [ps_relee,ps8]
        while True:
			zps_lock.acquire()
			#while zps_conn == True: time.sleep(0.1)
			s = SockConn(HOST, PORT)
			for ps in active_ps_list:
				volt = s.question('INST:NSEL %d\n:measure:voltage?'%ps.NR)
				self.setParam('%s:volt'%ps_to_prefix[ps], volt)
				curr = s.question(':measure:current?')
				self.setParam('%s:curr'%ps_to_prefix[ps], curr)
				print volt,curr

			s.__del__()
			zps_lock.release()
			self.updatePVs()
			time.sleep(zps_poling_time)
			

if __name__ == '__main__':


    server= SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while True:
		try:
			server.process(0.1)
		except KeyboardInterrupt:
			print "Bye"
			sys.exit()

