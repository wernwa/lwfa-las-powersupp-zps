from PowerSupply import PowerSupply
from PowerSupply import step_velocity

#HOST, PORT = "zps-netzteile", 8003
HOST, PORT = "169.254.2.164", 8003
#HOST, PORT = "localhost", 8003


# current/time [A/sec]
step_velocity=0.25
# cycling steps during the demagnitization
demag_steps=8

# max current remanence (that can recreate the remanence Field)
current_remanence=0.1

# current limit in Ampere
current_limit=6.0

zps_poling_time = 0.5        # in sesonds

# assignment of power supplies to HOST, PORT, popersupp-NR and magnet sign (depends on how it is wired)
# usage: PoerSupply('<host>',<port>,<psNR>[,magn_sign=-1])
# The last parameter magn_sign is optional and is set to 1 by default
ps_relee = PowerSupply(HOST,PORT,31)
ps1 = PowerSupply(HOST,PORT,1,magn_sign=-1)
ps2 = PowerSupply(HOST,PORT,2,magn_sign=1)
ps3 = PowerSupply(HOST,PORT,3,magn_sign=-1)
ps4 = PowerSupply(HOST,PORT,4,magn_sign=1)
ps5 = PowerSupply(HOST,PORT,5,magn_sign=-1)
ps6 = PowerSupply(HOST,PORT,6,magn_sign=1)
ps7 = PowerSupply(HOST,PORT,7)
ps8 = PowerSupply(HOST,PORT,8,magn_sign=-1)
ps9 = PowerSupply(HOST,PORT,9,magn_sign=1)
