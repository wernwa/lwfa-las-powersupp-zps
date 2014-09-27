#!/usr/bin/python

import os
#
#os.environ["EPICS_CA_REPEATER_PORT"] = "20000"
#os.environ["EPICS_CA_SERVER_PORT"] = "20001"

from pcaspy import Driver, SimpleServer, Severity
import random
import thread
import serial
from SockConn import SockConn
import socket
from PowerSupply import PowerSupply
import time
import sys
from termcolor import colored

zps_poling_time = 0.2		# in sesonds
HOST, PORT = "zps-netzteile", 8003

global ps_relee, ps2, ps3, ps4, ps5, ps6, ps7, ps8, ps9, ps10
#global q1, q2, q3, q4, q5, q6, q7, d1, d2

ps_relee = PowerSupply(HOST,PORT,1)
ps2 = PowerSupply(HOST,PORT,2)
ps3 = PowerSupply(HOST,PORT,3)
ps4 = PowerSupply(HOST,PORT,4)
ps5 = PowerSupply(HOST,PORT,5)
ps6 = PowerSupply(HOST,PORT,6)
ps7 = PowerSupply(HOST,PORT,7)
ps8 = PowerSupply(HOST,PORT,8)
ps9 = PowerSupply(HOST,PORT,9)
ps10 = PowerSupply(HOST,PORT,10)

#global prefix_to_ps, ps_to_prefix, record_to_ps
prefix_to_ps = {
	'relee' : ps_relee,
	'q1'	: ps2,
	'q2'	: ps3,
	'q3'	: ps4,
	'q4'	: ps5,
	'q5'	: ps6,
	'q6'	: ps7,
	'q7'	: ps8,
	'd1'	: ps9,
	'd2'	: ps10,
}

ps_to_prefix = {}
for key in prefix_to_ps: ps_to_prefix[prefix_to_ps[key]]=key

record_to_ps = {}
for key in prefix_to_ps:
	record_to_ps['%s:volt'%key] = prefix_to_ps[key]
	record_to_ps['%s:curr'%key] = prefix_to_ps[key]

#global zps_lock, zps_conn
zps_lock = thread.allocate_lock()
zps_conn = False

active_ps_list = []

prefix = 'shicane:'
pvdb={}
for name in prefix_to_ps:
	pvdb['%s:volt'%name] = {'prec' : 3,'unit' : 'V'}
	pvdb['%s:curr'%name] = {'prec' : 3,'unit' : 'A'}



class myDriver(Driver):
    def  __init__(self):
		super(myDriver, self).__init__()
		
		# aprove connection to the power supplies
		global active_ps_list
		try:
			s = SockConn(HOST, PORT)
		except socket.error, msg:
			print colored('Error: ', 'red'),"main LAN zps powersupply does not respond! %s"%msg
			sys.exit(-1)


		for ps in ps_to_prefix:
			try:
				idn = s.question('INST:NSEL %d\n*IDN?\n'%ps.NR,timeout=0.3)
				#print idn
				active_ps_list.append(ps)
				print '%s powersupplyNR %d [connection '%(ps_to_prefix[ps],ps.NR), colored('OK', 'green'),']'
				s.command('INST:NSEL %d\nOUTP:STAT ON'%ps.NR)
			except socket.timeout:
				print '%s powersupplyNR %d ['%(ps_to_prefix[ps],ps.NR),colored('disconnect', 'red'),']'

		if len(active_ps_list)==0:
			print colored('Error: ', 'red'),'no powersupplies discovered!'
			sys.exit(-1)
		
		s.__del__()
	

		#start polling	
		self.tid = thread.start_new_thread(self.continues_polling,())
		print '----------------------------------------------------------'
		print '%d ps up. Start polling with %0.3f seconds (CTRL+C -> end).'%(len(active_ps_list),zps_poling_time)
		print '----------------------------------------------------------'

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
		#TODO read status
		status = True
		ps = record_to_ps[reason]
		zps_lock.acquire()
		#zps_conn = True
		if 'volt' in reason: ps.setVolt(value)
		elif 'curr' in reason: ps.setCurr(value)
		#zps_conn = False
		zps_lock.release()

		if status:
			self.setParam(reason, value)

		return status


    def continues_polling(self):
		global active_ps_list
		while True:
			zps_lock.acquire()
			#while zps_conn == True: time.sleep(0.1)
			s = SockConn(HOST, PORT)
			for ps in active_ps_list:
				volt = s.question('INST:NSEL %d\n:measure:voltage?'%ps.NR)
				self.setParam('%s:volt'%ps_to_prefix[ps], volt)
				curr = s.question(':measure:current?')
				self.setParam('%s:curr'%ps_to_prefix[ps], curr)
				#print ps.NR,volt,curr,ps_to_prefix[ps]

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

