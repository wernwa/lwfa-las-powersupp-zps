import socket
import sys
import time
import SockConn

  
class PowerSupply:
  NR=None
  connection=None
  HOST=None
  PORT=None
  
  def __init__(self,host,port,nr):
    self.NR=nr
    #self.connection=con
    self.HOST=host
    self.PORT=port
    #self.connection.command("INST:NSEL {}".format(self.NR))
    
  def getCurr(self):
    s = SockConn.SockConn(self.HOST, self.PORT)
	# SCPI: MEASure:CURRent? (MC?)
    answer = s.question("INST:NSEL {}\nmeasure:current?".format(self.NR))
    return answer
    
  def setCurr(self,curr):
    s = SockConn.SockConn(self.HOST, self.PORT)
	# SCPI: MEASure:CURRent? (MC?)
    s.command("INST:NSEL {}\n:CURR {}".format(self.NR, curr))


  def getVolt(self):
    s = SockConn.SockConn(self.HOST, self.PORT)
	# SCPI: MEASure:Voltage? (MV?)
    answer = s.question("INST:NSEL {}\n:measure:voltage?".format(self.NR))
    return answer
    
  def setVolt(self,volt):
    s = SockConn.SockConn(self.HOST, self.PORT)
	# SCPI: MEASure:Voltage? (MV?)
    s.command("INST:NSEL {}\n:VOLT {}".format(self.NR, volt))
