#!/bin/bash

export EPICS_CA_SERVER_PORT=20000
export EPICS_CA_REPEATER_PORT=20001

killall -9 ./zps-ioc.py
killall -9 ./zps-ioc.sh

fuser -k 20000/tcp
fuser -k 20001/udp
