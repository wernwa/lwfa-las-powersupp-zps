from PowerSupply import PowerSupply



zps_poling_time = 0.2        # in sesonds
HOST, PORT = "zps-netzteile", 8003

ps_relee = PowerSupply(HOST,PORT,31)
ps1 = PowerSupply(HOST,PORT,1,magn_sign=-1)
ps2 = PowerSupply(HOST,PORT,2)
ps3 = PowerSupply(HOST,PORT,3)
ps4 = PowerSupply(HOST,PORT,4)
ps5 = PowerSupply(HOST,PORT,5)
ps6 = PowerSupply(HOST,PORT,6)
ps7 = PowerSupply(HOST,PORT,7)
ps8 = PowerSupply(HOST,PORT,8)
ps9 = PowerSupply(HOST,PORT,9)
