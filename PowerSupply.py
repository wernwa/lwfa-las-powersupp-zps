import socket
import sys
import time
from SockConn import SockConn


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


    def getVolt(self):
        s = SockConn(self.HOST, self.PORT)
        # SCPI: MEASure:Voltage? (MV?)
        answer = s.question("INST:NSEL {}\n:measure:voltage?".format(self.NR))
        s.__del__()
        return answer

    def setVolt(self,volt):
        s = SockConn(self.HOST, self.PORT)
        s.command("INST:NSEL {}\n:VOLT {}".format(self.NR, volt))
        #s.__del__()

    def getCurr(self):
        s = SockConn(self.HOST, self.PORT)
        # SCPI: MEASure:CURRent? (MC?)
        answer = s.question("INST:NSEL {}\nmeasure:current?".format(self.NR))
        s.__del__()
        return answer

    def setCurr(self,curr):
        s = SockConn(self.HOST, self.PORT)
        s.command("INST:NSEL {}\n:CURR {}".format(self.NR, curr))
        s.__del__()

    def setWaveCurr(self,curr):
        s = SockConn(self.HOST, self.PORT)
        curr_now = s.question("INST:NSEL %d\nmeasure:current?"%self.NR)
        curr_wave=1
        scpi_ps='''
INST:NSEL %d
TRIG:SOUR BUS
VOLT:MODE WAVE
LIST:VOLT %0.3f
LIST:DWEL %0.3f
LIST:COUNT 1
LIST:STEP AUTO
INIT:CONT OFF
INIT
      '''%(self.NR,curr,abs(float(curr_now)-curr)*curr_wave)
        print scpi_ps
        s.command(scpi_ps)
        s.__del__()

        s = SockConn(self.HOST, self.PORT)
        time.sleep(0.1)
        s.command('*TRIG\n')
        s.__del__()


