#!/usr/bin/python

import os
#
#os.environ["EPICS_CA_REPEATER_PORT"] = "20000"
#os.environ["EPICS_CA_SERVER_PORT"] = "20001"

from pcaspy import Driver, SimpleServer, Severity
import random
import math
import thread
import serial
from SockConn import SockConn
import socket
from PowerSupply import PowerSupply
import time
import sys
from termcolor import colored

alive=True

zps_poling_time = 0.2        # in sesonds
HOST, PORT = "zps-netzteile", 8003

global ps_relee, ps1,ps2, ps3, ps4, ps5, ps6, ps7, ps8, ps9
#global q1, q2, q3, q4, q5, q6, q7, d1, d2

ps_relee = PowerSupply(HOST,PORT,32)
ps1 = PowerSupply(HOST,PORT,1)
ps2 = PowerSupply(HOST,PORT,2)
ps3 = PowerSupply(HOST,PORT,3)
ps4 = PowerSupply(HOST,PORT,4)
ps5 = PowerSupply(HOST,PORT,5)
ps6 = PowerSupply(HOST,PORT,6)
ps7 = PowerSupply(HOST,PORT,7)
ps8 = PowerSupply(HOST,PORT,8)
ps9 = PowerSupply(HOST,PORT,9)

ps_to_magnet = {
    ps1 : 'q1',
    ps2 : 'q2',
    ps3 : 'q3',
    ps4 : 'q4',
    ps5 : 'q5',
    ps6 : 'q6',
    ps7 : 'q7',
    ps8 : 'd1',
    ps9 : 'd2',
}

prefix_to_ps = {
    'zps:1'    : ps1,
    'zps:2'    : ps2,
    'zps:3'    : ps3,
    'zps:4'    : ps4,
    'zps:5'    : ps5,
    'zps:6'    : ps6,
    'zps:7'    : ps7,
    'zps:8'    : ps8,
    'zps:9'    : ps9,
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
ps_list = [ps1,ps2,ps3,ps4,ps5,ps6,ps7,ps8,ps9]

relee_sign = -1.0    # plus and minus
relee_plus = 0.0    # V
relee_minus = 24.0    #V

prefix = 'shicane:'
pvdb={
    'demag': {},
    'demag:steps': {
        'type' : 'int'
    },
    'demag:sleep': {
        'type' : 'float',
        'prec' : 3,'unit' : 'seconds'
    },

    'zps:relee:sign': {
        'type' : 'enum',
        'enums': ['-', '+']
    },

    'zps:relee:volt': {
        'prec' : 3,'unit' : 'V'
    },

    'zps:relee:curr': {
        'prec' : 3,'unit' : 'A'
    },
    'ps_volt_all' : {
           'type' : 'char',
        'count' : 100,
           'unit' : 'C',
    },
    'ps_curr_all' : {
           'type' : 'char',
        'count' : 100,
           'unit' : 'C',
    },
}

for name in prefix_to_ps:
    pvdb['%s:volt'%name] = {'prec' : 3,'unit' : 'V',
                    'lolim': 0, 'hilim': 60,
                    'lolo': -1, 'low':-5,
                    'hihi': 55, 'high': 50}
    pvdb['%s:curr'%name] = {'prec' : 3,'unit' : 'A',
                    'lolim': 0, 'hilim': 6,
                    'lolo': -1, 'low':-5,
                    'hihi': 5.7, 'high': 5.5,
                    'DRVH':6
                    }

for name in ['q1','q2','q3','q4','q5','q6','q7','d1','d2']:
    pvdb['%s:volt'%name] = {'prec' : 3,'unit' : 'V', 'asg'  : 'readonly'}
    pvdb['%s:curr'%name] = {'prec' : 3,'unit' : 'A', 'asg'  : 'readonly'}


class myDriver(Driver):
    def  __init__(self):

        super(myDriver, self).__init__()

        self.setParam('demag', 0)
        self.setParam('demag:sleep', 1)
        self.setParam('demag:steps', 20)

        global active_ps_list
        active_ps_list = [ps1,ps2,ps3,ps4,ps5,ps6,ps7,ps8,ps9]


        # set initial ps
        for ps in active_ps_list:
            volt = round(random.random()*60,3)
            self.setParam('%s:volt'%ps_to_prefix[ps], volt)
            self.setParam('%s:volt'%ps_to_magnet[ps], relee_sign*float(volt))

            curr = round(random.random()*5,3)
            #curr_all += '%s '%curr
            self.setParam('%s:curr'%ps_to_prefix[ps], curr)
            self.setParam('%s:curr'%ps_to_magnet[ps], relee_sign*float(curr))

        #start polling
        self.tid = thread.start_new_thread(self.continues_polling,())
        print '----------------------------------------------------------'
        print 'Pseudo zps Server. Start polling with %0.3f seconds (CTRL+C -> end).'%(zps_poling_time)
        print '----------------------------------------------------------'


    def read(self, reason):
        return self.getParam(reason)

#   def demag(self):
#       print 'demag hier'


    def write(self, reason, value):
        global relee_plus, relee_minus, relee_sign


        zps_lock.acquire()

        #TODO read status
        status = True
        ps = None

        if reason=='demag':
            self.thred_demag_id = thread.start_new_thread(self.demag,())
            return True


        if status:
            self.setParam(reason, value)

        time.sleep(0.1)

        zps_lock.release()
        return status


    def continues_polling(self):
        global alive, ps_list, active_ps_list, relee_sign, relee_plus, relee_minus
        while alive:
            try:

#                volt = round(random.randint(0,1)*relee_plus,3)
                volt = self.getParam('zps:relee:volt')
                volt_all = '%s '%volt
#                self.setParam('zps:relee:volt', volt)
#                curr = round(random.random(),3)
                curr = self.getParam('zps:relee:curr')
                curr_all = '%s '%curr
#                self.setParam('zps:relee:curr', random.random())
#                if (round(float(volt))==relee_plus): relee_sign=1.0
#                elif (round(float(volt))==relee_minus): relee_sign=-1.0
#                # poll other ps
                for ps in active_ps_list:
                    volt = self.getParam('%s:volt'%ps_to_prefix[ps])
                    self.setParam('%s:volt'%ps_to_prefix[ps], volt)
                    self.setParam('%s:volt'%ps_to_magnet[ps], relee_sign*float(volt))

                    curr = self.getParam('%s:curr'%ps_to_prefix[ps])
                    self.setParam('%s:curr'%ps_to_prefix[ps], curr)
                    self.setParam('%s:curr'%ps_to_magnet[ps], relee_sign*float(curr))

                # refresh ps_all_volt and ps_all_curr
                for ps in ps_list:
                    if ps == ps_relee: continue
                    if ps in active_ps_list:
                        volt_all += '%s '%self.getParam('%s:volt'%ps_to_prefix[ps])
                        curr_all += '%s '%self.getParam('%s:curr'%ps_to_prefix[ps])
                    else:
                        volt_all += 'None '
                        curr_all += 'None '
                volt_all += '\n'
                curr_all += '\n'
                self.setParam('ps_volt_all',volt_all)
                self.setParam('ps_curr_all',curr_all)

            except Exception as e:
                print '%s'%e.message
                print 'Exiting due to socket error.'
                alive=False

            self.updatePVs()
            time.sleep(zps_poling_time)


if __name__ == '__main__':


    server= SimpleServer()
    server.initAccessSecurityFile('security.as', P=prefix)
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while alive:
        try:
            server.process(0.1)
        except KeyboardInterrupt:
            print " Bye"
            sys.exit()

