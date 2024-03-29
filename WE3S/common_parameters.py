from WE3S.timestamp import *

DEBUG = True
MIN_CONTENTION_WINDOW = 16
MAX_CONTENTION_WINDOW = 1024

MAX_AGGREGATED_FRAMES = 8

#TSBTT = 100 #ms
TBTT = Timestamp(100 * 10**-3) #ms
BEACON_EXPIRATION_DATE = Timestamp(10 * 10**-6) # If this duration elapses without sending the beacon,
                                                # then the beacon frame is dropped

# Values for 2.4 GHz band
SIFS = Timestamp(10 * 10**-6)
DIFS = Timestamp(50 * 10**-6)
BACKOFF_SLOT = Timestamp(20 * 10**-6)
PHY_HEADER_DURATION = Timestamp(210 * 10**-6)
# PHY_HEADER_DURATION = Timestamp(53 * 10**-6)

#Values for 5 GHz band
# SIFS = Timestamp(16 * 10**-6)
# DIFS = Timestamp(34 * 10**-6)
# BACKOFF_SLOT = Timestamp(9 * 10**-6)
# PHY_HEADER_DURATION = Timestamp(20 * 10**-6)

MAC_HEADER_SIZE = 34 * 8
ACK_DURATION = SIFS + Timestamp(40 * 10**-6)


PER = 1/10

SWITCH_DOZE_TO_AWAKE_DURATION = Timestamp(2.6 * 10**-3)
SWITCH_AWAKE_TO_DOZE_DURATION = Timestamp(0.8 * 10**-3)
MIN_DOZE_DURATION = SWITCH_AWAKE_TO_DOZE_DURATION + SWITCH_DOZE_TO_AWAKE_DURATION



AP_BUFFER_CAPACITY = 20
STA_BUFFER_CAPACITY = 20

PROMPT_SIZE = 20*8
BEACON_SIZE = 142*8
ACK_SIZE = 14*8

IDLE_CONSUMPTION = 0.82 #Watt
CCA_CONSUMPTION = 0.82 #Watt
RX_CONSUMPTION = 0.94 #Watt
TX_CONSUMPTION = 1.28 #Watt
DOZE_CONSUMPTION = 0.1 #Watt
SWITCH_DOZE_TO_AWAKE_CONSUMPTION = 0.15 #Watt
SWITCH_AWAKE_TO_DOZE_CONSUMPTION = 0.24 #Watt
RECEPTION_CROSSFACTOR_CONSUMPTION = 0.75 * 10**-3 #Joule
EMISSION_CROSSFACTOR_CONSUMPTION = 0.75 * 10**-3 #Joule


SIMULATION_TIME_STEP = Timestamp(10)
