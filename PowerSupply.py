import socket
import sys
import time
from SockConn import SockConn


step_velocity=0.25 # A/sec
#step_velocity=2 # A/sec relee friendly speed

class PowerSupply:
    NR=None
    connection=None
    HOST=None
    PORT=None

    def __init__(self,host,port,nr,magn_sign=1):
        self.NR=nr
        #self.connection=con
        self.HOST=host
        self.PORT=port
        #self.connection.command("INST:NSEL {}".format(self.NR))
        self.magn_sign=magn_sign

    def wait_for_op_complete(self, sock):
        opc = 0
        while opc!='1':
            opc=sock.question('*OPC?\n')

    def getVolt(self):
        s = SockConn(self.HOST, self.PORT)
        #s.command("INST:NSEL %d\n"%self.NR)
        self.wait_for_op_complete(s)
        answer = s.question(":measure:voltage?\n")
        s.__del__()
        return answer

    def setVolt(self,volt):
        s = SockConn(self.HOST, self.PORT)
        s.command("INST:NSEL %d\n"%self.NR)
        #self.wait_for_op_complete(s)
        s.command(":VOLT %.3f\n"%volt)
        s.__del__()

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
        s.__del__()

    def getCurr(self):
        s = SockConn(self.HOST, self.PORT)
        s.command("INST:NSEL %d\n"%self.NR)
        #self.wait_for_op_complete(s)
        answer = s.question("measure:current?\n")
        s.__del__()
        return answer

    def setCurr(self,curr):
        s = SockConn(self.HOST, self.PORT)
        s.command("INST:NSEL %d\n"%self.NR)
        #self.wait_for_op_complete(s)
        s.command(":CURR %.3f"%curr)
        s.__del__()


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
        s.__del__()


