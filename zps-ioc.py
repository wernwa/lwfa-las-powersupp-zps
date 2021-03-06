#!/usr/bin/python
#
#
#   Driver class for 10 power supplies
#
#   Author: Walter Werner
#   email: wernwa@gmail.com
#



import os

from pcaspy import Driver, SimpleServer, Severity
import random
import math
import thread
import serial
from SockConn import SockConn
import socket
import time
import sys
from termcolor import colored
from setup import *
import traceback, errno

alive=True  # helper variable for the polling thread


global ps_relee, ps1, ps2, ps3, ps4, ps5, ps6, ps7, ps8, ps9


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
    record_to_ps['%s:output'%key] = prefix_to_ps[key]
    record_to_ps['%s:volt'%key] = prefix_to_ps[key]
    record_to_ps['%s:curr'%key] = prefix_to_ps[key]

zps_lock = thread.allocate_lock()
zps_conn = False

active_ps_list = []
ps_list = [ps1,ps2,ps3,ps4,ps5,ps6,ps7,ps8,ps9]

relee_sign = -1.0    # plus and minus
relee_plus = 0.0    # V
relee_minus = 24.0    #V




##
##  Database variable definitions
##
prefix = 'chicane:'
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
        'prec' : 3,'unit' : 'A',
        #'asg'  : 'readonly'
    },
    'zps:relee:volt:status': {
            'type'  : 'enum',
            'enums' : ['IDLE','BUSY'],
    },

    'zps:relee:curr:status': {
            'type'  : 'enum',
            'enums' : ['IDLE','BUSY'],
    },
    'magn_volt_all' : {
           #'type' : 'string',
           'type' : 'char',
            'count' : 100,
            'unit' : 'V',
            'asg'  : 'readonly',
    },
    'magn_curr_all' : {
           'type' : 'char',
            'count' : 100,
            'unit' : 'A',
            'asg'  : 'readonly',
    },
}
for name in prefix_to_ps:
    pvdb['%s:volt'%name] = {'prec' : 3,'unit' : 'V',
                    'lolim': 0, 'hilim': 60,
                    'lolo': -1, 'low':-5,
                    'hihi': 55, 'high': 50,
                    'asyn': True,
                    }
    pvdb['%s:volt:status'%name] = {
            'type'  : 'enum',
            'enums' : ['IDLE','BUSY'],
        }
    pvdb['%s:curr'%name] = {'prec' : 3,'unit' : 'A',
                    'lolim': 0, 'hilim': 6,
                    'lolo': -1, 'low':-5,
                    'hihi': 5.7, 'high': 5.5,
                    'asyn': True,
                    }
    pvdb['%s:curr:status'%name] = {
            'type'  : 'enum',
            'enums' : ['IDLE','BUSY'],
        }
    pvdb['%s:output'%name] = {      # ps output on/off 1/0
            'type'  : 'int',
        }
    pvdb['%s:online'%name] = {      # ps connected to the main powersupp (no ethernet or no power)
            'type'  : 'enum',
            'enums' : ['NO','YES'],
        }

for name in ['q1','q2','q3','q4','q5','q6','q7','d1','d2']:
    pvdb['%s:volt'%name] = {'prec' : 3,'unit' : 'V', 'asg'  : 'readonly'}
    pvdb['%s:curr'%name] = {'prec' : 3,'unit' : 'A', 'asg'  : 'readonly'}






##
##  The actual driver class
##
class myDriver(Driver):
    #
    # Constructor, discover powersuppl that are connected with the relee
    #
    def  __init__(self):
        super(myDriver, self).__init__()

        self.setParam('demag', 0)
        self.setParam('demag:sleep', 1)
        self.setParam('demag:steps', demag_steps)

        # check connection to the power supplies
        global active_ps_list
        try:
            s = SockConn(HOST, PORT)
            #active_ps_list.append(ps_relee)
            #s.command('INST:NSEL %d\n*CLS\nOUTP:STAT ON\n'%ps_relee.NR)
            #s.command('INST:NSEL %d\n*RST\nOUTP:STAT ON\n'%ps_relee.NR)
            s.command('INST:NSEL %d\nOUTP:STAT ON\n'%ps_relee.NR)
            print '%s powersupplyNR %d [connection '%('zps:relee',ps_relee.NR), colored('OK', 'green'),']'
        except socket.error, msg:
            print colored('Error: ', 'red'),"main LAN zps powersupply does not respond! %s"%msg
            sys.exit(-1)


        time.sleep(1)

        for ps in ps_to_prefix:
            try:
                #ps_relee.ask_for_error(s,psNR=ps.NR)
                idn = s.question('INST:NSEL %d\n*IDN?\n'%ps.NR,timeout=0.6)
                ps_relee.ask_for_error(s,psNR=ps.NR)
                print '%s powersupplyNR %d [connection '%(ps_to_magnet[ps],ps.NR), colored('OK', 'green'),']'
                active_ps_list.append(ps)
                self.setParam('zps:%d:online'%ps.NR,1)

                #print ps.NR,idn
                #s.command('INST:NSEL %d\nOUTP:STAT ON\n'%ps.NR)

            except socket.timeout:
                print '%s powersupplyNR %d ['%(ps_to_magnet[ps],ps.NR),colored('disconnect', 'red'),']'
                self.setParam('zps:%d:online'%ps.NR,0)

            time.sleep(0.01)

        if len(active_ps_list)==0:
            print colored('Error: ', 'red'),'no powersupplies discovered!'
            sys.exit(-1)

        # clear command structure
        print 'clearing the command structure...'
        s.command('INST:NSEL %d\n*CLS\nOUTP:STAT ON\n'%ps_relee.NR)
        time.sleep(1.5)
        s.command('INST:NSEL %d\nOUTP:STAT ON\n'%ps_relee.NR)
        time.sleep(0.01)
        for ps in active_ps_list:
            s.command('INST:NSEL %d\nABORT\n*CLS\n'%ps.NR)
            #ps_relee.ask_for_error(s,psNR=ps.NR)
            time.sleep(1.5)
            s.command('INST:NSEL %d\nOUTP:STAT ON\n'%ps.NR)

        #ps_relee.ask_for_error(s,psNR=ps_relee.NR)

        # set relee volt=0 curr=0.6
        #print 'setting the relee...'
        #s.command("INST:NSEL %d\n:VOLT %.3f"%(ps_relee.NR,0))
        #ps_relee.ask_for_error(s,psNR=ps_relee.NR)
        #s.command("INST:NSEL %d\n:CURR %.3f"%(ps_relee.NR,0.6))
        #ps_relee.ask_for_error(s,psNR=ps_relee.NR)

        s.__del__()


        self.demag_active=False

        #start polling
        self.tid = thread.start_new_thread(self.continues_polling,())
        print '----------------------------------------------------------'
        print '%d ps up. Start polling with %0.3f seconds (CTRL+C -> end).'%(len(active_ps_list)+1,zps_poling_time)
        print '----------------------------------------------------------'

    #
    #   read method is called if a pv variable is readed, currently with no
    #   actual functionality and
    #   can be outcommented
    #
    def read(self, reason):

        if 'relee' in reason : ps = ps_relee
        elif reason in record_to_ps: ps = record_to_ps[reason]


        return self.getParam(reason)

    #
    #  get the opposite sign in Voltage for the relee
    #  needed by the demag function
    #
    def get_relee_invert(self):
        global relee_sign, relee_plus, relee_minus
        if relee_sign==1.0: return relee_minus
        elif relee_sign==-1.0: return relee_plus



    #
    #   Main demag method
    #
    def demag(self):


#        # ask for errors
#        zps_lock.acquire()
#        s = SockConn(HOST, PORT)
#        for i in range(0,len(active_ps_list)):
#            ps = active_ps_list[i]
#            ps_relee.ask_for_error(s,psNR=ps.NR)
#        s.__del__()
#        zps_lock.release()

        print 'starting demagnetesization of all active magnets'
        # demag duration set status to BUSY
        for i in range(1,10):
            self.setParam('zps:%d:curr:status'%i,1)

        # get the actuall currents
        ps_heightCurr = []
        curr_max = 0
        for ps in active_ps_list:
            curr = float(self.getParam('%s:curr'%ps_to_prefix[ps]))
            if curr > current_remanence: curr=current_remanence
            if curr_max<curr: curr_max=curr
            ps_heightCurr.append( curr )

        # goto zero
        self.demag_0()


        #''' do demag in steps '''
        #sleep_sec = self.getParam('demag:sleep')
        steps = int(self.getParam('demag:steps'))
        steps = demag_steps
        print 'steps',steps,'remanence curr',current_remanence
        for count in range(1,steps+1):
            ps_destCurr = []
            for curr in ps_heightCurr:
                ps_destCurr.append(round(curr-count*curr/float(steps),3))
            print count,'I=%s'%ps_destCurr
            self.demag_triangle(ps_destCurr)

        # demag duration set status to IDLE
        for i in range(1,10):
            self.setParam('zps:%d:curr:status'%i,0)
        print 'Demag DONE'

        self.setParam('demag',0)
        self.updatePVs()
        self.demag_active=False


#        # ask for errors
#        zps_lock.acquire()
#        s = SockConn(HOST, PORT)
#        for i in range(0,len(active_ps_list)):
#            ps = active_ps_list[i]
#            ps_relee.ask_for_error(s,psNR=ps.NR)
#        s.__del__()
#        zps_lock.release()

    #
    #   First Step, all ps to zero
    #
    def demag_0(self):
        global active_ps_list, relee_sign, relee_plus, relee_minus
        ps_heightCurr = []
        curr_max = 0
        for ps in active_ps_list:
            curr = float(self.getParam('%s:curr'%ps_to_prefix[ps]))
            if curr_max<curr: curr_max=curr
            ps_heightCurr.append( curr )

        duration_sec = curr_max/step_velocity
        if duration_sec==0:
            #print 'duration_sec ',duration_sec
            return


        step_size_sec = 1.0
        relee_steps = duration_sec/step_size_sec
        relee_steps = int(round(relee_steps/2.0))
        #print 'steps',relee_steps

#        VOLT_str = '24,0,'
#        VOLT_str = VOLT_str[:len(VOLT_str)-1]
#        DWEL_str = '%0.2f,%0.2f,'%(step_size_sec,step_size_sec)
#        DWEL_str = DWEL_str[:len(DWEL_str)-1]


        zps_lock.acquire()
        s = SockConn(HOST, PORT)

#        scpi_ps='''
#INST:NSEL %d
#TRIG:SOUR BUS
#VOLT:MODE LIST
#LIST:VOLT %s
#LIST:DWEL %s
#LIST:COUNT %d
#LIST:STEP AUTO
#INIT:CONT OFF
#INIT
#
#*TRG
#'''%(ps_relee.NR,VOLT_str,DWEL_str,relee_steps)

        scpi_ps=''


        for i in range(0,len(active_ps_list)):
            ps = active_ps_list[i]
            #print ps.NR,ps_heightCurr[i]
            #print 'psNr',ps.NR
            scpi_ps+='''
INST:NSEL %d
TRIG:SOUR BUS
CURR:MODE WAVE
LIST:CURR 0
LIST:DWEL %0.2f
LIST:COUNT 1
LIST:STEP AUTO
INIT:CONT OFF
INIT

*TRG
        '''%(ps.NR,ps_heightCurr[i]/step_velocity)
        # init all ps
        s.command(scpi_ps)



        #print scpi_ps

        s.__del__()
        zps_lock.release()

        # sleep until all magnets goes down
        time.sleep(duration_sec)

        # sleep some relax time
        time.sleep(0.1)

        # invert sign of the relee
        self.write('zps:relee:volt',self.get_relee_invert())

    #
    #   Triangle step (from zero to some lesser value and sign change of the
    #   relee)
    #
    def demag_triangle(self, ps_heightCurr):
        global active_ps_list, relee_sign, relee_plus, relee_minus
        curr_max = 0

        for curr in ps_heightCurr:
            if curr_max<curr: curr_max=curr


        duration_sec = curr_max/step_velocity
        if duration_sec==0:
            #print 'duration_sec ',duration_sec
            return


        step_size_sec = 1.0
        relee_steps = duration_sec/step_size_sec
        relee_steps = int(round(relee_steps/2.0))

        # goto triangle peak
        zps_lock.acquire()
        s = SockConn(HOST, PORT)


        scpi_ps=''


        for i in range(0,len(active_ps_list)):
            ps = active_ps_list[i]
            #print ps.NR,ps_heightCurr[i]
            #print 'psNr',ps.NR
            scpi_ps+='''
INST:NSEL %d
TRIG:SOUR BUS
CURR:MODE WAVE
LIST:CURR %0.2f
LIST:DWEL %0.2f
LIST:COUNT 1
LIST:STEP AUTO
INIT:CONT OFF
INIT

*TRG
        '''%(ps.NR,ps_heightCurr[i],ps_heightCurr[i]/step_velocity)
        # init all ps
        s.command(scpi_ps)

        #print scpi_ps

        s.__del__()
        zps_lock.release()

        # sleep until all magnets goes down
        time.sleep(duration_sec)

        # sleep some relax time
        time.sleep(0.1)




        # goto Zero
        zps_lock.acquire()
        s = SockConn(HOST, PORT)


        scpi_ps=''


        for i in range(0,len(active_ps_list)):
            ps = active_ps_list[i]
            #print ps.NR,ps_heightCurr[i]
            #print 'psNr',ps.NR
            scpi_ps+='''
INST:NSEL %d
TRIG:SOUR BUS
CURR:MODE WAVE
LIST:CURR 0
LIST:DWEL %0.2f
LIST:COUNT 1
LIST:STEP AUTO
INIT:CONT OFF
INIT

*TRG
        '''%(ps.NR,ps_heightCurr[i]/step_velocity)
        # init all ps
        s.command(scpi_ps)

        #print scpi_ps

        s.__del__()
        zps_lock.release()

        # sleep until all magnets goes down
        time.sleep(duration_sec)

        # sleep some relax time
        time.sleep(0.1)

        # invert sign of the relee
        self.write('zps:relee:volt',self.get_relee_invert())





    #
    #  The write method is called everytime the user wants to change a variable
    #
    def write(self, reason, value):
        global relee_plus, relee_minus, relee_sign
        status = True
        ps = None

        ## TODO rm: test with relee current
        #if reason== 'zps:relee:curr':
        #    print 'setting the relee current'
        #    self.setLockedCurrThread(ps_relee,value)
        #    #zps_lock.acquire()
        #    #ps_relee.setWaveCurr(value)
        #    #zps_lock.release()
        #    return True

        #if reason=='demag': print 'demag signal',self.demag_active

        if reason=='demag' and self.demag_active==False:
            self.demag_active=True
            self.thred_demag_id = thread.start_new_thread(self.demag,())
            return True

        if reason=='demag:steps':
            self.setParam(reason,value)
            return True


        if 'relee' in reason : ps = ps_relee
        elif reason in record_to_ps: ps = record_to_ps[reason]
        if ps==None: return False

        # turn output on/off
        if 'output' in reason and ps in active_ps_list:
            if value==0 or value ==1:
                #print 'output',ps.NR
                self.setLockedOutput(ps,value,reason)
                return True
            else: print 'Err: %s ps.Nr:%d value should be 0 or 1'%(reason,self.NR)


        if ps == ps_relee and reason == 'zps:relee:volt':
            zps_lock.acquire()
            if float(value) == relee_plus:
                self.setParam('zps:relee:sign', 1)    # plus
                ps.setVolt(relee_plus)
                self.setParam(reason, relee_plus)
                relee_sign=1.0
                #print 'PLUS'
                status=True
            elif float(value) == relee_minus:
                self.setParam('zps:relee:sign', 0)    # minus
                ps.setVolt(relee_minus)
                self.setParam(reason, relee_minus)
                relee_sign=-1.0
                #print 'MINUS'
                status=True
            else:
                status=False
            # update all magnet signs
            for ps in ps_to_magnet:
                self.setParam('%s:volt'%ps_to_magnet[ps], ps.magn_sign*relee_sign*abs(self.getParam('%s:volt'%ps_to_magnet[ps])))
                self.setParam('%s:curr'%ps_to_magnet[ps], ps.magn_sign*relee_sign*abs(self.getParam('%s:curr'%ps_to_magnet[ps])))
            zps_lock.release()
            return status
        else:
            if 'volt' in reason:
                self.setParam(reason+':status',1)
                zps_lock.acquire()
                ps.setVolt(value)
                zps_lock.release()
                self.setParam(reason+':status',0)

            elif 'curr' in reason:
                # look at current limit
                if value > current_limit:
                    print '%.3f A is above current limit'%value
                    status=False
                    return status
                # if not busy start setting the current
                if self.getParam(reason+':status')==0:
                    self.setLockedCurrThread(ps,value,reason)
                else:
                    status=False
                    print '%s BUSY!!!'%reason
                return status

        if status:
            self.setParam(reason, value)

        # update magnet record
        if ps in ps_to_magnet:
            if 'volt' in reason: self.setParam('%s:volt'%ps_to_magnet[ps], ps.magn_sign*relee_sign*value)
            elif 'curr' in reason: self.setParam('%s:curr'%ps_to_magnet[ps], ps.magn_sign*relee_sign*value)
        return status

    #
    #   Setting the Current asyncronous
    #
    def setLockedCurrThread(self, ps, value,reason):
        def f(self,value,reason):
            self.setParam(reason+':status',1)
            zps_lock.acquire()
            ps.setWaveCurr(value)
            zps_lock.release()
            curr_now = self.getParam(reason)
            sleep_s = (abs(value-float(curr_now)))/step_velocity
            #print sleep_s
            time.sleep(sleep_s)
            #print 'pv %s done'%reason
            self.setParam(reason+':status',0)

        thread.start_new_thread(f,(self,value,reason,))


    #
    #   Setting the output of the power supplies  asyncronous
    #
    def setLockedOutput(self, ps, value,reason):
        def f(self,value,reason):
            zps_lock.acquire()
            ps.setOutput(value)
            zps_lock.release()
            self.setParam(reason,value)

        thread.start_new_thread(f,(self,value,reason,))

#    def setLockedVoltThread(self, ps, value, reason):
#        print '*** temporare setLockedVoltThread ***'
#        def f(self,value,reason):
#            self.setParam(reason+':status',1)
#            zps_lock.acquire()
#            ps.setWaveVolt(value)
#            zps_lock.release()
#            volt_now = self.getParam(reason)
#            sleep_s = (abs(value-float(volt_now)))/step_velocity
#            print sleep_s
#            time.sleep(sleep_s)
#            print 'pv %s done'%reason
#            self.setParam(reason+':status',0)
#            #self.setParam(reason,value)
#            #self.callbackPV(reason)
#
#
#        thread.start_new_thread(f,(self,value,reason,))


    #
    #   The polling method used by a thread started in the constructor
    #
    def continues_polling(self):
        global alive, ps_list, active_ps_list, relee_sign, relee_plus, relee_minus
        s = None
        while alive:
            try:
                s = SockConn(HOST, PORT)
                zps_lock.acquire()
                ps_relee.ask_for_error(s,psNR=ps_relee.NR)
                #while zps_conn == True: time.sleep(0.1)
                # poll relee
                volt = s.question('INST:NSEL %d\n:measure:voltage?'%ps_relee.NR)
                ps_relee.ask_for_error(s,psNR=ps_relee.NR)
                self.setParam('zps:relee:volt', volt)
                curr = s.question(':measure:current?')
                ps_relee.ask_for_error(s,psNR=ps_relee.NR)
                self.setParam('zps:relee:curr', curr)
                if (round(float(volt))==relee_plus): relee_sign=1.0
                elif (round(float(volt))==relee_minus): relee_sign=-1.0
                # poll other ps
                for ps in active_ps_list:
                    volt = s.question('INST:NSEL %d\n:measure:voltage?'%ps.NR)
                    ps_relee.ask_for_error(s,psNR=ps.NR)
                    #volt_all += '%s '%volt
                    self.setParam('%s:volt'%ps_to_prefix[ps], volt)
                    self.setParam('%s:volt'%ps_to_magnet[ps], ps.magn_sign*relee_sign*float(volt))

                    curr = s.question(':measure:current?')
                    ps_relee.ask_for_error(s,psNR=ps.NR)
                    #curr_all += '%s '%curr
                    self.setParam('%s:curr'%ps_to_prefix[ps], curr)
                    self.setParam('%s:curr'%ps_to_magnet[ps], ps.magn_sign*relee_sign*float(curr))

                    outp = s.question('OUTP:STAT?')
                    ps_relee.ask_for_error(s,psNR=ps.NR)
                    self.setParam('%s:output'%ps_to_prefix[ps],float(outp))

                # refresh magn_all_volt and magn_all_curr
                volt_all = ''
                curr_all = ''
                for ps in ps_list:
                    if ps == ps_relee: continue
                    if ps in active_ps_list:
                        volt_all += '%s '%(ps.magn_sign*relee_sign*float(self.getParam('%s:volt'%ps_to_prefix[ps])))
                        curr_all += '%s '%(ps.magn_sign*relee_sign*float(self.getParam('%s:curr'%ps_to_prefix[ps])))
                    else:
                        volt_all += 'None '
                        curr_all += 'None '
                #volt_all += '\n'
                #curr_all += '\n'
                self.setParam('magn_volt_all',volt_all)
                self.setParam('magn_curr_all',curr_all)

                ps_relee.ask_for_error(s,psNR=ps_relee.NR)
                s.__del__()
                zps_lock.release()
            except Exception as e:
                #if e.errno == errno.ECONNREFUSED:
                if e.errno == errno.ECONNRESET or e.errno == errno.ECONNREFUSED or e.errno == errno.ETIMEDOUT:
                    time_to_sleep=0.5
                    #print 'Connection to powersupplies refused, poling after %.1f sec.'%time_to_sleep
                    s.__del__()
                    time.sleep(time_to_sleep)
                    zps_lock.release()
                else:
                    alive=False
                    print traceback.format_exc()

            self.updatePVs()
            time.sleep(zps_poling_time)



#
# main function, create the server and driver object and listen to user inquire
# until Error or CTRL-C accrues
#
if __name__ == '__main__':


    server= SimpleServer()
    server.initAccessSecurityFile('security.as', P=prefix)
    server.createPV(prefix, pvdb)
    driver = myDriver()

    start_ts = time.time()

    # process CA transactions
    while alive:
        try:
            server.process(0.1)
            ts = time.time() - start_ts
            sys.stdout.write('%d s\r'%int(round(ts)))
            sys.stdout.flush()
        except KeyboardInterrupt:
            print "User interrupted. Bye"
            sys.exit()
        except Exception as e:
            print traceback.format_exc()
            sys.exit()

