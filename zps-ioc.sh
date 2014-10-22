#!/bin/bash

export EPICS_CA_SERVER_PORT=20000
export EPICS_CA_REPEATER_PORT=20001

if [ "$1" == "start" ]
then
    ./zps-ioc.py &
elif [ "$1" == "stop" ]
then
    
    killall -9 ./zps-ioc.py
    killall -9 ./zps-ioc.sh

    fuser -k $EPICS_CA_SERVER_PORT/tcp
    fuser -k $EPICS_CA_REPEATER_PORT/udp
else
    echo "usage: ./zps_ioc.sh start|stop"
fi
