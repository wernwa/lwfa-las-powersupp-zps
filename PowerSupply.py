#
#   PowerSupply class for talking to one poer supply
#
import socket
import sys
import time
from SockConn import SockConn




# TODO import setup.py for this variable
step_velocity=0.25 # A/sec
#step_velocity=2 # A/sec relee friendly speed

class PowerSupply:
    NR=None
    connection=None
    HOST=None
    PORT=None
    #
    #   Constructor
    #
    def __init__(self,host,port,nr,magn_sign=1):
        self.NR=nr
        #self.connection=con
        self.HOST=host
        self.PORT=port
        #self.connection.command("INST:NSEL {}".format(self.NR))
        self.magn_sign=magn_sign

    #
    #   wates for the ps be ready for new commands
    #   this method is obsolete, ask_for_errors does the same job
    #
    def wait_for_op_complete(self, sock):
        opc = 0
        while opc!='1':
            opc=sock.question('*OPC?\n')

    #
    #   get current voltage
    #
    def getVolt(self):
        s = SockConn(self.HOST, self.PORT)
        #s.command("INST:NSEL %d\n"%self.NR)
        #self.wait_for_op_complete(s)
        answer = s.question(":measure:voltage?\n")
        self.ask_for_error(s)
        s.__del__()
        return answer

    #
    #   set the current voltage
    #
    def setVolt(self,volt):
        s = SockConn(self.HOST, self.PORT)
        s.command("INST:NSEL %d\n"%self.NR)
        #self.wait_for_op_complete(s)
        s.command(":VOLT %.3f\n"%volt)
        self.ask_for_error(s)
        s.__del__()

    #
    #   set voltage as a linear ramp
    #
    def setWaveVolt(self,volt):
        s = SockConn(self.HOST, self.PORT)
        s.command("INST:NSEL %d\n"%self.NR)
        #self.wait_for_op_complete(s)
        volt_now = s.question("measure:voltage?\n")
        diff = float(volt_now)-volt
        if diff==0: return
        DWEL=abs(diff)/step_velocity
        scpi_ps='''
TRIG:SOUR BUS
VOLT:MODE WAVE
LIST:VOLT %0.3f
LIST:DWEL %0.2f
LIST:COUNT 1
LIST:STEP AUTO
INIT:CONT OFF
INIT

*TRG
      '''%(volt,DWEL)
        s.command(scpi_ps)
        self.ask_for_error(s)
        s.__del__()



    #
    #   get current current
    #
    def getCurr(self):
        s = SockConn(self.HOST, self.PORT)
        s.command("INST:NSEL %d\n"%self.NR)
        #self.wait_for_op_complete(s)
        answer = s.question("measure:current?\n")
        s.__del__()
        self.ask_for_error(s)
        return answer


    #
    #   set current
    #
    def setCurr(self,curr):
        s = SockConn(self.HOST, self.PORT)
        s.command("INST:NSEL %d\n"%self.NR)
        #self.wait_for_op_complete(s)
        s.command(":CURR %.3f"%curr)
        self.ask_for_error(s)
        s.__del__()


    #
    #   set current as a linear ramp
    #
    def setWaveCurr(self,curr):
        s = SockConn(self.HOST, self.PORT)
        s.command("INST:NSEL %d\n"%self.NR)
        #self.wait_for_op_complete(s)
        curr_now = s.question("measure:current?\n")
        #print 'curr_now: ',curr_now
        diff = float(curr_now)-curr
        if diff==0: return
        DWEL=abs(diff)/step_velocity
        scpi_ps='''
TRIG:SOUR BUS
CURR:MODE WAVE
LIST:CURR %0.3f
LIST:DWEL %0.2f
LIST:COUNT 1
LIST:STEP AUTO
INIT:CONT OFF
INIT

*TRG
      '''%(curr,DWEL)
        #print scpi_ps
        s.command(scpi_ps)
        self.ask_for_error(s)
        s.__del__()


    #
    #   set output of a ps
    #
    def setOutput(self,value):
        v = None
        if value==1: v='ON'
        elif value==0: v='OFF'

        s = SockConn(self.HOST, self.PORT)
        s.command("INST:NSEL %d\nOUTP:STAT %s\n"%(self.NR,v))
        time.sleep(1)
        self.ask_for_error(s)
        s.__del__()

    #
    #   get output of a ps
    #
    def getOutput(self):

        s = SockConn(self.HOST, self.PORT)
        answer = s.question("INST:NSEL %d\nOUTP:STAT?\n"%(self.NR))
        self.ask_for_error(s)
        s.__del__()

        return answer


    #
    #   after each query it is recommended to ask a ps for errors
    #   This call (intern in the ps) wates until previous requests are finished
    #
    def ask_for_error(self, sock, psNR=None):
        if psNR==None: psNR=self.NR
        err_msg = sock.question('INST:NSEL %d\nSYST:ERR?'%psNR)
        if err_msg[0] == '0': return

        print 'err_msg:',psNR,err_msg
